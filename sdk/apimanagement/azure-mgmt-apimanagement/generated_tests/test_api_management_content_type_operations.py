# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------
import pytest
from azure.mgmt.apimanagement import ApiManagementClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = "eastus"


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestApiManagementContentTypeOperations(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(ApiManagementClient)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_content_type_list_by_service(self, resource_group):
        response = self.client.content_type.list_by_service(
            resource_group_name=resource_group.name,
            service_name="str",
            api_version="2024-05-01",
        )
        result = [r for r in response]
        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_content_type_get(self, resource_group):
        response = self.client.content_type.get(
            resource_group_name=resource_group.name,
            service_name="str",
            content_type_id="str",
            api_version="2024-05-01",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_content_type_create_or_update(self, resource_group):
        response = self.client.content_type.create_or_update(
            resource_group_name=resource_group.name,
            service_name="str",
            content_type_id="str",
            parameters={
                "description": "str",
                "id": "str",
                "name": "str",
                "schema": {},
                "type": "str",
                "version": "str",
            },
            api_version="2024-05-01",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_content_type_delete(self, resource_group):
        response = self.client.content_type.delete(
            resource_group_name=resource_group.name,
            service_name="str",
            content_type_id="str",
            if_match="str",
            api_version="2024-05-01",
        )

        # please add some check logic here by yourself
        # ...
