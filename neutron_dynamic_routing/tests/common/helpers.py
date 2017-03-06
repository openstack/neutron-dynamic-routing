# Copyright 2016 Hewlett Packard Development Co
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from neutron_lib import context

from neutron.tests.common import helpers

from neutron_dynamic_routing.services.bgp.common import constants as bgp_const


def _get_bgp_dragent_dict(host):
    agent = {
        'binary': 'neutron-bgp-dragent',
        'host': host,
        'topic': 'q-bgp_dragent',
        'agent_type': bgp_const.AGENT_TYPE_BGP_ROUTING,
        'configurations': {'bgp_speakers': 1}}
    return agent


def register_bgp_dragent(host=helpers.HOST, admin_state_up=True,
                        alive=True):
    agent = helpers._register_agent(
        _get_bgp_dragent_dict(host))

    if not admin_state_up:
        helpers.set_agent_admin_state(agent['id'])
    if not alive:
        helpers.kill_agent(agent['id'])

    return helpers.FakePlugin()._get_agent_by_type_and_host(
        context.get_admin_context(), agent['agent_type'], agent['host'])
