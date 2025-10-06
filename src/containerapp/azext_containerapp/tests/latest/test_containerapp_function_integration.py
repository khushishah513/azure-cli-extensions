# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Integration tests for containerapp function commands.

To run these tests with a real function app:
1. Deploy an Azure Function App on Container Apps
2. Update the FUNCTION_APP_NAME and RESOURCE_GROUP variables below
3. Uncomment the @pytest.mark.skip decorators
4. Run: python -m pytest test_containerapp_function_integration.py -v
"""

import pytest
import os
import subprocess
import json

# Configuration - Update these with your actual function app details
RESOURCE_GROUP = "your-resource-group"
FUNCTION_APP_NAME = "your-function-app-name" 
FUNCTION_NAME = "HttpExample"  # Common default function name
LOCATION = "northcentralusstage"


class TestContainerAppFunctionCommands:
    """Integration tests for containerapp function commands"""
    
    def setup_method(self):
        """Setup before each test"""
        # Configure default location
        subprocess.run(['az', 'configure', '--defaults', f'location={LOCATION}'], check=True)
    
    @pytest.mark.skip(reason="Requires actual function app - update FUNCTION_APP_NAME and remove skip")
    def test_function_list(self):
        """Test az containerapp function list"""
        # Test basic list
        result = subprocess.run([
            'az', 'containerapp', 'function', 'list',
            '-g', RESOURCE_GROUP,
            '-n', FUNCTION_APP_NAME,
            '--output', 'json'
        ], capture_output=True, text=True, check=True)
        
        functions = json.loads(result.stdout)
        assert 'value' in functions
        assert isinstance(functions['value'], list)
        
        # Test list with revision
        result = subprocess.run([
            'az', 'containerapp', 'function', 'list', 
            '-g', RESOURCE_GROUP,
            '-n', FUNCTION_APP_NAME,
            '--revision', 'latest',
            '--output', 'json'
        ], capture_output=True, text=True, check=True)
        
        functions_with_revision = json.loads(result.stdout)
        assert 'value' in functions_with_revision

    @pytest.mark.skip(reason="Requires actual function app - update FUNCTION_APP_NAME and remove skip") 
    def test_function_show(self):
        """Test az containerapp function show"""
        result = subprocess.run([
            'az', 'containerapp', 'function', 'show',
            '-g', RESOURCE_GROUP,
            '-n', FUNCTION_APP_NAME, 
            '--function-name', FUNCTION_NAME,
            '--output', 'json'
        ], capture_output=True, text=True, check=True)
        
        function = json.loads(result.stdout)
        assert function['name'] == FUNCTION_NAME
        assert 'properties' in function

    @pytest.mark.skip(reason="Requires actual function app - update FUNCTION_APP_NAME and remove skip")
    def test_function_keys_list_host_keys(self):
        """Test az containerapp function keys list for host keys"""
        result = subprocess.run([
            'az', 'containerapp', 'function', 'keys', 'list',
            '-g', RESOURCE_GROUP,
            '-n', FUNCTION_APP_NAME,
            '--key-type', 'hostKey',
            '--output', 'json'
        ], capture_output=True, text=True, check=True)
        
        keys = json.loads(result.stdout)
        assert 'keys' in keys
        assert isinstance(keys['keys'], dict)

    @pytest.mark.skip(reason="Requires actual function app - update FUNCTION_APP_NAME and remove skip")
    def test_function_keys_list_function_keys(self):
        """Test az containerapp function keys list for function keys"""
        result = subprocess.run([
            'az', 'containerapp', 'function', 'keys', 'list',
            '-g', RESOURCE_GROUP,
            '-n', FUNCTION_APP_NAME,
            '--key-type', 'functionKey',
            '--function-name', FUNCTION_NAME,
            '--output', 'json'
        ], capture_output=True, text=True, check=True)
        
        keys = json.loads(result.stdout)
        assert 'keys' in keys

    @pytest.mark.skip(reason="Requires actual function app - update FUNCTION_APP_NAME and remove skip")
    def test_function_keys_show(self):
        """Test az containerapp function keys show"""
        # First list keys to get a valid key name
        result = subprocess.run([
            'az', 'containerapp', 'function', 'keys', 'list',
            '-g', RESOURCE_GROUP, 
            '-n', FUNCTION_APP_NAME,
            '--key-type', 'hostKey',
            '--output', 'json'
        ], capture_output=True, text=True, check=True)
        
        keys = json.loads(result.stdout)
        if keys['keys']:
            key_name = list(keys['keys'].keys())[0]
            
            # Show the specific key
            result = subprocess.run([
                'az', 'containerapp', 'function', 'keys', 'show',
                '-g', RESOURCE_GROUP,
                '-n', FUNCTION_APP_NAME,
                '--key-type', 'hostKey', 
                '--key-name', key_name,
                '--output', 'json'
            ], capture_output=True, text=True, check=True)
            
            key = json.loads(result.stdout)
            assert key['name'] == key_name
            assert 'value' in key

    @pytest.mark.skip(reason="Requires actual function app - update FUNCTION_APP_NAME and remove skip")
    def test_function_keys_set(self):
        """Test az containerapp function keys set"""
        key_name = 'test-key'
        key_value = 'test-key-value-12345'
        
        result = subprocess.run([
            'az', 'containerapp', 'function', 'keys', 'set',
            '-g', RESOURCE_GROUP,
            '-n', FUNCTION_APP_NAME,
            '--key-type', 'functionKey',
            '--function-name', FUNCTION_NAME,
            '--key-name', key_name,
            '--key-value', key_value,
            '--output', 'json'
        ], capture_output=True, text=True, check=True)
        
        key = json.loads(result.stdout)
        assert key['name'] == key_name
        assert key['value'] == key_value
        
        # Verify the key was set by showing it
        result = subprocess.run([
            'az', 'containerapp', 'function', 'keys', 'show',
            '-g', RESOURCE_GROUP,
            '-n', FUNCTION_APP_NAME,
            '--key-type', 'functionKey',
            '--function-name', FUNCTION_NAME,
            '--key-name', key_name,
            '--output', 'json'
        ], capture_output=True, text=True, check=True)
        
        shown_key = json.loads(result.stdout)
        assert shown_key['name'] == key_name
        assert shown_key['value'] == key_value

    @pytest.mark.skip(reason="Requires actual function app with invocations - update FUNCTION_APP_NAME and remove skip")
    def test_function_invocations_summary(self):
        """Test az containerapp function invocations summary"""
        result = subprocess.run([
            'az', 'containerapp', 'function', 'invocations', 'summary',
            '-g', RESOURCE_GROUP,
            '-n', FUNCTION_APP_NAME,
            '--function-name', FUNCTION_NAME,
            '--output', 'json'
        ], capture_output=True, text=True, check=True)
        
        summary = json.loads(result.stdout)
        assert 'summary' in summary or 'functionName' in summary
        
        # Test with timespan
        result = subprocess.run([
            'az', 'containerapp', 'function', 'invocations', 'summary', 
            '-g', RESOURCE_GROUP,
            '-n', FUNCTION_APP_NAME,
            '--function-name', FUNCTION_NAME,
            '--timespan', '1h',
            '--output', 'json'
        ], capture_output=True, text=True, check=True)
        
        summary_with_timespan = json.loads(result.stdout)
        assert 'summary' in summary_with_timespan or 'functionName' in summary_with_timespan

    @pytest.mark.skip(reason="Requires actual function app with invocations - update FUNCTION_APP_NAME and remove skip")
    def test_function_invocations_traces(self):
        """Test az containerapp function invocations traces"""
        result = subprocess.run([
            'az', 'containerapp', 'function', 'invocations', 'traces',
            '-g', RESOURCE_GROUP,
            '-n', FUNCTION_APP_NAME,
            '--function-name', FUNCTION_NAME,
            '--output', 'json'
        ], capture_output=True, text=True, check=True)
        
        traces = json.loads(result.stdout)
        assert 'traces' in traces
        assert isinstance(traces['traces'], list)
        
        # Test with timespan and limit
        result = subprocess.run([
            'az', 'containerapp', 'function', 'invocations', 'traces',
            '-g', RESOURCE_GROUP,
            '-n', FUNCTION_APP_NAME,
            '--function-name', FUNCTION_NAME,
            '--timespan', '1h',
            '--limit', '10',
            '--output', 'json'
        ], capture_output=True, text=True, check=True)
        
        limited_traces = json.loads(result.stdout)
        assert 'traces' in limited_traces

    def test_function_validation_error_regular_containerapp(self):
        """Test that function commands fail on regular container apps"""
        # This test assumes there's a regular container app that will fail validation
        # You can create one for testing or use an existing non-function container app
        regular_app_name = "regular-containerapp"  # Update with actual regular container app
        
        # Test function list validation error
        result = subprocess.run([
            'az', 'containerapp', 'function', 'list',
            '-g', RESOURCE_GROUP,
            '-n', regular_app_name,
        ], capture_output=True, text=True, check=False)
        
        assert result.returncode != 0
        assert "is not an Azure Function App" in result.stderr

    def test_function_commands_help(self):
        """Test that all function commands show help properly"""
        commands_to_test = [
            ['az', 'containerapp', 'function', '-h'],
            ['az', 'containerapp', 'function', 'list', '-h'],
            ['az', 'containerapp', 'function', 'show', '-h'],
            ['az', 'containerapp', 'function', 'keys', '-h'],
            ['az', 'containerapp', 'function', 'keys', 'list', '-h'],
            ['az', 'containerapp', 'function', 'keys', 'show', '-h'],
            ['az', 'containerapp', 'function', 'keys', 'set', '-h'],
            ['az', 'containerapp', 'function', 'invocations', '-h'],
            ['az', 'containerapp', 'function', 'invocations', 'summary', '-h'],
            ['az', 'containerapp', 'function', 'invocations', 'traces', '-h'],
        ]
        
        for cmd in commands_to_test:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            assert result.returncode == 0
            assert 'usage:' in result.stdout.lower() or 'commands:' in result.stdout.lower()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])