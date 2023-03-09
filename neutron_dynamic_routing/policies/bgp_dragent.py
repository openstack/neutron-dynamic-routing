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
        'add_bgp_speaker_to_dragent',
        base.RULE_ADMIN_ONLY,
        'Add a BGP speaker to a dynamic routing agent',
        [
            {
                'method': 'POST',
                'path': '/agents/{agent_id}/bgp-drinstances',
            },
        ]
    ),
    policy.DocumentedRuleDefault(
        'remove_bgp_speaker_from_dragent',
        base.RULE_ADMIN_ONLY,
        'Remove a BGP speaker from a dynamic routing agent',
        [
            {
                'method': 'DELETE',
                'path': '/agents/{agent_id}/bgp-drinstances/{bgp_speaker_id}',
            },
        ]
    ),
    policy.DocumentedRuleDefault(
        'list_bgp_speaker_on_dragent',
        base.RULE_ADMIN_ONLY,
        'List BGP speakers hosted by a dynamic routing agent',
        [
            {
                'method': 'GET',
                'path': '/agents/{agent_id}/bgp-drinstances',
            },
        ]
    ),
    policy.DocumentedRuleDefault(
        'list_dragent_hosting_bgp_speaker',
        base.RULE_ADMIN_ONLY,
        'List dynamic routing agents hosting a BGP speaker',
        [
            {
                'method': 'GET',
                'path': '/bgp-speakers/{bgp_speaker_id}/bgp-dragents',
            },
        ]
    ),
]


def list_rules():
    return rules
