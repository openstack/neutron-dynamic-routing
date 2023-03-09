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
        'create_bgp_peer',
        base.RULE_ADMIN_ONLY,
        'Create a BGP peer',
        [
            {
                'method': 'POST',
                'path': '/bgp-peers',
            },
        ]
    ),
    policy.DocumentedRuleDefault(
        'update_bgp_peer',
        base.RULE_ADMIN_ONLY,
        'Update a BGP peer',
        [
            {
                'method': 'PUT',
                'path': '/bgp-peers/{id}',
            },
        ]
    ),
    policy.DocumentedRuleDefault(
        'delete_bgp_peer',
        base.RULE_ADMIN_ONLY,
        'Delete a BGP peer',
        [
            {
                'method': 'DELETE',
                'path': '/bgp-peers/{id}',
            },
        ]
    ),
    policy.DocumentedRuleDefault(
        'get_bgp_peer',
        base.RULE_ADMIN_ONLY,
        'Get BGP peers',
        [
            {
                'method': 'GET',
                'path': '/bgp-peers',
            },
            {
                'method': 'GET',
                'path': '/bgp-peers/{id}',
            },
        ]
    ),
]


def list_rules():
    return rules
