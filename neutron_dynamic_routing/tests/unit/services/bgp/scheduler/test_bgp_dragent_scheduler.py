# Copyright 2016 Huawei Technologies India Pvt. Ltd.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from unittest import mock

from neutron.tests.unit import testlib_api
from neutron_lib.callbacks import events
from neutron_lib.callbacks import registry
from neutron_lib import context
from oslo_utils import importutils
import testscenarios

from neutron_dynamic_routing.api.rpc.callbacks import resources as dr_resources
from neutron_dynamic_routing.db import bgp_db
from neutron_dynamic_routing.db import bgp_dragentscheduler_db as bgp_dras_db
from neutron_dynamic_routing.services.bgp import bgp_plugin
from neutron_dynamic_routing.services.bgp.scheduler import bgp_dragent_scheduler as bgp_dras  # noqa
from neutron_dynamic_routing.tests.common import helpers

# Required to generate tests from scenarios. Not compatible with nose.
load_tests = testscenarios.load_tests_apply_scenarios


class TestBgpDrAgentSchedulerBaseTestCase(testlib_api.SqlTestCase):

    def setUp(self):
        super(TestBgpDrAgentSchedulerBaseTestCase, self).setUp()
        self.ctx = context.get_admin_context()
        self.bgp_speaker = {'id': 'foo_bgp_speaker_id'}
        self.bgp_speaker_id = 'foo_bgp_speaker_id'
        self._save_bgp_speaker(self.bgp_speaker_id)

    def _create_and_set_agents_down(self, hosts, down_agent_count=0,
                                    admin_state_up=True):
        agents = []
        for i, host in enumerate(hosts):
            is_alive = i >= down_agent_count
            agents.append(helpers.register_bgp_dragent(
                host,
                admin_state_up=admin_state_up,
                alive=is_alive))
        return agents

    def _save_bgp_speaker(self, bgp_speaker_id):
        cls = bgp_db.BgpDbMixin()
        bgp_speaker_body = {'bgp_speaker': {
                                'name': 'fake_bgp_speaker',
                                'ip_version': '4',
                                'local_as': '123',
                                'advertise_floating_ip_host_routes': False,
                                'advertise_tenant_networks': False,
                                'peers': [],
                                'networks': []}}
        cls._save_bgp_speaker(self.ctx, bgp_speaker_body, uuid=bgp_speaker_id)

    def _get_dragent_bgp_speaker_bindings(self, bgp_speaker_id):
        return self.ctx.session.query(
            bgp_dras_db.BgpSpeakerDrAgentBinding).filter_by(
            bgp_speaker_id=bgp_speaker_id).all()

    def _test_schedule_bind_bgp_speaker(self, agents, bgp_speaker_id):
        scheduler = bgp_dras.ChanceScheduler()
        scheduler.resource_filter.bind(self.ctx, agents, bgp_speaker_id)
        results = self._get_dragent_bgp_speaker_bindings(bgp_speaker_id)

        for result in results:
            self.assertEqual(bgp_speaker_id, result.bgp_speaker_id)


class TestSchedulerCallback(TestBgpDrAgentSchedulerBaseTestCase):

    def setUp(self):
        super(TestSchedulerCallback, self).setUp()
        bgp_notify_p = mock.patch('neutron_dynamic_routing.api.rpc.'
                                  'agentnotifiers.bgp_dr_rpc_agent_api.'
                                  'BgpDrAgentNotifyApi')
        bgp_notify_p.start()
        rpc_conn_p = mock.patch('neutron_lib.rpc.Connection')
        rpc_conn_p.start()
        self.plugin = bgp_plugin.BgpPlugin()
        self.scheduler = bgp_dras.ChanceScheduler()

    def _create_test_payload(self, context='test_ctx'):
        bgp_speaker = {'id': '11111111-2222-3333-4444-555555555555'}
        payload = events.DBEventPayload(
                      context,
                      metadata={'plugin': self.plugin},
                      states=(bgp_speaker,))
        return payload

    def test__register_callbacks(self):
        with mock.patch.object(registry, 'subscribe') as subscribe:
            scheduler = bgp_dras.ChanceScheduler()
            expected_calls = [
                mock.call(scheduler.schedule_bgp_speaker_callback,
                          dr_resources.BGP_SPEAKER, events.AFTER_CREATE),
            ]
            self.assertEqual(subscribe.call_args_list, expected_calls)
        with mock.patch.object(registry, 'subscribe') as subscribe:
            scheduler = bgp_dras.WeightScheduler()
            expected_calls = [
                mock.call(scheduler.schedule_bgp_speaker_callback,
                          dr_resources.BGP_SPEAKER, events.AFTER_CREATE),
            ]
            self.assertEqual(subscribe.call_args_list, expected_calls)

    def test_schedule_bgp_speaker_callback_with_valid_event(self):
        payload = self._create_test_payload()
        with mock.patch.object(self.plugin,
                               'schedule_bgp_speaker') as sched_bgp:
            self.scheduler.schedule_bgp_speaker_callback(
                dr_resources.BGP_SPEAKER,
                events.AFTER_CREATE,
                self.scheduler, payload)
            sched_bgp.assert_called_once_with(mock.ANY,
                                              payload.latest_state)

    def test_schedule_bgp_speaker_callback_with_invalid_event(self):
        payload = self._create_test_payload()
        with mock.patch.object(self.plugin,
                               'schedule_bgp_speaker') as sched_bgp:
            self.scheduler.schedule_bgp_speaker_callback(
                dr_resources.BGP_SPEAKER,
                events.BEFORE_CREATE,
                self.scheduler, payload)
            sched_bgp.assert_not_called()


class TestBgpDrAgentScheduler(TestBgpDrAgentSchedulerBaseTestCase,
                              bgp_db.BgpDbMixin):

    def test_schedule_bind_bgp_speaker_single_agent(self):
        agents = self._create_and_set_agents_down(['host-a'])
        self._test_schedule_bind_bgp_speaker(agents, self.bgp_speaker_id)

    def test_schedule_bind_bgp_speaker_multi_agents(self):
        agents = self._create_and_set_agents_down(['host-a', 'host-b'])
        self._test_schedule_bind_bgp_speaker(agents, self.bgp_speaker_id)


class TestBgpAgentFilter(TestBgpDrAgentSchedulerBaseTestCase,
                         bgp_db.BgpDbMixin,
                         bgp_dras_db.BgpDrAgentSchedulerDbMixin):

    def setUp(self):
        super(TestBgpAgentFilter, self).setUp()
        self.bgp_drscheduler = importutils.import_object(
            'neutron_dynamic_routing.services.bgp.scheduler.'
            'bgp_dragent_scheduler.ChanceScheduler'
        )
        self.plugin = self

    def _test_filter_agents_helper(self, bgp_speaker,
                                   expected_filtered_dragent_ids=None,
                                   expected_num_agents=1):
        filtered_agents = (
            self.plugin.bgp_drscheduler.resource_filter.filter_agents(
                self.plugin, self.ctx, bgp_speaker))
        self.assertEqual(expected_num_agents,
                         filtered_agents['n_agents'])
        actual_filtered_dragent_ids = [
            agent.id for agent in filtered_agents['hostable_agents']]
        if expected_filtered_dragent_ids is None:
            expected_filtered_dragent_ids = []
        self.assertEqual(len(expected_filtered_dragent_ids),
                         len(actual_filtered_dragent_ids))
        for filtered_agent_id in actual_filtered_dragent_ids:
            self.assertIn(filtered_agent_id, expected_filtered_dragent_ids)

    def test_filter_agents_single_agent(self):
        agents = self._create_and_set_agents_down(['host-a'])
        expected_filtered_dragent_ids = [agents[0].id]
        self._test_filter_agents_helper(
            self.bgp_speaker,
            expected_filtered_dragent_ids=expected_filtered_dragent_ids)

    def test_filter_agents_no_agents(self):
        expected_filtered_dragent_ids = []
        self._test_filter_agents_helper(
            self.bgp_speaker,
            expected_filtered_dragent_ids=expected_filtered_dragent_ids,
            expected_num_agents=0)

    def test_filter_agents_two_agents(self):
        agents = self._create_and_set_agents_down(['host-a', 'host-b'])
        expected_filtered_dragent_ids = [agent.id for agent in agents]
        self._test_filter_agents_helper(
            self.bgp_speaker,
            expected_filtered_dragent_ids=expected_filtered_dragent_ids)

    def test_filter_agents_agent_already_scheduled(self):
        agents = self._create_and_set_agents_down(['host-a', 'host-b'])
        self._test_schedule_bind_bgp_speaker([agents[0]], self.bgp_speaker_id)
        self._test_filter_agents_helper(self.bgp_speaker,
                                        expected_num_agents=0)

    def test_filter_agents_multiple_agents_bgp_speakers(self):
        agents = self._create_and_set_agents_down(['host-a', 'host-b'])
        self._test_schedule_bind_bgp_speaker([agents[0]], self.bgp_speaker_id)
        bgp_speaker = {'id': 'bar-speaker-id'}
        self._save_bgp_speaker(bgp_speaker['id'])
        expected_filtered_dragent_ids = [agents[1].id]
        self._test_filter_agents_helper(
            bgp_speaker,
            expected_filtered_dragent_ids=expected_filtered_dragent_ids)


class TestAutoScheduleBgpSpeakers(TestBgpDrAgentSchedulerBaseTestCase):
    """Unit test scenarios for schedule_unscheduled_bgp_speakers.

    bgp_speaker_present
        BGP speaker is present or not

    scheduled_already
        BGP speaker is already scheduled to the agent or not

    agent_down
        BGP DRAgent is down or alive

    valid_host
        If true, then an valid host is passed to schedule BGP speaker,
        else an invalid host is passed.
    """
    scenarios = [
        ('BGP speaker present',
         dict(bgp_speaker_present=True,
              scheduled_already=False,
              agent_down=False,
              valid_host=True,
              expected_result=True)),

        ('No BGP speaker',
         dict(bgp_speaker_present=False,
              scheduled_already=False,
              agent_down=False,
              valid_host=True,
              expected_result=False)),

        ('BGP speaker already scheduled',
         dict(bgp_speaker_present=True,
              scheduled_already=True,
              agent_down=False,
              valid_host=True,
              expected_result=False)),

        ('BGP DR agent down',
         dict(bgp_speaker_present=True,
              scheduled_already=False,
              agent_down=True,
              valid_host=False,
              expected_result=False)),

        ('Invalid host',
         dict(bgp_speaker_present=True,
              scheduled_already=False,
              agent_down=False,
              valid_host=False,
              expected_result=False)),
    ]

    def test_auto_schedule_bgp_speaker(self):
        scheduler = bgp_dras.ChanceScheduler()
        if self.bgp_speaker_present:
            down_agent_count = 1 if self.agent_down else 0
            agents = self._create_and_set_agents_down(
                ['host-a'], down_agent_count=down_agent_count)
            if self.scheduled_already:
                self._test_schedule_bind_bgp_speaker(agents,
                                                     self.bgp_speaker_id)

        expected_hosted_agents = (1 if self.bgp_speaker_present and
                                  self.valid_host else 0)
        host = "host-a" if self.valid_host else "host-b"
        observed_ret_value = scheduler.schedule_unscheduled_bgp_speakers(
            self.ctx, host)
        self.assertEqual(self.expected_result, observed_ret_value)
        hosted_agents = self.ctx.session.query(
            bgp_dras_db.BgpSpeakerDrAgentBinding).all()
        self.assertEqual(expected_hosted_agents, len(hosted_agents))


class TestRescheduleBgpSpeaker(TestBgpDrAgentSchedulerBaseTestCase,
                               bgp_db.BgpDbMixin):

    def setUp(self):
        super(TestRescheduleBgpSpeaker, self).setUp()
        bgp_notify_p = mock.patch('neutron_dynamic_routing.api.rpc.'
                                  'agentnotifiers.bgp_dr_rpc_agent_api.'
                                  'BgpDrAgentNotifyApi')
        bgp_notify_p.start()
        rpc_conn_p = mock.patch('neutron_lib.rpc.Connection')
        rpc_conn_p.start()
        self.plugin = bgp_plugin.BgpPlugin()
        self.scheduler = bgp_dras.ChanceScheduler()
        self.host1 = 'host-a'
        self.host2 = 'host-b'

    def _kill_bgp_dragent(self, hosts):
        agents = []
        for host in hosts:
            agents.append(
                helpers.register_bgp_dragent(host=host, alive=False))
        return agents

    def _schedule_bind_bgp_speaker(self, agents, bgp_speaker_id):
        self.scheduler.resource_filter.bind(self.ctx, agents, bgp_speaker_id)
        return self._get_dragent_bgp_speaker_bindings(bgp_speaker_id)

    def test_reschedule_bgp_speaker_bound_to_down_dragent(self):
        agents = self._create_and_set_agents_down([self.host1, self.host2])
        self._schedule_bind_bgp_speaker([agents[0]], self.bgp_speaker_id)
        self._kill_bgp_dragent([self.host1])
        self.plugin.remove_bgp_speaker_from_down_dragents()
        binds = self._get_dragent_bgp_speaker_bindings(self.bgp_speaker_id)
        self.assertEqual(binds[0].agent_id, agents[1].id)

    def test_no_schedule_with_non_available_dragent(self):
        agents = self._create_and_set_agents_down([self.host1, self.host2])
        self._schedule_bind_bgp_speaker([agents[0]], self.bgp_speaker_id)
        self._kill_bgp_dragent([self.host1, self.host2])
        self.plugin.remove_bgp_speaker_from_down_dragents()
        binds = self._get_dragent_bgp_speaker_bindings(self.bgp_speaker_id)
        self.assertEqual(binds, [])

    def test_schedule_unbind_bgp_speaker(self):
        agents = self._create_and_set_agents_down([self.host1, self.host2])
        self._schedule_bind_bgp_speaker([agents[0]], self.bgp_speaker_id)
        self._kill_bgp_dragent([self.host1, self.host2])
        self.plugin.remove_bgp_speaker_from_down_dragents()
        binds = self._get_dragent_bgp_speaker_bindings(self.bgp_speaker_id)
        self.assertEqual(binds, [])
        # schedule a unbind bgp speaker
        agents = self._create_and_set_agents_down([self.host1])
        self.scheduler.schedule_all_unscheduled_bgp_speakers(self.ctx)
        binds = self._get_dragent_bgp_speaker_bindings(self.bgp_speaker_id)
        self.assertEqual(binds[0].agent_id, agents[0].id)
