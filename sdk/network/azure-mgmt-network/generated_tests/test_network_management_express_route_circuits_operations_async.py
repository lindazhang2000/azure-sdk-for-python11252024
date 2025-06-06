# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------
import pytest
from azure.mgmt.network.aio import NetworkManagementClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer
from devtools_testutils.aio import recorded_by_proxy_async

AZURE_LOCATION = "eastus"


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestNetworkManagementExpressRouteCircuitsOperationsAsync(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(NetworkManagementClient, is_async=True)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_express_route_circuits_begin_delete(self, resource_group):
        response = await (
            await self.client.express_route_circuits.begin_delete(
                resource_group_name=resource_group.name,
                circuit_name="str",
                api_version="2024-07-01",
            )
        ).result()  # call '.result()' to poll until service return final result

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_express_route_circuits_get(self, resource_group):
        response = await self.client.express_route_circuits.get(
            resource_group_name=resource_group.name,
            circuit_name="str",
            api_version="2024-07-01",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_express_route_circuits_begin_create_or_update(self, resource_group):
        response = await (
            await self.client.express_route_circuits.begin_create_or_update(
                resource_group_name=resource_group.name,
                circuit_name="str",
                parameters={
                    "allowClassicOperations": bool,
                    "authorizationKey": "str",
                    "authorizationStatus": "str",
                    "authorizations": [
                        {
                            "authorizationKey": "str",
                            "authorizationUseStatus": "str",
                            "connectionResourceUri": "str",
                            "etag": "str",
                            "id": "str",
                            "name": "str",
                            "provisioningState": "str",
                            "type": "str",
                        }
                    ],
                    "bandwidthInGbps": 0.0,
                    "circuitProvisioningState": "str",
                    "enableDirectPortRateLimit": bool,
                    "etag": "str",
                    "expressRoutePort": {"id": "str"},
                    "gatewayManagerEtag": "str",
                    "globalReachEnabled": bool,
                    "id": "str",
                    "location": "str",
                    "name": "str",
                    "peerings": [
                        {
                            "azureASN": 0,
                            "connections": [
                                {
                                    "addressPrefix": "str",
                                    "authorizationKey": "str",
                                    "circuitConnectionStatus": "str",
                                    "etag": "str",
                                    "expressRouteCircuitPeering": {"id": "str"},
                                    "id": "str",
                                    "ipv6CircuitConnectionConfig": {
                                        "addressPrefix": "str",
                                        "circuitConnectionStatus": "str",
                                    },
                                    "name": "str",
                                    "peerExpressRouteCircuitPeering": {"id": "str"},
                                    "provisioningState": "str",
                                    "type": "str",
                                }
                            ],
                            "etag": "str",
                            "expressRouteConnection": {"id": "str"},
                            "gatewayManagerEtag": "str",
                            "id": "str",
                            "ipv6PeeringConfig": {
                                "microsoftPeeringConfig": {
                                    "advertisedCommunities": ["str"],
                                    "advertisedPublicPrefixInfo": [
                                        {
                                            "prefix": "str",
                                            "signature": "str",
                                            "validationId": "str",
                                            "validationState": "str",
                                        }
                                    ],
                                    "advertisedPublicPrefixes": ["str"],
                                    "advertisedPublicPrefixesState": "str",
                                    "customerASN": 0,
                                    "legacyMode": 0,
                                    "routingRegistryName": "str",
                                },
                                "primaryPeerAddressPrefix": "str",
                                "routeFilter": {"id": "str"},
                                "secondaryPeerAddressPrefix": "str",
                                "state": "str",
                            },
                            "lastModifiedBy": "str",
                            "microsoftPeeringConfig": {
                                "advertisedCommunities": ["str"],
                                "advertisedPublicPrefixInfo": [
                                    {
                                        "prefix": "str",
                                        "signature": "str",
                                        "validationId": "str",
                                        "validationState": "str",
                                    }
                                ],
                                "advertisedPublicPrefixes": ["str"],
                                "advertisedPublicPrefixesState": "str",
                                "customerASN": 0,
                                "legacyMode": 0,
                                "routingRegistryName": "str",
                            },
                            "name": "str",
                            "peerASN": 0,
                            "peeredConnections": [
                                {
                                    "addressPrefix": "str",
                                    "authResourceGuid": "str",
                                    "circuitConnectionStatus": "str",
                                    "connectionName": "str",
                                    "etag": "str",
                                    "expressRouteCircuitPeering": {"id": "str"},
                                    "id": "str",
                                    "name": "str",
                                    "peerExpressRouteCircuitPeering": {"id": "str"},
                                    "provisioningState": "str",
                                    "type": "str",
                                }
                            ],
                            "peeringType": "str",
                            "primaryAzurePort": "str",
                            "primaryPeerAddressPrefix": "str",
                            "provisioningState": "str",
                            "routeFilter": {"id": "str"},
                            "secondaryAzurePort": "str",
                            "secondaryPeerAddressPrefix": "str",
                            "sharedKey": "str",
                            "state": "str",
                            "stats": {
                                "primarybytesIn": 0,
                                "primarybytesOut": 0,
                                "secondarybytesIn": 0,
                                "secondarybytesOut": 0,
                            },
                            "type": "str",
                            "vlanId": 0,
                        }
                    ],
                    "provisioningState": "str",
                    "serviceKey": "str",
                    "serviceProviderNotes": "str",
                    "serviceProviderProperties": {
                        "bandwidthInMbps": 0,
                        "peeringLocation": "str",
                        "serviceProviderName": "str",
                    },
                    "serviceProviderProvisioningState": "str",
                    "sku": {"family": "str", "name": "str", "tier": "str"},
                    "stag": 0,
                    "tags": {"str": "str"},
                    "type": "str",
                },
                api_version="2024-07-01",
            )
        ).result()  # call '.result()' to poll until service return final result

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_express_route_circuits_update_tags(self, resource_group):
        response = await self.client.express_route_circuits.update_tags(
            resource_group_name=resource_group.name,
            circuit_name="str",
            parameters={"tags": {"str": "str"}},
            api_version="2024-07-01",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_express_route_circuits_begin_list_arp_table(self, resource_group):
        response = await (
            await self.client.express_route_circuits.begin_list_arp_table(
                resource_group_name=resource_group.name,
                circuit_name="str",
                peering_name="str",
                device_path="str",
                api_version="2024-07-01",
            )
        ).result()  # call '.result()' to poll until service return final result

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_express_route_circuits_begin_list_routes_table(self, resource_group):
        response = await (
            await self.client.express_route_circuits.begin_list_routes_table(
                resource_group_name=resource_group.name,
                circuit_name="str",
                peering_name="str",
                device_path="str",
                api_version="2024-07-01",
            )
        ).result()  # call '.result()' to poll until service return final result

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_express_route_circuits_begin_list_routes_table_summary(self, resource_group):
        response = await (
            await self.client.express_route_circuits.begin_list_routes_table_summary(
                resource_group_name=resource_group.name,
                circuit_name="str",
                peering_name="str",
                device_path="str",
                api_version="2024-07-01",
            )
        ).result()  # call '.result()' to poll until service return final result

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_express_route_circuits_get_stats(self, resource_group):
        response = await self.client.express_route_circuits.get_stats(
            resource_group_name=resource_group.name,
            circuit_name="str",
            api_version="2024-07-01",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_express_route_circuits_get_peering_stats(self, resource_group):
        response = await self.client.express_route_circuits.get_peering_stats(
            resource_group_name=resource_group.name,
            circuit_name="str",
            peering_name="str",
            api_version="2024-07-01",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_express_route_circuits_list(self, resource_group):
        response = self.client.express_route_circuits.list(
            resource_group_name=resource_group.name,
            api_version="2024-07-01",
        )
        result = [r async for r in response]
        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_express_route_circuits_list_all(self, resource_group):
        response = self.client.express_route_circuits.list_all(
            api_version="2024-07-01",
        )
        result = [r async for r in response]
        # please add some check logic here by yourself
        # ...
