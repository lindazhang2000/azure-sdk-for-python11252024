# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------

from typing import (
    TypeVar,
    Generic,
    Dict,
    Any,
    Tuple,
    List,
    Optional,
    overload,
    TYPE_CHECKING,
    Union,
)

HTTPResponseType = TypeVar("HTTPResponseType", covariant=True)  # pylint: disable=typevar-name-incorrect-variance
HTTPRequestType = TypeVar("HTTPRequestType", covariant=True)  # pylint: disable=typevar-name-incorrect-variance

if TYPE_CHECKING:
    from .transport import HttpTransport, AsyncHttpTransport

    TransportType = Union[HttpTransport[Any, Any], AsyncHttpTransport[Any, Any]]


class PipelineContext(Dict[str, Any]):
    """A context object carried by the pipeline request and response containers.

    This is transport specific and can contain data persisted between
    pipeline requests (for example reusing an open connection pool or "session"),
    as well as used by the SDK developer to carry arbitrary data through
    the pipeline.

    :param transport: The HTTP transport type.
    :type transport: ~azure.core.pipeline.transport.HttpTransport or ~azure.core.pipeline.transport.AsyncHttpTransport
    :param any kwargs: Developer-defined keyword arguments.
    """

    _PICKLE_CONTEXT = {"deserialized_data"}

    def __init__(self, transport: Optional["TransportType"], **kwargs: Any) -> None:
        self.transport: Optional["TransportType"] = transport
        self.options = kwargs
        self._protected = ["transport", "options"]

    def __getstate__(self) -> Dict[str, Any]:
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        del state["transport"]
        return state

    def __reduce__(self) -> Tuple[Any, ...]:
        reduced = super(PipelineContext, self).__reduce__()
        saved_context = {}
        for key, value in self.items():
            if key in self._PICKLE_CONTEXT:
                saved_context[key] = value
        # 1 is for from __reduce__ spec of pickle (generic args for recreation)
        # 2 is how dict is implementing __reduce__ (dict specific)
        # tuple are read-only, we use a list in the meantime
        reduced_as_list: List[Any] = list(reduced)
        dict_reduced_result = list(reduced_as_list[1])
        dict_reduced_result[2] = saved_context
        reduced_as_list[1] = tuple(dict_reduced_result)
        return tuple(reduced_as_list)

    def __setstate__(self, state: Dict[str, Any]) -> None:
        self.__dict__.update(state)
        # Re-create the unpickable entries
        self.transport = None

    def __setitem__(self, key: str, item: Any) -> None:
        # If reloaded from pickle, _protected might not be here until restored by pickle
        # this explains the hasattr test
        if hasattr(self, "_protected") and key in self._protected:
            raise ValueError("Context value {} cannot be overwritten.".format(key))
        return super(PipelineContext, self).__setitem__(key, item)

    def __delitem__(self, key: str) -> None:
        if key in self._protected:
            raise ValueError("Context value {} cannot be deleted.".format(key))
        return super(PipelineContext, self).__delitem__(key)

    def clear(  # pylint: disable=docstring-missing-return, docstring-missing-rtype
        self,
    ) -> None:
        """Clears the context objects.

        :raises TypeError: If context objects cannot be cleared
        """
        raise TypeError("Context objects cannot be cleared.")

    def update(  # pylint: disable=docstring-missing-return, docstring-missing-rtype, docstring-missing-param
        self, *args: Any, **kwargs: Any
    ) -> None:
        """Updates the context objects.

        :raises TypeError: If context objects cannot be updated
        """
        raise TypeError("Context objects cannot be updated.")

    @overload
    def pop(self, __key: str) -> Any: ...

    @overload
    def pop(self, __key: str, __default: Optional[Any]) -> Any: ...

    def pop(self, *args: Any) -> Any:
        """Removes specified key and returns the value.

        :param args: The key to remove.
        :type args: str
        :return: The value for this key.
        :rtype: any
        :raises ValueError: If the key is in the protected list.
        """
        if args and args[0] in self._protected:
            raise ValueError("Context value {} cannot be popped.".format(args[0]))
        return super(PipelineContext, self).pop(*args)


class PipelineRequest(Generic[HTTPRequestType]):
    """A pipeline request object.

    Container for moving the HttpRequest through the pipeline.
    Universal for all transports, both synchronous and asynchronous.

    :param http_request: The request object.
    :type http_request: ~azure.core.pipeline.transport.HttpRequest
    :param context: Contains the context - data persisted between pipeline requests.
    :type context: ~azure.core.pipeline.PipelineContext
    """

    def __init__(self, http_request: HTTPRequestType, context: PipelineContext) -> None:
        self.http_request = http_request
        self.context = context


class PipelineResponse(Generic[HTTPRequestType, HTTPResponseType]):
    """A pipeline response object.

    The PipelineResponse interface exposes an HTTP response object as it returns through the pipeline of Policy objects.
    This ensures that Policy objects have access to the HTTP response.

    This also has a "context" object where policy can put additional fields.
    Policy SHOULD update the "context" with additional post-processed field if they create them.
    However, nothing prevents a policy to actually sub-class this class a return it instead of the initial instance.

    :param http_request: The request object.
    :type http_request: ~azure.core.pipeline.transport.HttpRequest
    :param http_response: The response object.
    :type http_response: ~azure.core.pipeline.transport.HttpResponse
    :param context: Contains the context - data persisted between pipeline requests.
    :type context: ~azure.core.pipeline.PipelineContext
    """

    def __init__(
        self,
        http_request: HTTPRequestType,
        http_response: HTTPResponseType,
        context: PipelineContext,
    ) -> None:
        self.http_request = http_request
        self.http_response = http_response
        self.context = context


from ._base import Pipeline  # pylint: disable=wrong-import-position
from ._base_async import AsyncPipeline  # pylint: disable=wrong-import-position

__all__ = [
    "Pipeline",
    "PipelineRequest",
    "PipelineResponse",
    "PipelineContext",
    "AsyncPipeline",
]
