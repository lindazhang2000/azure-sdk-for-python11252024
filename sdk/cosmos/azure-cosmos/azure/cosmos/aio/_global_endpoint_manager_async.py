# The MIT License (MIT)
# Copyright (c) 2021 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Internal class for global endpoint manager implementation in the Azure Cosmos
database service.
"""

import asyncio # pylint: disable=do-not-import-asyncio
import logging
from typing import Tuple, Dict, Any

from azure.core.exceptions import AzureError
from azure.cosmos import DatabaseAccount

from .. import _constants as constants
from .. import exceptions
from .._location_cache import LocationCache
from .._utils import current_time_millis
from .._request_object import RequestObject

# pylint: disable=protected-access

logger = logging.getLogger("azure.cosmos.aio._GlobalEndpointManager")

class _GlobalEndpointManager(object): # pylint: disable=too-many-instance-attributes
    """
    This internal class implements the logic for endpoint management for
    geo-replicated database accounts.
    """

    def __init__(self, client):
        self.client = client
        self.PreferredLocations = client.connection_policy.PreferredLocations
        self.DefaultEndpoint = client.url_connection
        self.refresh_time_interval_in_ms = self.get_refresh_time_interval_in_ms_stub()
        self.location_cache = LocationCache(
            self.DefaultEndpoint,
            client.connection_policy
        )
        self.startup = True
        self.refresh_task = None
        self.refresh_needed = False
        self.refresh_lock = asyncio.Lock()
        self.last_refresh_time = 0
        self._database_account_cache = None

    def get_refresh_time_interval_in_ms_stub(self):
        return constants._Constants.DefaultEndpointsRefreshTime

    def get_write_endpoint(self):
        return self.location_cache.get_write_regional_routing_context()

    def get_read_endpoint(self):
        return self.location_cache.get_read_regional_routing_context()

    def _resolve_service_endpoint(
            self,
            request: RequestObject
    ) -> str:
        return self.location_cache.resolve_service_endpoint(request)

    def mark_endpoint_unavailable_for_read(self, endpoint, refresh_cache):
        self.location_cache.mark_endpoint_unavailable_for_read(endpoint, refresh_cache)

    def mark_endpoint_unavailable_for_write(self, endpoint, refresh_cache):
        self.location_cache.mark_endpoint_unavailable_for_write(endpoint, refresh_cache)

    def get_ordered_write_locations(self):
        return self.location_cache.get_ordered_write_locations()

    def get_ordered_read_locations(self):
        return self.location_cache.get_ordered_read_locations()

    def can_use_multiple_write_locations(self, request):
        return self.location_cache.can_use_multiple_write_locations_for_request(request)

    async def force_refresh_on_startup(self, database_account):
        self.refresh_needed = True
        await self.refresh_endpoint_list(database_account)
        self.startup = False

    def update_location_cache(self):
        self.location_cache.update_location_cache()

    async def refresh_endpoint_list(self, database_account, **kwargs):
        if self.refresh_task and self.refresh_task.done():
            try:
                await self.refresh_task
                self.refresh_task = None
            except (Exception, asyncio.CancelledError) as exception: #pylint: disable=broad-exception-caught
                logger.exception("Health check task failed: %s", exception) #pylint: disable=do-not-use-logging-exception
        if current_time_millis() - self.last_refresh_time > self.refresh_time_interval_in_ms:
            self.refresh_needed = True
        if self.refresh_needed:
            async with self.refresh_lock:
                # if refresh is not needed or refresh is already taking place, return
                if not self.refresh_needed:
                    return
                try:
                    await self._refresh_endpoint_list_private(database_account, **kwargs)
                except Exception as e:
                    raise e

    async def _refresh_endpoint_list_private(self, database_account=None, **kwargs):
        if database_account and not self.startup:
            self.location_cache.perform_on_database_account_read(database_account)
            self.refresh_needed = False
            self.last_refresh_time = current_time_millis()
        else:
            if self.location_cache.should_refresh_endpoints() or self.refresh_needed:
                self.refresh_needed = False
                self.last_refresh_time = current_time_millis()
                if not self.startup:
                    # this will perform getDatabaseAccount calls to check endpoint health
                    # in background
                    self.refresh_task = asyncio.create_task(self._endpoints_health_check(**kwargs))
                else:
                    # on startup do this in foreground
                    await self._endpoints_health_check(**kwargs)
                    self.startup = False

    async def _database_account_check(self, endpoint: str, **kwargs: Dict[str, Any]):
        try:
            await self.client._GetDatabaseAccountCheck(endpoint, **kwargs)
            self.location_cache.mark_endpoint_available(endpoint)
        except (exceptions.CosmosHttpResponseError, AzureError):
            self.mark_endpoint_unavailable_for_read(endpoint, False)
            self.mark_endpoint_unavailable_for_write(endpoint, False)

    async def _endpoints_health_check(self, **kwargs):
        """Gets the database account for each endpoint.

        Validating if the endpoint is healthy else marking it as unavailable.
        """
        # get the database account from the default endpoint first
        database_account, attempted_endpoint = await self._GetDatabaseAccount(**kwargs)
        self.location_cache.perform_on_database_account_read(database_account)
        # get all the endpoints to check
        endpoints = self.location_cache.endpoints_to_health_check()
        database_account_checks = []
        for endpoint in endpoints:
            if endpoint != attempted_endpoint:
                database_account_checks.append(self._database_account_check(endpoint, **kwargs))
        await asyncio.gather(*database_account_checks)

        self.location_cache.update_location_cache()

    async def _GetDatabaseAccount(self, **kwargs) -> Tuple[DatabaseAccount, str]:
        """Gets the database account.

        First tries by using the default endpoint, and if that doesn't work,
        use the endpoints for the preferred locations in the order they are
        specified, to get the database account.
        :returns: A `DatabaseAccount` instance representing the Cosmos DB Database Account
        and the endpoint that was used for the request.
        :rtype: tuple of (~azure.cosmos.DatabaseAccount, str)
        """
        try:
            database_account = await self._GetDatabaseAccountStub(self.DefaultEndpoint, **kwargs)
            self._database_account_cache = database_account
            self.location_cache.mark_endpoint_available(self.DefaultEndpoint)
            return database_account, self.DefaultEndpoint
        # If for any reason(non-globaldb related), we are not able to get the database
        # account from the above call to GetDatabaseAccount, we would try to get this
        # information from any of the preferred locations that the user might have
        # specified (by creating a locational endpoint) and keeping eating the exception
        # until we get the database account and return None at the end, if we are not able
        # to get that info from any endpoints
        except (exceptions.CosmosHttpResponseError, AzureError):
            self.mark_endpoint_unavailable_for_read(self.DefaultEndpoint, False)
            self.mark_endpoint_unavailable_for_write(self.DefaultEndpoint, False)
            for location_name in self.PreferredLocations:
                locational_endpoint = LocationCache.GetLocationalEndpoint(self.DefaultEndpoint, location_name)
                try:
                    database_account = await self._GetDatabaseAccountStub(locational_endpoint, **kwargs)
                    self._database_account_cache = database_account
                    self.location_cache.mark_endpoint_available(locational_endpoint)
                    return database_account, locational_endpoint
                except (exceptions.CosmosHttpResponseError, AzureError):
                    self.mark_endpoint_unavailable_for_read(locational_endpoint, False)
                    self.mark_endpoint_unavailable_for_write(locational_endpoint, False)
            raise

    async def _GetDatabaseAccountStub(self, endpoint, **kwargs):
        """Stub for getting database account from the client.
        This can be used for mocking purposes as well.

        :param str endpoint: the endpoint being used to get the database account
        :returns: A `DatabaseAccount` instance representing the Cosmos DB Database Account.
        :rtype: ~azure.cosmos.DatabaseAccount
        """
        return await self.client.GetDatabaseAccount(endpoint, **kwargs)

    async def close(self):
        # cleanup any running tasks
        if self.refresh_task:
            self.refresh_task.cancel()
            try:
                await self.refresh_task
            except (Exception, asyncio.CancelledError) : #pylint: disable=broad-exception-caught
                pass
