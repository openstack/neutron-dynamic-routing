#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

from neutron_lib import policy as base
from oslo_policy import policy


rules = [
    policy.DocumentedRuleDefault(
        'create_bgp_speaker',
        base.RULE_ADMIN_ONLY,
        'Create a BGP speaker',
        [
            {
                'method': 'POST',
                'path': '/bgp-speakers',
            },
        ]
    ),
    policy.DocumentedRuleDefault(
        'update_bgp_speaker',
        base.RULE_ADMIN_ONLY,
        'Update a BGP speaker',
        [
            {
                'method': 'PUT',
                'path': '/bgp-speakers/{id}',
            },
        ]
    ),
    policy.DocumentedRuleDefault(
        'delete_bgp_speaker',
        base.RULE_ADMIN_ONLY,
        'Delete a BGP speaker',
        [
            {
                'method': 'DELETE',
                'path': '/bgp-speakers/{id}',
            },
        ]
    ),
    policy.DocumentedRuleDefault(
        'get_bgp_speaker',
        base.RULE_ADMIN_ONLY,
        'Get BGP speakers',
        [
            {
                'method': 'GET',
                'path': '/bgp-speakers',
            },
            {
                'method': 'GET',
                'path': '/bgp-speakers/{id}',
            },
        ]
    ),

    policy.DocumentedRuleDefault(
        'add_bgp_peer',
        base.RULE_ADMIN_ONLY,
        'Add a BGP peer to a BGP speaker',
        [
            {
                'method': 'PUT',
                'path': '/bgp-speakers/{id}/add_bgp_peer',
            },
        ]
    ),
    policy.DocumentedRuleDefault(
        'remove_bgp_peer',
        base.RULE_ADMIN_ONLY,
        'Remove a BGP peer from a BGP speaker',
        [
            {
                'method': 'PUT',
                'path': '/bgp-speakers/{id}/remove_bgp_peer',
            },
        ]
    ),
    policy.DocumentedRuleDefault(
        'add_gateway_network',
        base.RULE_ADMIN_ONLY,
        'Add a gateway network to a BGP speaker',
        [
            {
                'method': 'PUT',
                'path': '/bgp-speakers/{id}/add_gateway_network',
            },
        ]
    ),
    policy.DocumentedRuleDefault(
        'remove_gateway_network',
        base.RULE_ADMIN_ONLY,
        'Remove a gateway network from a BGP speaker',
        [
            {
                'method': 'PUT',
                'path': '/bgp-speakers/{id}/remove_gateway_network',
            },
        ]
    ),
    policy.DocumentedRuleDefault(
        'get_advertised_routes',
        base.RULE_ADMIN_ONLY,
        'Get advertised routes of a BGP speaker',
        [
            {
                'method': 'GET',
                'path': '/bgp-speakers/{id}/get_advertised_routes',
            },
        ]
    ),
]


def list_rules():
    return rules
