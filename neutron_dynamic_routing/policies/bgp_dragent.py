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
        name='add_bgp_speaker_to_dragent',
        check_str=neutron_base.ADMIN,
        scope_types=['project'],
        description='Add a BGP speaker to a dynamic routing agent',
        operations=[
            {
                'method': 'POST',
                'path': '/agents/{agent_id}/bgp-drinstances',
            },
        ],
        deprecated_rule=policy.DeprecatedRule(
            name='add_bgp_speaker_to_dragent',
            check_str=base.RULE_ADMIN_ONLY,
            deprecated_reason=DEPRECATED_REASON,
            deprecated_since='2026.1')
    ),
    policy.DocumentedRuleDefault(
        name='remove_bgp_speaker_from_dragent',
        check_str=neutron_base.ADMIN,
        scope_types=['project'],
        description='Remove a BGP speaker from a dynamic routing agent',
        operations=[
            {
                'method': 'DELETE',
                'path': '/agents/{agent_id}/bgp-drinstances/{bgp_speaker_id}',
            },
        ],
        deprecated_rule=policy.DeprecatedRule(
            name='remove_bgp_speaker_from_dragent',
            check_str=base.RULE_ADMIN_ONLY,
            deprecated_reason=DEPRECATED_REASON,
            deprecated_since='2026.1')
    ),
    policy.DocumentedRuleDefault(
        name='list_bgp_speaker_on_dragent',
        check_str=neutron_base.ADMIN,
        scope_types=['project'],
        description='List BGP speakers hosted by a dynamic routing agent',
        operations=[
            {
                'method': 'GET',
                'path': '/agents/{agent_id}/bgp-drinstances',
            },
        ],
        deprecated_rule=policy.DeprecatedRule(
            name='list_bgp_speaker_on_dragent',
            check_str=base.RULE_ADMIN_ONLY,
            deprecated_reason=DEPRECATED_REASON,
            deprecated_since='2026.1')

    ),
    policy.DocumentedRuleDefault(
        name='list_dragent_hosting_bgp_speaker',
        check_str=neutron_base.ADMIN,
        scope_types=['project'],
        description='List dynamic routing agents hosting a BGP speaker',
        operations=[
            {
                'method': 'GET',
                'path': '/bgp-speakers/{bgp_speaker_id}/bgp-dragents',
            },
        ],
        deprecated_rule=policy.DeprecatedRule(
            name='list_dragent_hosting_bgp_speaker',
            check_str=base.RULE_ADMIN_ONLY,
            deprecated_reason=DEPRECATED_REASON,
            deprecated_since='2026.1')
    ),
]


def list_rules():
    return rules
