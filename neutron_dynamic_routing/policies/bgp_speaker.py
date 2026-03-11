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

from neutron.conf.policies import base as neutron_base
from neutron_lib import policy as base
from oslo_policy import policy

DEPRECATED_REASON = """
The neutron-dynamic-routing BGP API now supports Secure RBAC default roles.
"""

rules = [
    policy.DocumentedRuleDefault(
        name='create_bgp_speaker',
        check_str=neutron_base.ADMIN,
        scope_types=['project'],
        description='Create a BGP speaker',
        operations=[
            {
                'method': 'POST',
                'path': '/bgp-speakers',
            },
        ],
        deprecated_rule=policy.DeprecatedRule(
            name='create_bgp_speaker',
            check_str=base.RULE_ADMIN_ONLY,
            deprecated_reason=DEPRECATED_REASON,
            deprecated_since='2026.1')
    ),
    policy.DocumentedRuleDefault(
        name='update_bgp_speaker',
        check_str=neutron_base.ADMIN,
        scope_types=['project'],
        description='Update a BGP speaker',
        operations=[
            {
                'method': 'PUT',
                'path': '/bgp-speakers/{id}',
            },
        ],
        deprecated_rule=policy.DeprecatedRule(
            name='update_bgp_speaker',
            check_str=base.RULE_ADMIN_ONLY,
            deprecated_reason=DEPRECATED_REASON,
            deprecated_since='2026.1')
    ),
    policy.DocumentedRuleDefault(
        name='delete_bgp_speaker',
        check_str=neutron_base.ADMIN,
        scope_types=['project'],
        description='Delete a BGP speaker',
        operations=[
            {
                'method': 'DELETE',
                'path': '/bgp-speakers/{id}',
            },
        ],
        deprecated_rule=policy.DeprecatedRule(
            name='delete_bgp_speaker',
            check_str=base.RULE_ADMIN_ONLY,
            deprecated_reason=DEPRECATED_REASON,
            deprecated_since='2026.1')
    ),
    policy.DocumentedRuleDefault(
        name='get_bgp_speaker',
        check_str=neutron_base.ADMIN,
        scope_types=['project'],
        description='Get BGP speakers',
        operations=[
            {
                'method': 'GET',
                'path': '/bgp-speakers',
            },
            {
                'method': 'GET',
                'path': '/bgp-speakers/{id}',
            },
        ],
        deprecated_rule=policy.DeprecatedRule(
            name='get_bgp_speaker',
            check_str=base.RULE_ADMIN_ONLY,
            deprecated_reason=DEPRECATED_REASON,
            deprecated_since='2026.1')
    ),

    policy.DocumentedRuleDefault(
        name='add_bgp_peer',
        check_str=neutron_base.ADMIN,
        scope_types=['project'],
        description='Add a BGP peer to a BGP speaker',
        operations=[
            {
                'method': 'PUT',
                'path': '/bgp-speakers/{id}/add_bgp_peer',
            },
        ],
        deprecated_rule=policy.DeprecatedRule(
            name='add_bgp_peer',
            check_str=base.RULE_ADMIN_ONLY,
            deprecated_reason=DEPRECATED_REASON,
            deprecated_since='2026.1')
    ),
    policy.DocumentedRuleDefault(
        name='remove_bgp_peer',
        check_str=neutron_base.ADMIN,
        scope_types=['project'],
        description='Remove a BGP peer from a BGP speaker',
        operations=[
            {
                'method': 'PUT',
                'path': '/bgp-speakers/{id}/remove_bgp_peer',
            },
        ],
        deprecated_rule=policy.DeprecatedRule(
            name='remove_bgp_peer',
            check_str=base.RULE_ADMIN_ONLY,
            deprecated_reason=DEPRECATED_REASON,
            deprecated_since='2026.1')
    ),
    policy.DocumentedRuleDefault(
        name='add_gateway_network',
        check_str=neutron_base.ADMIN,
        scope_types=['project'],
        description='Add a gateway network to a BGP speaker',
        operations=[
            {
                'method': 'PUT',
                'path': '/bgp-speakers/{id}/add_gateway_network',
            },
        ],
        deprecated_rule=policy.DeprecatedRule(
            name='add_gateway_network',
            check_str=base.RULE_ADMIN_ONLY,
            deprecated_reason=DEPRECATED_REASON,
            deprecated_since='2026.1')
    ),
    policy.DocumentedRuleDefault(
        name='remove_gateway_network',
        check_str=neutron_base.ADMIN,
        scope_types=['project'],
        description='Remove a gateway network from a BGP speaker',
        operations=[
            {
                'method': 'PUT',
                'path': '/bgp-speakers/{id}/remove_gateway_network',
            },
        ],
        deprecated_rule=policy.DeprecatedRule(
            name='remove_gateway_network',
            check_str=base.RULE_ADMIN_ONLY,
            deprecated_reason=DEPRECATED_REASON,
            deprecated_since='2026.1')
    ),
    policy.DocumentedRuleDefault(
        name='get_advertised_routes',
        check_str=neutron_base.ADMIN,
        scope_types=['project'],
        description='Get advertised routes of a BGP speaker',
        operations=[
            {
                'method': 'GET',
                'path': '/bgp-speakers/{id}/get_advertised_routes',
            },
        ],
        deprecated_rule=policy.DeprecatedRule(
            name='get_advertised_routes',
            check_str=base.RULE_ADMIN_ONLY,
            deprecated_reason=DEPRECATED_REASON,
            deprecated_since='2026.1')
    ),
]


def list_rules():
    return rules
