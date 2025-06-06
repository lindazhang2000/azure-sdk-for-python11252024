# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import asyncio
import logging
from typing import Callable, Dict, List, Optional, Tuple, Union

from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation.simulator._constants import SupportedLanguages
from azure.ai.evaluation.simulator._helpers._language_suffix_mapping import SUPPORTED_LANGUAGES_MAPPING
from ..._http_utils import AsyncHttpPipeline
from . import ConversationBot, ConversationTurn
from azure.ai.evaluation._common.onedp._client import AIProjectClient


def is_closing_message(response: Union[Dict, str], recursion_depth: int = 0) -> bool:
    """Determine if a response indicates an end to the conversation.

    :param response: The response to check.
    :type response: Union[Dict, str]
    :param recursion_depth: The current recursion depth. Defaults to 0.
    :type recursion_depth: int
    :return: True if the response indicates an end to the conversation, False otherwise.
    :rtype: bool
    """
    if recursion_depth > 10:
        msg = "Exceeded max call depth in is_closing_message"
        raise EvaluationException(
            message=msg,
            internal_message=msg,
            error_category=ErrorCategory.INVALID_VALUE,
            error_target=ErrorTarget.CONVERSATION,
            error_blame=ErrorBlame.USER_ERROR,
        )

    # recursively go through each inner dictionary in the JSON dict
    # and check if any value entry contains a closing message
    if isinstance(response, dict):
        for value in response.values():
            if is_closing_message(value, recursion_depth=recursion_depth + 1):
                return True
    elif isinstance(response, str):
        return is_closing_message_helper(response)

    return False


def is_closing_message_helper(response: str) -> bool:
    """Determine if a response indicates an end to the conversation.

    :param response: The response to check.
    :type response: str
    :return: True if the response indicates an end to the conversation, False otherwise.
    :rtype: bool
    """
    message = response.lower()
    if "?" in message.lower():
        return False
    punctuation = [".", ",", "!", ";", ":"]
    for p in punctuation:
        message = message.replace(p, "")
    if (
        "bye" not in message.lower().split()
        and "goodbye" not in message.lower().split()
        # and "thanks" not in message.lower()
        # and "thank" not in message.lower()
    ):
        return False
    return True


async def simulate_conversation(
    *,
    bots: List[ConversationBot],
    session: Union[AsyncHttpPipeline, AIProjectClient],
    language: SupportedLanguages,
    stopping_criteria: Callable[[str], bool] = is_closing_message,
    turn_limit: int = 10,
    history_limit: int = 5,
    api_call_delay_sec: float = 0,
    logger: logging.Logger = logging.getLogger(__name__),
) -> Tuple[Optional[str], List[ConversationTurn]]:
    """
    Simulate a conversation between the given bots.

    :keyword bots: List of ConversationBot instances participating in the conversation.
    :paramtype bots: List[ConversationBot]
    :keyword session: The session to use for making API calls.
    :paramtype session: AsyncHttpPipeline
    :keyword stopping_criteria: A callable that determines when the conversation should stop.
    :paramtype stopping_criteria: Callable[[str], bool]
    :keyword turn_limit: The maximum number of turns in the conversation. Defaults to 10.
    :paramtype turn_limit: int
    :keyword history_limit: The maximum number of turns to keep in the conversation history. Defaults to 5.
    :paramtype history_limit: int
    :keyword api_call_delay_sec: Delay between API calls in seconds. Defaults to 0.
    :paramtype api_call_delay_sec: float
    :keyword logger: The logger to use for logging. Defaults to the logger named after the current module.
    :paramtype logger: logging.Logger
    :return: Simulation a conversation between the given bots.
    :rtype: Tuple[Optional[str], List[ConversationTurn]]
    """

    session_state = {}
    # Read the first prompt.
    (first_response, request, _, full_response) = await bots[0].generate_response(
        session=session,
        conversation_history=[],
        max_history=history_limit,
        turn_number=0,
    )
    if "id" in first_response:
        conversation_id: Optional[str] = first_response["id"]
    else:
        conversation_id = None
    first_prompt = first_response["samples"][0]
    if language != SupportedLanguages.English:
        if not isinstance(language, SupportedLanguages) or language not in SupportedLanguages:
            raise Exception(  # pylint: disable=broad-exception-raised
                f"Language option '{language}' isn't supported. Select a supported language option from "
                f"azure.ai.evaluation.simulator.SupportedLanguages: {[f'{e}' for e in SupportedLanguages]}"
            )
        first_prompt += f" {SUPPORTED_LANGUAGES_MAPPING[language]}"
    # Add all generated turns into array to pass for each bot while generating
    # new responses. We add generated response and the person generating it.
    # in the case of the first turn, it is supposed to be the user search query
    conversation_history = [
        ConversationTurn(
            role=bots[0].role,
            name=bots[0].name,
            message=first_prompt,
            full_response=full_response,
            request=request,
        )
    ]

    # initialize the turn counter
    current_turn = 1

    # Keep iterating and alternate between bots until a stopping word is
    # generated or maximum number of turns is reached.
    while (not stopping_criteria(conversation_history[-1].message)) and (current_turn < turn_limit):
        try:
            current_character_idx = current_turn % len(bots)
            current_bot = bots[current_character_idx]
            # invoke Bot to generate response given the input request
            # pass only the last generated turn without passing the bot name.
            response, request, _, full_response = await current_bot.generate_response(
                session=session,
                conversation_history=conversation_history,
                max_history=history_limit,
                turn_number=current_turn,
                session_state=session_state,
            )
            if "session_state" in full_response and full_response["session_state"] is not None:
                session_state.update(full_response["session_state"])

            # check if conversation id is null, which means conversation starter was used. use id from next turn
            if conversation_id is None and "id" in response:
                conversation_id = response["id"]
            # add the generated response to the list of generated responses
            conversation_history.append(
                ConversationTurn(
                    role=current_bot.role,
                    name=current_bot.name,
                    message=response["samples"][0],
                    full_response=full_response,
                    request=request,
                )
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.warning("Error: %s", str(e))

        # Increment outside the try block so we don't get stuck if
        # an exception is thrown
        current_turn += 1

        # Sleep between consecutive requests to avoid rate limit
        await asyncio.sleep(api_call_delay_sec)

    return conversation_id, conversation_history
