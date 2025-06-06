# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) Python Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------

from azure.identity import DefaultAzureCredential

from azure.mgmt.standbypool import StandbyPoolMgmtClient

"""
# PREREQUISITES
    pip install azure-identity
    pip install azure-mgmt-standbypool
# USAGE
    python standby_container_group_pool_runtime_views_get.py

    Before run the sample, please set the values of the client ID, tenant ID and client secret
    of the AAD application as environment variables: AZURE_CLIENT_ID, AZURE_TENANT_ID,
    AZURE_CLIENT_SECRET. For more info about how to get the value, please see:
    https://docs.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal
"""


def main():
    client = StandbyPoolMgmtClient(
        credential=DefaultAzureCredential(),
        subscription_id="SUBSCRIPTION_ID",
    )

    response = client.standby_container_group_pool_runtime_views.get(
        resource_group_name="rgstandbypool",
        standby_container_group_pool_name="pool",
        runtime_view="latest",
    )
    print(response)


# x-ms-original-file: 2025-03-01/StandbyContainerGroupPoolRuntimeViews_Get.json
if __name__ == "__main__":
    main()
