# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import time
import unittest

from azure.cli.command_modules.containerapp._utils import format_location
from unittest import mock
from azure.cli.core.azclierror import ValidationError, CLIInternalError

from azure.cli.testsdk.scenario_tests import AllowLargeResponse, live_only
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck, JMESPathCheckNotExists, JMESPathCheckExists, live_only, StorageAccountPreparer, LogAnalyticsWorkspacePreparer)
from azure.mgmt.core.tools import parse_resource_id

from azext_containerapp.tests.latest.common import (write_test_file, clean_up_test_file)
from .common import TEST_LOCATION, STAGE_LOCATION
from .custom_preparers import SubnetPreparer
from .utils import create_containerapp_env, prepare_containerapp_env_for_app_e2e_tests

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ContainerappFunctionTests(ScenarioTest):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, random_config_dir=True, **kwargs)
    

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northcentralus")
    def test_containerapp_function_list_show_basic(self, resource_group):
        """Test basic function list functionality with various scenarios"""
        location = "northcentralusstage"
        self.cmd('configure --defaults location={}'.format(location))

        ca_name = self.create_random_name(prefix='containerapp', length=24)
        function_name = "HttpExample"
        function_image = "mcr.microsoft.com/azure-functions/dotnet8-quickstart-demo:1.0"

        env = prepare_containerapp_env_for_app_e2e_tests(self, location=location)
        
        # Create a function app
        self.cmd(f'containerapp create -g {resource_group} -n {ca_name} --image {function_image} --ingress external --target-port 80 --environment {env} --kind functionapp', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("kind", "functionapp")
        ])
        time.sleep(30)
        rev_status = self.cmd(f'az containerapp revision list -g {resource_group} -n {ca_name}').get_output_in_json()
        assert any(r["properties"]["active"] and r["properties"]["healthState"] == "Healthy" for r in rev_status)
        
        time.sleep(30)
        result = self.cmd(f'containerapp function list -g {resource_group} -n {ca_name}').get_output_in_json()

        # Test successful function show
        function_details = self.cmd(f'containerapp function show -g {resource_group} -n {ca_name} --function-name {function_name}').get_output_in_json()
        
        # Verify function details structure
        self.assertIsInstance(function_details, dict, "Function show should return a dictionary")
        self.assertIn('name', function_details["properties"], "Function details should contain name")
        self.assertEqual(function_details["properties"]['name'], function_name, "Function name should match requested function")
    

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northcentralus")
    def test_containerapp_function_list_show_error_scenarios(self, resource_group):
        """Test error scenarios for function list command"""
        location = "northcentralusstage"
        self.cmd('configure --defaults location={}'.format(location))

        ca_name = self.create_random_name(prefix='containerapp', length=24)
        ca_func_name = self.create_random_name(prefix='functionapp', length=24)
        containerapp_image = "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"
        function_image = "mcr.microsoft.com/azure-functions/dotnet8-quickstart-demo:1.0"
        function_name = "HttpExample"

        env = prepare_containerapp_env_for_app_e2e_tests(self, location=location)
        
        # Create a regular container app (not a function app)
        self.cmd(f'containerapp create -g {resource_group} -n {ca_name} --image {containerapp_image} --ingress external --target-port 80 --environment {env}', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded")
        ])
        time.sleep(40)
        self.cmd(f'containerapp create -g {resource_group} -n {ca_func_name} --image {function_image} --ingress external --target-port 80 --environment {env} --kind functionapp', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("kind", "functionapp")
        ])
        time.sleep(60)

        rev_status = self.cmd(f'az containerapp revision list -g {resource_group} -n {ca_name}').get_output_in_json()
        assert any(r["properties"]["active"] and r["properties"]["healthState"] == "Healthy" for r in rev_status)

        rev_status = self.cmd(f'az containerapp revision list -g {resource_group} -n {ca_func_name}').get_output_in_json()
        assert any(r["properties"]["active"] and r["properties"]["healthState"] == "Healthy" for r in rev_status)

        # Test: List functions from a regular app should fail
        with self.assertRaisesRegex(Exception, ".*"):
            self.cmd(f'containerapp function list -g {resource_group} -n {ca_name}')

        # Test: List functions from non-existent app should fail
        with self.assertRaisesRegex(Exception, ".*"):
            self.cmd(f'containerapp function list -g {resource_group} -n nonexistent-app')

        # Test: List functions from non-existent resource group should fail
        with self.assertRaisesRegex(Exception, ".*"):
            self.cmd(f'containerapp function list -g nonexistent-resource-group -n {ca_func_name}')

        # Test: List functions with non-existent revision should fail
        with self.assertRaisesRegex(Exception, ".*"):
            self.cmd(f'containerapp function list -g {resource_group} -n {ca_func_name} --revision nonexistent-revision')

        #Test: Show functions with a regular app should fail 
        with self.assertRaisesRegex(Exception, ".*"):
            self.cmd(f'containerapp function show -g {resource_group} -n {ca_name} --function-name {function_name}')

        # Test: Show functions with non-existent resource group
        with self.assertRaisesRegex(Exception, ".*"):
            self.cmd(f'containerapp function show -g nonexistent-resource-group -n {ca_func_name} --function-name {function_name}')

        # Test: Show functions with non-existent container app
        with self.assertRaisesRegex(Exception, ".*"):
            self.cmd(f'containerapp function show -g {resource_group} -n nonexistent-app --function-name {function_name}')

         # Test: Show functions with non-existent revision should fail
        with self.assertRaisesRegex(Exception, ".*"):
            self.cmd(f'containerapp function show -g {resource_group} -n {ca_func_name} --revision nonexistent-revision --function-name {function_name}')


    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northcentralus")
    def test_containerapp_function_list_show_multirevision_scenarios(self, resource_group):
        """Test multiple revisions scenarios for function list command"""
        location = "northcentralusstage"
        self.cmd('configure --defaults location={}'.format(location))
        env = prepare_containerapp_env_for_app_e2e_tests(self, location=location)

        # Create a function app for revision testing
        ca_func_name = self.create_random_name(prefix='funcapp', length=24)
        function_image_latest = "mcr.microsoft.com/azure-functions/dotnet8-quickstart-demo:latest"
        function_image_v1 = "mcr.microsoft.com/azure-functions/dotnet8-quickstart-demo:1.0"

        # Create the initial function app with function_image_latest
        self.cmd(f'containerapp create -g {resource_group} -n {ca_func_name} '
                 f'--image {function_image_latest} --ingress external --target-port 80 '
                 f'--environment {env} --kind functionapp --revisions-mode multiple', checks=[
            JMESPathCheck("properties.provisioningState", "Succeeded"),
            JMESPathCheck("kind", "functionapp")
        ])
        
        # Wait for the first revision to be created
        time.sleep(30)  # Sleep to allow revision creation (may need more time based on provisioning time)

        # self.cmd(f'containerapp update -g {resource_group} -n {ca_func_name} --revision-mode multiple')
        # self.cmd(f'containerapp revision set-mode -g {resource_group} -n {ca_func_name} --mode multiple')
        # time.sleep(30)
        # time.sleep(10)
        
        # Update the function app to use the second image (function_image_v1)
        self.cmd(f'containerapp update -g {resource_group} -n {ca_func_name} --image {function_image_v1}')
        
        # Wait for the second revision to be created
        time.sleep(30)

        # List the revisions to retrieve revision names
        revision_list = self.cmd(f'containerapp revision list -g {resource_group} -n {ca_func_name}').get_output_in_json()
        print("Revisions found:", revision_list)
        self.assertGreater(len(revision_list), 1, "There should be more than one revision.")

        # Extract revision names from the list
        revision_name_latest = revision_list[0]['name']
        revision_name_v1 = revision_list[1]['name']

        # Split traffic between the two revisions
        self.cmd(f'containerapp ingress traffic set -g {resource_group} -n {ca_func_name} '
            f'--revision-weight {revision_name_latest}=50 '
            f'--revision-weight {revision_name_v1}=50')

        # Test 1: Do not provide revision name - should fail (multiple revision mode requires revision name)
        with self.assertRaisesRegex(Exception, ".*"):
            self.cmd(f'containerapp function list -g {resource_group} -n {ca_func_name}')

        # Test 2: Provide wrong revision name - should fail
        with self.assertRaisesRegex(Exception, ".*"):
            self.cmd(f'containerapp function list -g {resource_group} -n {ca_func_name} --revision nonexistent-revision')

        # Test 3: Provide correct revision name - should pass for both revisions
        # Test with first revision
        function_list_rev1 = self.cmd(f'containerapp function list -g {resource_group} -n {ca_func_name} --revision {revision_name_latest}').get_output_in_json()
        assert isinstance(function_list_rev1["value"], list)
        assert len(function_list_rev1["value"]) > 0


        # Test with second revision  
        function_list_rev2 = self.cmd(f'containerapp function list -g {resource_group} -n {ca_func_name} --revision {revision_name_v1}').get_output_in_json()
        assert isinstance(function_list_rev2["value"], list)
        assert len(function_list_rev2["value"]) > 0
