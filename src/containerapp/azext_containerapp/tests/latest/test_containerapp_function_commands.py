# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
from unittest import mock

from azure.cli.command_modules.containerapp._utils import format_location
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck, JMESPathCheckExists, 
                               JMESPathCheckNotExists, live_only)

from .utils import prepare_containerapp_env_for_app_e2e_tests

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))
TEST_LOCATION = "northcentralusstage"


class ContainerAppFunctionTest(ScenarioTest):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, random_config_dir=True, **kwargs)

    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location="northcentralusstage")
    def test_containerapp_function_validation_error(self, resource_group):
        """Test that function commands fail on regular container apps (not function apps)"""
        location = TEST_LOCATION
        self.cmd('configure --defaults location={}'.format(location))

        app = self.create_random_name(prefix='containerapp', length=24)
        env = prepare_containerapp_env_for_app_e2e_tests(self, location)
        
        # Create a regular container app (not a function app)
        self.cmd('containerapp create -g {} -n {} --environment {} --image mcr.microsoft.com/k8se/quickstart:latest --ingress external --target-port 80'.format(
            resource_group, app, env))

        # Test that function commands fail with validation error
        with self.assertRaises(Exception) as context:
            self.cmd('containerapp function list -g {} -n {}'.format(resource_group, app))
        self.assertIn("is not an Azure Function App", str(context.exception))

        with self.assertRaises(Exception) as context:
            self.cmd('containerapp function show -g {} -n {} --function-name testfunc'.format(resource_group, app))
        self.assertIn("is not an Azure Function App", str(context.exception))

        with self.assertRaises(Exception) as context:
            self.cmd('containerapp function keys list -g {} -n {} --key-type hostKey'.format(resource_group, app))
        self.assertIn("is not an Azure Function App", str(context.exception))

        with self.assertRaises(Exception) as context:
            self.cmd('containerapp function keys show -g {} -n {} --key-type hostKey --key-name default'.format(resource_group, app))
        self.assertIn("is not an Azure Function App", str(context.exception))

        with self.assertRaises(Exception) as context:
            self.cmd('containerapp function keys set -g {} -n {} --key-type hostKey --key-name default --key-value test'.format(resource_group, app))
        self.assertIn("is not an Azure Function App", str(context.exception))

        with self.assertRaises(Exception) as context:
            self.cmd('containerapp function invocations summary -g {} -n {} --function-name myfunction'.format(resource_group, app))
        self.assertIn("is not an Azure Function App", str(context.exception))

        with self.assertRaises(Exception) as context:
            self.cmd('containerapp function invocations traces -g {} -n {} --function-name myfunction'.format(resource_group, app))
        self.assertIn("is not an Azure Function App", str(context.exception))




class ContainerAppFunctionAppTest(ScenarioTest):
    """Tests for actual function app operations - these would need a real function app"""
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, random_config_dir=True, **kwargs)

    @unittest.skip("Requires actual Azure Function App deployment - enable for integration tests")
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location=TEST_LOCATION)
    def test_containerapp_function_list(self, resource_group):
        """Test listing functions in a function app"""
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        # This would need to create/use an actual function app
        function_app = "your-function-app-name"  # Replace with actual function app
        
        # Test function list
        self.cmd('containerapp function list -g {} -n {}'.format(resource_group, function_app), checks=[
            JMESPathCheckExists('value'),
            JMESPathCheck('type(@.value)', 'array')
        ])

        # Test function list with revision
        self.cmd('containerapp function list -g {} -n {} --revision latest'.format(resource_group, function_app), checks=[
            JMESPathCheckExists('value')
        ])

    @unittest.skip("Requires actual Azure Function App deployment - enable for integration tests")
    @AllowLargeResponse(8192) 
    @ResourceGroupPreparer(location=TEST_LOCATION)
    def test_containerapp_function_show(self, resource_group):
        """Test showing a specific function"""
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        function_app = "your-function-app-name"  # Replace with actual function app
        function_name = "HttpExample"  # Replace with actual function name

        # Test function show
        self.cmd('containerapp function show -g {} -n {} --function-name {}'.format(
            resource_group, function_app, function_name), checks=[
            JMESPathCheck('name', function_name),
            JMESPathCheckExists('properties')
        ])

        # Test function show with revision
        self.cmd('containerapp function show -g {} -n {} --function-name {} --revision latest'.format(
            resource_group, function_app, function_name), checks=[
            JMESPathCheck('name', function_name)
        ])

    @unittest.skip("Requires actual Azure Function App deployment - enable for integration tests") 
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location=TEST_LOCATION)
    def test_containerapp_function_keys_list(self, resource_group):
        """Test listing function keys"""
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        function_app = "your-function-app-name"  # Replace with actual function app
        function_name = "HttpExample"  # Replace with actual function name

        # Test list host keys
        self.cmd('containerapp function keys list -g {} -n {} --key-type hostKey'.format(
            resource_group, function_app), checks=[
            JMESPathCheckExists('keys'),
            JMESPathCheck('type(@.keys)', 'object')
        ])

        # Test list function keys
        self.cmd('containerapp function keys list -g {} -n {} --key-type functionKey --function-name {}'.format(
            resource_group, function_app, function_name), checks=[
            JMESPathCheckExists('keys')
        ])

    @unittest.skip("Requires actual Azure Function App deployment - enable for integration tests")
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location=TEST_LOCATION) 
    def test_containerapp_function_keys_show(self, resource_group):
        """Test showing a specific function key"""
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        function_app = "your-function-app-name"  # Replace with actual function app
        function_name = "HttpExample"  # Replace with actual function name
        key_name = "default"

        # Test show host key
        self.cmd('containerapp function keys show -g {} -n {} --key-type hostKey --key-name {}'.format(
            resource_group, function_app, key_name), checks=[
            JMESPathCheck('name', key_name),
            JMESPathCheckExists('value')
        ])

        # Test show function key
        self.cmd('containerapp function keys show -g {} -n {} --key-type functionKey --function-name {} --key-name {}'.format(
            resource_group, function_app, function_name, key_name), checks=[
            JMESPathCheck('name', key_name),
            JMESPathCheckExists('value')
        ])

    @unittest.skip("Requires actual Azure Function App deployment - enable for integration tests")
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location=TEST_LOCATION)
    def test_containerapp_function_keys_set(self, resource_group):
        """Test setting a function key"""
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        function_app = "your-function-app-name"  # Replace with actual function app
        function_name = "HttpExample"  # Replace with actual function name
        key_name = "testkey"
        key_value = "test-key-value-12345"

        # Test set function key
        self.cmd('containerapp function keys set -g {} -n {} --key-type functionKey --function-name {} --key-name {} --key-value {}'.format(
            resource_group, function_app, function_name, key_name, key_value), checks=[
            JMESPathCheck('name', key_name),
            JMESPathCheck('value', key_value)
        ])

        # Verify the key was set by showing it
        self.cmd('containerapp function keys show -g {} -n {} --key-type functionKey --function-name {} --key-name {}'.format(
            resource_group, function_app, function_name, key_name), checks=[
            JMESPathCheck('name', key_name),
            JMESPathCheck('value', key_value)
        ])

    @unittest.skip("Requires actual Azure Function App deployment with invocations - enable for integration tests")
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location=TEST_LOCATION)
    def test_containerapp_function_invocations_summary(self, resource_group):
        """Test getting function invocations summary"""
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        function_app = "your-function-app-name"  # Replace with actual function app
        function_name = "HttpExample"  # Replace with actual function name

        # Test invocations summary
        self.cmd('containerapp function invocations summary -g {} -n {} --function-name {}'.format(
            resource_group, function_app, function_name), checks=[
            JMESPathCheckExists('summary'),
            JMESPathCheckExists('functionName')
        ])

        # Test with time range
        self.cmd('containerapp function invocations summary -g {} -n {} --function-name {} --timespan "1h"'.format(
            resource_group, function_app, function_name), checks=[
            JMESPathCheckExists('summary')
        ])

    @unittest.skip("Requires actual Azure Function App deployment with invocations - enable for integration tests")
    @AllowLargeResponse(8192)
    @ResourceGroupPreparer(location=TEST_LOCATION)
    def test_containerapp_function_invocations_traces(self, resource_group):
        """Test getting function invocations traces"""
        self.cmd('configure --defaults location={}'.format(TEST_LOCATION))

        function_app = "your-function-app-name"  # Replace with actual function app
        function_name = "HttpExample"  # Replace with actual function name

        # Test invocations traces
        self.cmd('containerapp function invocations traces -g {} -n {} --function-name {}'.format(
            resource_group, function_app, function_name), checks=[
            JMESPathCheckExists('traces'),
            JMESPathCheck('type(@.traces)', 'array')
        ])

        # Test with time range and limit
        self.cmd('containerapp function invocations traces -g {} -n {} --function-name {} --timespan "1h" --limit 10'.format(
            resource_group, function_app, function_name), checks=[
            JMESPathCheckExists('traces')
        ])


class ContainerAppFunctionCommandStructureTest(ScenarioTest):
    """Test command structure and help without requiring actual function apps"""
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, random_config_dir=True, **kwargs)

    def test_containerapp_function_commands_help(self):
        """Test that all function commands have proper help"""
        # Test main function command group
        result = self.cmd('containerapp function -h')
        self.assertIn('Commands:', result.output)
        self.assertIn('list', result.output)
        self.assertIn('show', result.output)

        # Test function list help
        result = self.cmd('containerapp function list -h')
        self.assertIn('List functions', result.output)
        self.assertIn('--resource-group', result.output)
        self.assertIn('--name', result.output)

        # Test function show help  
        result = self.cmd('containerapp function show -h')
        self.assertIn('Show function details', result.output)
        self.assertIn('--function-name', result.output)

        # Test function keys help
        result = self.cmd('containerapp function keys -h')
        self.assertIn('Commands:', result.output)
        self.assertIn('list', result.output)
        self.assertIn('show', result.output)
        self.assertIn('set', result.output)

        # Test function keys list help
        result = self.cmd('containerapp function keys list -h')
        self.assertIn('List function keys', result.output)
        self.assertIn('--key-type', result.output)

        # Test function keys show help
        result = self.cmd('containerapp function keys show -h')
        self.assertIn('Show function key', result.output)
        self.assertIn('--key-name', result.output)

        # Test function keys set help
        result = self.cmd('containerapp function keys set -h')
        self.assertIn('Set function key', result.output)
        self.assertIn('--key-value', result.output)

        # Test function invocations help
        result = self.cmd('containerapp function invocations -h')
        self.assertIn('Commands:', result.output)
        self.assertIn('summary', result.output)
        self.assertIn('traces', result.output)

        # Test function invocations summary help
        result = self.cmd('containerapp function invocations summary -h')
        self.assertIn('Get invocations summary', result.output)
        self.assertIn('--timespan', result.output)

        # Test function invocations traces help
        result = self.cmd('containerapp function invocations traces -h')
        self.assertIn('Get invocations traces', result.output)
        self.assertIn('--limit', result.output)

    def test_containerapp_function_parameter_validation(self):
        """Test parameter validation without making actual API calls"""
        # Test missing resource group
        with self.assertRaises(SystemExit):
            self.cmd('containerapp function list --name test')

        # Test missing container app name
        with self.assertRaises(SystemExit):
            self.cmd('containerapp function list --resource-group test')

        # Test missing function name for show command
        with self.assertRaises(SystemExit):
            self.cmd('containerapp function show --resource-group test --name test')

        # Test missing key-type for keys commands
        with self.assertRaises(SystemExit):
            self.cmd('containerapp function keys list --resource-group test --name test')

        # Test missing key-name for keys show command
        with self.assertRaises(SystemExit):
            self.cmd('containerapp function keys show --resource-group test --name test --key-type hostKey')