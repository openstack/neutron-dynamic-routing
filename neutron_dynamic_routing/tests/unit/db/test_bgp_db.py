# Copyright 2016 Hewlett Packard Enterprise Development Company LP
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

import contextlib
from unittest import mock

import netaddr
from neutron.db import l3_dvr_ha_scheduler_db
from neutron.tests.unit.extensions import test_l3
from neutron.tests.unit.plugins.ml2 import test_plugin
from neutron_lib.api import attributes
from neutron_lib.api.definitions import external_net
from neutron_lib.api.definitions import network_ha
from neutron_lib.api.definitions import portbindings
from neutron_lib import constants as n_const
from neutron_lib import exceptions as n_exc
from neutron_lib.plugins import constants as plugin_constants
from neutron_lib.plugins import directory
from oslo_config import cfg
from oslo_utils import uuidutils

from neutron_dynamic_routing.extensions import bgp
from neutron_dynamic_routing.services.bgp import bgp_plugin

_uuid = uuidutils.generate_uuid

ADVERTISE_FIPS_KEY = 'advertise_floating_ip_host_routes'
IMAGINARY = '2b2334c8-adfe-42d9-82c6-ad866c7fc5d8'  # non existent resource id


class TestL3Plugin(test_l3.TestL3NatAgentSchedulingServicePlugin,
                   l3_dvr_ha_scheduler_db.L3_DVR_HA_scheduler_db_mixin):
    pass


class BgpEntityCreationMixin(object):

    @contextlib.contextmanager
    def bgp_speaker(self, ip_version, local_as, name='my-speaker',
                    advertise_fip_host_routes=True,
                    advertise_tenant_networks=True,
                    networks=None, peers=None):
        data = {'ip_version': ip_version,
                ADVERTISE_FIPS_KEY: advertise_fip_host_routes,
                'advertise_tenant_networks': advertise_tenant_networks,
                'local_as': local_as, 'name': name}
        bgp_speaker = self.bgp_plugin.create_bgp_speaker(self.context,
                                                        {'bgp_speaker': data})
        bgp_speaker_id = bgp_speaker['id']

        if networks:
            for network_id in networks:
                self.bgp_plugin.add_gateway_network(
                                                   self.context,
                                                   bgp_speaker_id,
                                                   {'network_id': network_id})
        if peers:
            for peer_id in peers:
                self.bgp_plugin.add_bgp_peer(self.context, bgp_speaker_id,
                                             {'bgp_peer_id': peer_id})

        yield self.bgp_plugin.get_bgp_speaker(self.context, bgp_speaker_id)

    @contextlib.contextmanager
    def bgp_peer(self, tenant_id=_uuid(), remote_as='4321',
                 peer_ip="192.168.1.1", auth_type="md5",
                 password="my-secret", name="my-peer"):
        data = {'peer_ip': peer_ip, 'tenant_id': tenant_id,
                'remote_as': remote_as, 'auth_type': auth_type,
                'password': password, 'name': name}
        bgp_peer = self.bgp_plugin.create_bgp_peer(self.context,
                                                   {'bgp_peer': data})
        yield bgp_peer
        self.bgp_plugin.delete_bgp_peer(self.context, bgp_peer['id'])

    @contextlib.contextmanager
    def bgp_speaker_with_gateway_network(self, address_scope_id, local_as,
                                         advertise_fip_host_routes=True,
                                         advertise_tenant_networks=True,
                                         network_external=True,
                                         fmt=None, set_context=False):
        pass

    @contextlib.contextmanager
    def bgp_speaker_with_router(self, address_scope_id, local_as,
                                gw_network_id=None, gw_subnet_ids=None,
                                tenant_subnet_ids=None,
                                advertise_fip_host_routes=True,
                                advertise_tenant_networks=True,
                                fmt=None, set_context=False,
                                router_distributed=False):
        pass

    @contextlib.contextmanager
    def gw_network(self, name='ext-net', external=False, **kwargs):
        with self.network(name=name, **kwargs) as gw_network:
            if external:
                self._update('networks', gw_network['network']['id'],
                             {'network': {external_net.EXTERNAL: True}},
                             as_admin=True)
            yield gw_network

    @contextlib.contextmanager
    def router(self, name='bgp-test-router', tenant_id=_uuid(),
               admin_state_up=True, **kwargs):
        request = {'router': {'tenant_id': tenant_id,
                              'name': name,
                              'admin_state_up': admin_state_up}}
        for arg in kwargs:
            request['router'][arg] = kwargs[arg]
        router = self.l3plugin.create_router(self.context, request)
        yield router

    @contextlib.contextmanager
    def router_with_external_and_tenant_networks(
                                              self,
                                              tenant_id=_uuid(),
                                              gw_prefix='8.8.8.0/24',
                                              tenant_prefix='192.168.0.0/16',
                                              address_scope=None,
                                              distributed=False,
                                              ha=False,
                                              ext_net_use_addr_scope=True,
                                              tenant_net_use_addr_scope=True):
        gw_ip_net = netaddr.IPNetwork(gw_prefix)
        tenant_ip_net = netaddr.IPNetwork(tenant_prefix)
        ext_pool_args = {'tenant_id': tenant_id,
                         'name': 'bgp-pool'}
        tenant_pool_args = ext_pool_args.copy()

        if address_scope and ext_net_use_addr_scope:
            ext_pool_args['address_scope_id'] = address_scope['id']

        if address_scope and tenant_net_use_addr_scope:
            tenant_pool_args['address_scope_id'] = address_scope['id']

        with self.gw_network(external=True) as ext_net,\
            self.network() as int_net,\
            self.subnetpool([gw_prefix], **ext_pool_args) as ext_pool,\
            self.subnetpool([tenant_prefix], **tenant_pool_args) as int_pool:
            ext_subnetpool_id = ext_pool['subnetpool']['id']
            int_subnetpool_id = int_pool['subnetpool']['id']
            gw_net_id = ext_net['network']['id']
            with self.subnet(ext_net,
                             cidr=gw_prefix,
                             subnetpool_id=ext_subnetpool_id,
                             ip_version=gw_ip_net.version,
                             as_admin=True),\
                self.subnet(int_net,
                            cidr=tenant_prefix,
                            subnetpool_id=int_subnetpool_id,
                            ip_version=tenant_ip_net.version,
                            as_admin=True) as int_subnet:
                ext_gw_info = {'network_id': gw_net_id}
                with self.router(external_gateway_info=ext_gw_info,
                                 distributed=distributed,
                                 ha=ha) as router:
                    router_id = router['id']
                    router_interface_info = {'subnet_id':
                                             int_subnet['subnet']['id']}
                    self.l3plugin.add_router_interface(self.context,
                                                       router_id,
                                                       router_interface_info)
                    yield router, ext_net, int_net


class BgpTests(BgpEntityCreationMixin):
    @contextlib.contextmanager
    def subnetpool_with_address_scope(self, ip_version, prefixes=None,
                                      shared=False, admin=True,
                                      name='test-pool', is_default_pool=False,
                                      tenant_id=None, **kwargs):
        if not tenant_id:
            tenant_id = _uuid()

        scope_data = {'tenant_id': tenant_id, 'ip_version': ip_version,
                      'shared': shared, 'name': name + '-scope'}
        address_scope = self.plugin.create_address_scope(
                                                self.context,
                                                {'address_scope': scope_data})
        address_scope_id = address_scope['id']
        pool_data = {'tenant_id': tenant_id, 'shared': shared, 'name': name,
                     'address_scope_id': address_scope_id,
                     'prefixes': prefixes, 'is_default': is_default_pool}
        for key in kwargs:
            pool_data[key] = kwargs[key]

        yield self.plugin.create_subnetpool(self.context,
                                            {'subnetpool': pool_data})

    @contextlib.contextmanager
    def floatingip_from_address_scope_assoc(self, prefixes,
                                            address_scope_id,
                                            ext_prefixlen=24,
                                            int_prefixlen=24):
        pass

    def test_add_duplicate_bgp_peer_ip(self):
        peer_ip = '192.168.1.10'
        with self.bgp_peer(peer_ip=peer_ip) as peer1,\
            self.bgp_peer(peer_ip=peer_ip) as peer2,\
            self.subnetpool_with_address_scope(4,
                                               prefixes=['8.0.0.0/8']) as sp:

            with self.bgp_speaker(sp['ip_version'], 1234,
                                  peers=[peer1['id']]) as speaker:
                self.assertRaises(bgp.DuplicateBgpPeerIpException,
                                  self.bgp_plugin.add_bgp_peer,
                                  self.context, speaker['id'],
                                  {'bgp_peer_id': peer2['id']})

    def test_bgpspeaker_create(self):
        with self.subnetpool_with_address_scope(4,
                                                prefixes=['8.0.0.0/8']) as sp:
            speaker_name = 'test-speaker'
            expected_values = [('ip_version', sp['ip_version']),
                               ('name', speaker_name)]
            with self.bgp_speaker(sp['ip_version'], 1234,
                                  name=speaker_name) as bgp_speaker:
                for k, v in expected_values:
                    self.assertEqual(v, bgp_speaker[k])

    def test_bgp_speaker_list(self):
        with self.subnetpool_with_address_scope(4,
                                              prefixes=['8.0.0.0/8']) as sp1,\
            self.subnetpool_with_address_scope(4,
                                               prefixes=['9.0.0.0/8']) as sp2:
            with self.bgp_speaker(sp1['ip_version'], 1234,
                                  name='speaker1'),\
                self.bgp_speaker(sp2['ip_version'], 4321,
                                 name='speaker2'):
                speakers = self.bgp_plugin.get_bgp_speakers(self.context)
                self.assertEqual(2, len(speakers))

    def test_bgp_speaker_update_local_as(self):
        local_as_1 = 1234
        local_as_2 = 4321
        with self.subnetpool_with_address_scope(4,
                                              prefixes=['8.0.0.0/8']) as sp:
            with self.bgp_speaker(sp['ip_version'], local_as_1) as speaker:
                self.assertEqual(local_as_1, speaker['local_as'])
                new_speaker = self.bgp_plugin.update_bgp_speaker(
                                                self.context,
                                                speaker['id'],
                                                {'bgp_speaker':
                                                    {'local_as': local_as_2}})
                self.assertEqual(local_as_2, new_speaker['local_as'])

    def test_bgp_speaker_show_non_existent(self):
        self.assertRaises(bgp.BgpSpeakerNotFound,
                          self.bgp_plugin.get_bgp_speaker,
                          self.context, _uuid())

    def test_create_bgp_peer(self):
        args = {'tenant_id': _uuid(),
                'remote_as': '1111',
                'peer_ip': '10.10.10.10',
                'auth_type': 'md5'}
        with self.bgp_peer(tenant_id=args['tenant_id'],
                           remote_as=args['remote_as'],
                           peer_ip=args['peer_ip'],
                           auth_type='md5',
                           password='my-secret') as peer:
            self.assertIsNone(peer.get('password'))
            for key in args:
                self.assertEqual(args[key], peer[key])

    def test_update_bgp_peer_auth_type_none(self):
        args = {'tenant_id': _uuid(),
                'remote_as': '1111',
                'peer_ip': '10.10.10.10',
                'auth_type': 'md5'}
        with self.bgp_peer(tenant_id=args['tenant_id'],
                           remote_as=args['remote_as'],
                           peer_ip=args['peer_ip'],
                           auth_type='none',
                           name="my-peer") as peer:
            data = {'bgp_peer': {'password': "my-secret",
                                 'name': "my-peer1"}}
            self.assertRaises(bgp.BgpPeerNotAuthenticated,
                              self.bgp_plugin.update_bgp_peer,
                              self.context, peer['id'], data)

    def test_update_bgp_peer_password_none(self):
        args = {'tenant_id': _uuid(),
                'remote_as': 1111,
                'peer_ip': '10.10.10.10',
                'name': 'my-peer',
                'auth_type': 'none'}
        with self.bgp_peer(tenant_id=args['tenant_id'],
                           remote_as=args['remote_as'],
                           peer_ip=args['peer_ip'],
                           auth_type=args['auth_type'],
                           name=args['name']) as peer:
            data = {'bgp_peer': {'name': "my-peer1"}}
            updated_peer = self.bgp_plugin.update_bgp_peer(self.context,
                                                           peer['id'],
                                                           data)
            for key in args:
                if key == 'name':
                    self.assertEqual('my-peer1', updated_peer[key])
                else:
                    self.assertEqual(peer[key], updated_peer[key])

    def test_bgp_peer_show_non_existent(self):
        self.assertRaises(bgp.BgpPeerNotFound,
                          self.bgp_plugin.get_bgp_peer,
                          self.context,
                          'unreal-bgp-peer-id')

    def test_associate_bgp_peer(self):
        with self.bgp_peer() as peer,\
            self.subnetpool_with_address_scope(4,
                                               prefixes=['8.0.0.0/8']) as sp:
            with self.bgp_speaker(sp['ip_version'], 1234) as speaker:
                self.bgp_plugin.add_bgp_peer(self.context, speaker['id'],
                                             {'bgp_peer_id': peer['id']})
                new_speaker = self.bgp_plugin.get_bgp_speaker(self.context,
                                                              speaker['id'])
                self.assertIn('peers', new_speaker)
                self.assertIn(peer['id'], new_speaker['peers'])
                self.assertEqual(1, len(new_speaker['peers']))

    def test_remove_bgp_peer(self):
        with self.bgp_peer() as peer,\
            self.subnetpool_with_address_scope(4,
                                               prefixes=['8.0.0.0/8']) as sp:
            with self.bgp_speaker(sp['ip_version'], 1234,
                                  peers=[peer['id']]) as speaker:
                self.bgp_plugin.remove_bgp_peer(self.context, speaker['id'],
                                                {'bgp_peer_id': peer['id']})
                new_speaker = self.bgp_plugin.get_bgp_speaker(self.context,
                                                              speaker['id'])
                self.assertIn('peers', new_speaker)
                self.assertTrue(not new_speaker['peers'])

    def test_remove_unassociated_bgp_peer(self):
        with self.bgp_peer() as peer,\
            self.subnetpool_with_address_scope(4,
                                               prefixes=['8.0.0.0/8']) as sp:
            with self.bgp_speaker(sp['ip_version'], 1234) as speaker:
                self.assertRaises(bgp.BgpSpeakerPeerNotAssociated,
                                  self.bgp_plugin.remove_bgp_peer,
                                  self.context,
                                  speaker['id'],
                                  {'bgp_peer_id': peer['id']})

    def test_remove_non_existent_bgp_peer(self):
        bgp_peer_id = IMAGINARY
        with self.subnetpool_with_address_scope(4,
                                                prefixes=['8.0.0.0/8']) as sp:
            with self.bgp_speaker(sp['ip_version'], 1234) as speaker:
                self.assertRaises(bgp.BgpSpeakerPeerNotAssociated,
                                  self.bgp_plugin.remove_bgp_peer,
                                  self.context,
                                  speaker['id'],
                                  {'bgp_peer_id': bgp_peer_id})

    def test_add_non_existent_bgp_peer(self):
        bgp_peer_id = IMAGINARY
        with self.subnetpool_with_address_scope(4,
                                                prefixes=['8.0.0.0/8']) as sp:
            with self.bgp_speaker(sp['ip_version'], 1234) as speaker:
                self.assertRaises(bgp.BgpPeerNotFound,
                                  self.bgp_plugin.add_bgp_peer,
                                  self.context,
                                  speaker['id'],
                                  {'bgp_peer_id': bgp_peer_id})

    def test_add_bgp_peer_without_id(self):
        with self.subnetpool_with_address_scope(4,
                                                prefixes=['8.0.0.0/8']) as sp:
            with self.bgp_speaker(sp['ip_version'], 1234) as speaker:
                self.assertRaises(n_exc.BadRequest,
                                  self.bgp_plugin.add_bgp_peer,
                                  self.context,
                                  speaker['id'],
                                  {})

    def test_add_bgp_peer_with_bad_id(self):
        with self.subnetpool_with_address_scope(4,
                                                prefixes=['8.0.0.0/8']) as sp:
            with self.bgp_speaker(sp['ip_version'], 1234) as speaker:
                self.assertRaises(n_exc.BadRequest,
                                  self.bgp_plugin.add_bgp_peer,
                                  self.context,
                                  speaker['id'],
                                  {'bgp_peer_id': 'aaa'})

    def test_add_bgp_peer_with_none_id(self):
        with self.subnetpool_with_address_scope(4,
                                                prefixes=['8.0.0.0/8']) as sp:
            with self.bgp_speaker(sp['ip_version'], 1234) as speaker:
                self.assertRaises(n_exc.BadRequest,
                                  self.bgp_plugin.add_bgp_peer,
                                  self.context,
                                  speaker['id'],
                                  {'bgp_peer_id': None})

    def test_add_gateway_network(self):
        with self.subnetpool_with_address_scope(4,
                                                prefixes=['8.0.0.0/8']) as sp:
            with self.bgp_speaker(sp['ip_version'], 1234) as speaker,\
                self.gw_network() as network:
                network_id = network['network']['id']
                self.bgp_plugin.add_gateway_network(self.context,
                                                   speaker['id'],
                                                   {'network_id': network_id})
                new_speaker = self.bgp_plugin.get_bgp_speaker(self.context,
                                                              speaker['id'])
                self.assertEqual(1, len(new_speaker['networks']))
                self.assertTrue(network_id in new_speaker['networks'])

    def test_create_bgp_speaker_with_network(self):
        with self.subnetpool_with_address_scope(4,
                                                prefixes=['8.0.0.0/8']) as sp,\
            self.gw_network(name='test-net', tenant_id=_uuid(),
                            shared=True, as_admin=True) as network:
            network_id = network['network']['id']
            with self.bgp_speaker(sp['ip_version'], 1234,
                                  networks=[network_id]) as speaker:
                self.assertEqual(1, len(speaker['networks']))
                self.assertTrue(network_id in speaker['networks'])

    def test_remove_gateway_network(self):
        with self.gw_network() as network1,\
            self.gw_network() as network2,\
            self.subnetpool_with_address_scope(4,
                                               prefixes=['8.0.0.0/8']) as sp:
            network1_id = network1['network']['id']
            network2_id = network2['network']['id']
            with self.bgp_speaker(sp['ip_version'], 1234,
                              networks=[network1_id, network2_id]) as speaker:
                self.bgp_plugin.remove_gateway_network(
                                                self.context,
                                                speaker['id'],
                                                {'network_id': network1_id})
                new_speaker = self.bgp_plugin.get_bgp_speaker(self.context,
                                                              speaker['id'])
                self.assertEqual(1, len(new_speaker['networks']))

    def test_add_non_existent_gateway_network(self):
        network_id = IMAGINARY
        with self.subnetpool_with_address_scope(4,
                                                prefixes=['8.0.0.0/8']) as sp:
            with self.bgp_speaker(sp['ip_version'], 1234) as speaker:
                self.assertRaises(n_exc.NetworkNotFound,
                                  self.bgp_plugin.add_gateway_network,
                                  self.context, speaker['id'],
                                  {'network_id': network_id})

    def test_remove_non_existent_gateway_network(self):
        network_id = IMAGINARY
        with self.subnetpool_with_address_scope(4,
                                                prefixes=['8.0.0.0/8']) as sp:
            with self.bgp_speaker(sp['ip_version'], 1234) as speaker:
                self.assertRaises(bgp.BgpSpeakerNetworkNotAssociated,
                                  self.bgp_plugin.remove_gateway_network,
                                  self.context, speaker['id'],
                                  {'network_id': network_id})

    def test_add_gateway_network_two_bgp_speakers_same_scope(self):
        with self.subnetpool_with_address_scope(4,
                                                prefixes=['8.0.0.0/8']) as sp:
            with self.bgp_speaker(sp['ip_version'], 1234) as speaker1,\
                self.bgp_speaker(sp['ip_version'], 4321) as speaker2,\
                self.gw_network() as network:
                network_id = network['network']['id']
                self.bgp_plugin.add_gateway_network(self.context,
                                                   speaker1['id'],
                                                   {'network_id': network_id})
                self.bgp_plugin.add_gateway_network(self.context,
                                                   speaker2['id'],
                                                   {'network_id': network_id})
                speaker1 = self.bgp_plugin.get_bgp_speaker(self.context,
                                                           speaker1['id'])
                speaker2 = self.bgp_plugin.get_bgp_speaker(self.context,
                                                           speaker2['id'])
                for speaker in [speaker1, speaker2]:
                    self.assertEqual(1, len(speaker['networks']))
                    self.assertEqual(network_id,
                                     speaker['networks'][0])

    def test_create_bgp_peer_md5_auth_no_password(self):
        bgp_peer = {'bgp_peer': {'auth_type': 'md5', 'password': None}}
        self.assertRaises(bgp.InvalidBgpPeerMd5Authentication,
                          self.bgp_plugin.create_bgp_peer,
                          self.context, bgp_peer)

    def test__get_address_scope_ids_for_bgp_speaker(self):
        prefixes1 = ['8.0.0.0/8']
        prefixes2 = ['9.0.0.0/8']
        prefixes3 = ['10.0.0.0/8']
        tenant_id = _uuid()
        with self.bgp_speaker(4, 1234) as speaker,\
            self.subnetpool_with_address_scope(4,
                                               prefixes=prefixes1,
                                               tenant_id=tenant_id) as sp1,\
            self.subnetpool_with_address_scope(4,
                                               prefixes=prefixes2,
                                               tenant_id=tenant_id) as sp2,\
            self.subnetpool_with_address_scope(4,
                                               prefixes=prefixes3,
                                               tenant_id=tenant_id) as sp3,\
            self.gw_network() as network1, self.gw_network() as network2,\
            self.gw_network() as network3:
            network1_id = network1['network']['id']
            network2_id = network2['network']['id']
            network3_id = network3['network']['id']
            base_subnet_data = {
                'allocation_pools': n_const.ATTR_NOT_SPECIFIED,
                'cidr': n_const.ATTR_NOT_SPECIFIED,
                'prefixlen': n_const.ATTR_NOT_SPECIFIED,
                'ip_version': 4,
                'enable_dhcp': True,
                'dns_nameservers': n_const.ATTR_NOT_SPECIFIED,
                'host_routes': n_const.ATTR_NOT_SPECIFIED}
            subnet1_data = {'network_id': network1_id,
                            'subnetpool_id': sp1['id'],
                            'name': 'subnet1',
                            'tenant_id': tenant_id}
            subnet2_data = {'network_id': network2_id,
                            'subnetpool_id': sp2['id'],
                            'name': 'subnet2',
                            'tenant_id': tenant_id}
            subnet3_data = {'network_id': network3_id,
                            'subnetpool_id': sp3['id'],
                            'name': 'subnet2',
                            'tenant_id': tenant_id}
            for k in base_subnet_data:
                subnet1_data[k] = base_subnet_data[k]
                subnet2_data[k] = base_subnet_data[k]
                subnet3_data[k] = base_subnet_data[k]

            self.plugin.create_subnet(self.context, {'subnet': subnet1_data})
            self.plugin.create_subnet(self.context, {'subnet': subnet2_data})
            self.plugin.create_subnet(self.context, {'subnet': subnet3_data})
            self.bgp_plugin.add_gateway_network(self.context, speaker['id'],
                                            {'network_id': network1_id})
            self.bgp_plugin.add_gateway_network(self.context, speaker['id'],
                                            {'network_id': network2_id})
            scopes = self.bgp_plugin._get_address_scope_ids_for_bgp_speaker(
                                                                self.context,
                                                                speaker['id'])
            self.assertEqual(2, len(scopes))
            self.assertTrue(sp1['address_scope_id'] in scopes)
            self.assertTrue(sp2['address_scope_id'] in scopes)

    def test_get_routes_by_bgp_speaker_binding(self):
        gw_prefix = '172.16.10.0/24'
        tenant_prefix = '10.10.10.0/24'
        tenant_id = _uuid()
        scope_data = {'tenant_id': tenant_id, 'ip_version': 4,
                      'shared': True, 'name': 'bgp-scope'}
        scope = self.plugin.create_address_scope(
                                                self.context,
                                                {'address_scope': scope_data})
        with self.router_with_external_and_tenant_networks(
                                               tenant_id=tenant_id,
                                               gw_prefix=gw_prefix,
                                               tenant_prefix=tenant_prefix,
                                               address_scope=scope) as res:
            router, ext_net, int_net = res
            ext_gw_info = router['external_gateway_info']
            gw_net_id = ext_net['network']['id']
            with self.bgp_speaker(4, 1234,
                                  networks=[gw_net_id]) as speaker:
                bgp_speaker_id = speaker['id']
                routes = self.bgp_plugin.get_routes_by_bgp_speaker_binding(
                                                              self.context,
                                                              bgp_speaker_id,
                                                              gw_net_id)
                routes = list(routes)
                next_hop = ext_gw_info['external_fixed_ips'][0]['ip_address']
                self.assertEqual(1, len(routes))
                self.assertEqual(tenant_prefix, routes[0]['destination'])
                self.assertEqual(next_hop, routes[0]['next_hop'])

    def test_get_routes_by_binding_network(self):
        gw_prefix = '172.16.10.0/24'
        tenant_prefix = '10.10.10.0/24'
        tenant_id = _uuid()
        scope_data = {'tenant_id': tenant_id, 'ip_version': 4,
                      'shared': True, 'name': 'bgp-scope'}
        scope = self.plugin.create_address_scope(
                                                self.context,
                                                {'address_scope': scope_data})
        with self.router_with_external_and_tenant_networks(
                                               tenant_id=tenant_id,
                                               gw_prefix=gw_prefix,
                                               tenant_prefix=tenant_prefix,
                                               address_scope=scope) as res:
            router, ext_net, int_net = res
            ext_gw_info = router['external_gateway_info']
            gw_net_id = ext_net['network']['id']
            with self.bgp_speaker(4, 1234, networks=[gw_net_id]) as speaker:
                bgp_speaker_id = speaker['id']
                routes = self.bgp_plugin.get_routes_by_bgp_speaker_binding(
                                                               self.context,
                                                               bgp_speaker_id,
                                                               gw_net_id)
                routes = list(routes)
                next_hop = ext_gw_info['external_fixed_ips'][0]['ip_address']
                self.assertEqual(1, len(routes))
                self.assertEqual(tenant_prefix, routes[0]['destination'])
                self.assertEqual(next_hop, routes[0]['next_hop'])

    def _advertised_routes_by_bgp_speaker(self,
                                      bgp_speaker_ip_version,
                                      local_as,
                                      tenant_cidr,
                                      gateway_cidr,
                                      fip_routes=True,
                                      router_distributed=False):
        tenant_id = _uuid()
        scope_data = {'tenant_id': tenant_id,
                      'ip_version': bgp_speaker_ip_version,
                      'shared': True,
                      'name': 'bgp-scope'}
        scope = self.plugin.create_address_scope(
                                                self.context,
                                                {'address_scope': scope_data})
        with self.router_with_external_and_tenant_networks(
                                    tenant_id=tenant_id,
                                    gw_prefix=gateway_cidr,
                                    tenant_prefix=tenant_cidr,
                                    address_scope=scope,
                                    distributed=router_distributed) as res:
            router, ext_net, int_net = res
            gw_net_id = ext_net['network']['id']
            with self.bgp_speaker(
                             bgp_speaker_ip_version,
                             local_as,
                             networks=[gw_net_id],
                             advertise_fip_host_routes=fip_routes) as speaker:
                routes = self.bgp_plugin.get_advertised_routes(
                    self.context, speaker['id'])
                return routes['advertised_routes']

    def test__tenant_prefixes_by_router_no_gateway_port(self):
        with self.network() as net1, self.network() as net2,\
            self.subnetpool_with_address_scope(6, tenant_id=_uuid(),
                                          prefixes=['2001:db8::/63']) as pool:
            subnetpool_id = pool['id']
            with self.subnet(network=net1,
                             cidr=None,
                             subnetpool_id=subnetpool_id,
                             ip_version=6,
                             as_admin=True) as ext_subnet,\
                self.subnet(network=net2,
                            cidr=None,
                            subnetpool_id=subnetpool_id,
                            ip_version=6,
                            as_admin=True) as int_subnet,\
                self.router() as router:

                router_id = router['id']
                int_subnet_id = int_subnet['subnet']['id']
                ext_subnet_id = ext_subnet['subnet']['id']
                self.l3plugin.add_router_interface(self.context,
                                                   router_id,
                                                   {'subnet_id':
                                                    int_subnet_id})
                self.l3plugin.add_router_interface(self.context,
                                                   router_id,
                                                   {'subnet_id':
                                                    ext_subnet_id})
                with self.bgp_speaker(6, 1234) as speaker:
                    bgp_speaker_id = speaker['id']
                    cidrs = list(self.bgp_plugin._tenant_prefixes_by_router(
                                                              self.context,
                                                              router_id,
                                                              bgp_speaker_id))
                    self.assertFalse(cidrs)

    def test_get_ipv6_tenant_subnet_routes_by_bgp_speaker_ipv6(self):
        tenant_cidr = '2001:db8::/64'
        binding_cidr = '2001:ab8::/64'
        routes = self._advertised_routes_by_bgp_speaker(6, 1234, tenant_cidr,
                                                        binding_cidr)
        self.assertEqual(1, len(routes))
        dest_prefix = routes[0]['destination']
        next_hop = routes[0]['next_hop']
        self.assertEqual(tenant_cidr, dest_prefix)
        self.assertTrue(netaddr.IPSet([binding_cidr]).__contains__(next_hop))

    def test_get_ipv4_tenant_subnet_routes_by_bgp_speaker_ipv4(self):
        tenant_cidr = '172.16.10.0/24'
        binding_cidr = '20.10.1.0/24'
        routes = self._advertised_routes_by_bgp_speaker(4, 1234, tenant_cidr,
                                                        binding_cidr)
        routes = list(routes)
        self.assertEqual(1, len(routes))
        dest_prefix = routes[0]['destination']
        next_hop = routes[0]['next_hop']
        self.assertEqual(tenant_cidr, dest_prefix)
        self.assertTrue(netaddr.IPSet([binding_cidr]).__contains__(next_hop))

    def test_get_ipv4_tenant_subnet_routes_by_bgp_speaker_dvr_router(self):
        tenant_cidr = '172.16.10.0/24'
        binding_cidr = '20.10.1.0/24'
        routes = self._advertised_routes_by_bgp_speaker(
                                                      4,
                                                      1234,
                                                      tenant_cidr,
                                                      binding_cidr,
                                                      router_distributed=True)
        routes = list(routes)
        self.assertEqual(1, len(routes))

    def test_all_routes_by_bgp_speaker_different_tenant_address_scope(self):
        binding_cidr = '2001:db8::/64'
        tenant_cidr = '2002:ab8::/64'
        with self.subnetpool_with_address_scope(6, tenant_id=_uuid(),
                                       prefixes=[binding_cidr]) as ext_pool,\
            self.subnetpool_with_address_scope(6, tenant_id=_uuid(),
                                       prefixes=[tenant_cidr]) as int_pool,\
            self.gw_network(external=True) as ext_net,\
            self.network() as int_net:
            gw_net_id = ext_net['network']['id']
            ext_pool_id = ext_pool['id']
            int_pool_id = int_pool['id']
            with self.subnet(cidr=None,
                             subnetpool_id=ext_pool_id,
                             network=ext_net,
                             ip_version=6,
                             as_admin=True) as ext_subnet,\
                self.subnet(cidr=None,
                            subnetpool_id=int_pool_id,
                            network=int_net,
                            ip_version=6,
                            as_admin=True) as int_subnet,\
                self.router() as router:
                router_id = router['id']
                int_subnet_id = int_subnet['subnet']['id']
                ext_subnet_id = ext_subnet['subnet']['id']
                self.l3plugin.add_router_interface(self.context,
                                                   router_id,
                                                   {'subnet_id':
                                                    int_subnet_id})
                self.l3plugin.add_router_interface(self.context,
                                                   router_id,
                                                   {'subnet_id':
                                                    ext_subnet_id})
                with self.bgp_speaker(6, 1234,
                                      networks=[gw_net_id]) as speaker:
                    bgp_speaker_id = speaker['id']
                    cidrs = self.bgp_plugin.get_routes_by_bgp_speaker_id(
                        self.context, bgp_speaker_id)
                    self.assertEqual(0, len(list(cidrs)))

    def test__get_routes_by_router_with_fip(self):
        gw_prefix = '172.16.10.0/24'
        tenant_prefix = '10.10.10.0/24'
        tenant_id = _uuid()
        scope_data = {'tenant_id': tenant_id, 'ip_version': 4,
                      'shared': True, 'name': 'bgp-scope'}
        scope = self.plugin.create_address_scope(
                                                self.context,
                                                {'address_scope': scope_data})
        with self.router_with_external_and_tenant_networks(
                                               tenant_id=tenant_id,
                                               gw_prefix=gw_prefix,
                                               tenant_prefix=tenant_prefix,
                                               address_scope=scope) as res:
            router, ext_net, int_net = res
            ext_gw_info = router['external_gateway_info']
            gw_net_id = ext_net['network']['id']
            tenant_net_id = int_net['network']['id']
            fixed_port_data = {'port':
                               {'name': 'test',
                                'network_id': tenant_net_id,
                                'tenant_id': tenant_id,
                                'admin_state_up': True,
                                'device_id': _uuid(),
                                'device_owner': 'compute:nova',
                                'mac_address': n_const.ATTR_NOT_SPECIFIED,
                                'fixed_ips': n_const.ATTR_NOT_SPECIFIED}}
            fixed_port = self.plugin.create_port(self.context,
                                                 fixed_port_data)
            fip_data = {'floatingip': {'floating_network_id': gw_net_id,
                                       'tenant_id': tenant_id,
                                       'port_id': fixed_port['id']}}
            fip = self.l3plugin.create_floatingip(self.context, fip_data)
            fip_prefix = fip['floating_ip_address'] + '/32'
            with self.bgp_speaker(4, 1234, networks=[gw_net_id]) as speaker:
                bgp_speaker_id = speaker['id']
                routes = self.bgp_plugin._get_routes_by_router(self.context,
                                                               router['id'])
                routes = routes[bgp_speaker_id]
                next_hop = ext_gw_info['external_fixed_ips'][0]['ip_address']
                self.assertEqual(2, len(routes))
                tenant_prefix_found = False
                fip_prefix_found = False
                for route in routes:
                    self.assertEqual(next_hop, route['next_hop'])
                    if route['destination'] == tenant_prefix:
                        tenant_prefix_found = True
                    if route['destination'] == fip_prefix:
                        fip_prefix_found = True
                self.assertTrue(tenant_prefix_found)
                self.assertTrue(fip_prefix_found)

    def test_get_routes_by_bgp_speaker_id_with_fip(self):
        gw_prefix = '172.16.10.0/24'
        tenant_prefix = '10.10.10.0/24'
        tenant_id = _uuid()
        scope_data = {'tenant_id': tenant_id, 'ip_version': 4,
                      'shared': True, 'name': 'bgp-scope'}
        scope = self.plugin.create_address_scope(
                                                self.context,
                                                {'address_scope': scope_data})
        with self.router_with_external_and_tenant_networks(
                                               tenant_id=tenant_id,
                                               gw_prefix=gw_prefix,
                                               tenant_prefix=tenant_prefix,
                                               address_scope=scope) as res:
            router, ext_net, int_net = res
            ext_gw_info = router['external_gateway_info']
            gw_net_id = ext_net['network']['id']
            tenant_net_id = int_net['network']['id']
            fixed_port_data = {'port':
                               {'name': 'test',
                                'network_id': tenant_net_id,
                                'tenant_id': tenant_id,
                                'admin_state_up': True,
                                'device_id': _uuid(),
                                'device_owner': 'compute:nova',
                                'mac_address': n_const.ATTR_NOT_SPECIFIED,
                                'fixed_ips': n_const.ATTR_NOT_SPECIFIED}}
            fixed_port = self.plugin.create_port(self.context,
                                                 fixed_port_data)
            fip_data = {'floatingip': {'floating_network_id': gw_net_id,
                                       'tenant_id': tenant_id,
                                       'port_id': fixed_port['id']}}
            fip = self.l3plugin.create_floatingip(self.context, fip_data)
            fip_prefix = fip['floating_ip_address'] + '/32'
            with self.bgp_speaker(4, 1234, networks=[gw_net_id]) as speaker:
                bgp_speaker_id = speaker['id']
                routes = self.bgp_plugin.get_routes_by_bgp_speaker_id(
                                                               self.context,
                                                               bgp_speaker_id)
                routes = list(routes)
                next_hop = ext_gw_info['external_fixed_ips'][0]['ip_address']
                self.assertEqual(2, len(routes))
                tenant_prefix_found = False
                fip_prefix_found = False
                for route in routes:
                    self.assertEqual(next_hop, route['next_hop'])
                    if route['destination'] == tenant_prefix:
                        tenant_prefix_found = True
                    if route['destination'] == fip_prefix:
                        fip_prefix_found = True
                self.assertTrue(tenant_prefix_found)
                self.assertTrue(fip_prefix_found)

    def test_get_routes_by_bgp_speaker_id_with_fip_dvr(self):
        gw_prefix = '172.16.10.0/24'
        tenant_prefix = '10.10.10.0/24'
        tenant_id = _uuid()
        scope_data = {'tenant_id': tenant_id, 'ip_version': 4,
                      'shared': True, 'name': 'bgp-scope'}
        scope = self.plugin.create_address_scope(
                                                self.context,
                                                {'address_scope': scope_data})
        with self.router_with_external_and_tenant_networks(
                                               tenant_id=tenant_id,
                                               gw_prefix=gw_prefix,
                                               tenant_prefix=tenant_prefix,
                                               address_scope=scope,
                                               distributed=True) as res:
            router, ext_net, int_net = res
            ext_gw_info = router['external_gateway_info']
            gw_net_id = ext_net['network']['id']
            tenant_net_id = int_net['network']['id']
            fixed_port_data = {'port':
                               {'name': 'test',
                                'network_id': tenant_net_id,
                                'tenant_id': tenant_id,
                                'admin_state_up': True,
                                'device_id': _uuid(),
                                'device_owner': 'compute:nova',
                                'mac_address': n_const.ATTR_NOT_SPECIFIED,
                                'fixed_ips': n_const.ATTR_NOT_SPECIFIED,
                                portbindings.HOST_ID: 'test-host'}}
            fixed_port = self.plugin.create_port(self.context,
                                                 fixed_port_data)
            self.plugin.create_or_update_agent(self.context,
                                               {'agent_type': 'L3 agent',
                                                'host': 'test-host',
                                                'binary': 'neutron-l3-agent',
                                                'topic': 'test'})
            fip_gw = self.l3plugin.create_fip_agent_gw_port_if_not_exists(
                                                                 self.context,
                                                                 gw_net_id,
                                                                 'test-host')
            fip_data = {'floatingip': {'floating_network_id': gw_net_id,
                                       'tenant_id': tenant_id,
                                       'port_id': fixed_port['id']}}
            fip = self.l3plugin.create_floatingip(self.context, fip_data)
            fip_prefix = fip['floating_ip_address'] + '/32'
            fixed_prefix = fixed_port['fixed_ips'][0]['ip_address'] + '/32'
            with self.bgp_speaker(4, 1234, networks=[gw_net_id]) as speaker:
                bgp_speaker_id = speaker['id']
                routes = self.bgp_plugin.get_routes_by_bgp_speaker_id(
                                                               self.context,
                                                               bgp_speaker_id)
                routes = list(routes)
                cvr_gw_ip = ext_gw_info['external_fixed_ips'][0]['ip_address']
                dvr_gw_ip = fip_gw['fixed_ips'][0]['ip_address']
                self.assertEqual(3, len(routes))
                tenant_route_verified = False
                fip_route_verified = False
                fixed_ip_route_verified = False
                for route in routes:
                    if route['destination'] == tenant_prefix:
                        self.assertEqual(cvr_gw_ip, route['next_hop'])
                        tenant_route_verified = True
                    if route['destination'] == fip_prefix:
                        self.assertEqual(dvr_gw_ip, route['next_hop'])
                        fip_route_verified = True
                    if route['destination'] == fixed_prefix:
                        self.assertEqual(dvr_gw_ip, route['next_hop'])
                        fixed_ip_route_verified = True
                self.assertTrue(tenant_route_verified)
                self.assertTrue(fip_route_verified)
                self.assertTrue(fixed_ip_route_verified)

    def test__get_dvr_fip_host_routes_by_binding(self):
        gw_prefix = '172.16.10.0/24'
        tenant_prefix = '10.10.10.0/24'
        tenant_id = _uuid()
        scope_data = {'tenant_id': tenant_id, 'ip_version': 4,
                      'shared': True, 'name': 'bgp-scope'}
        scope = self.plugin.create_address_scope(
                                                self.context,
                                                {'address_scope': scope_data})
        with self.router_with_external_and_tenant_networks(
                                               tenant_id=tenant_id,
                                               gw_prefix=gw_prefix,
                                               tenant_prefix=tenant_prefix,
                                               address_scope=scope,
                                               distributed=True) as res:
            router, ext_net, int_net = res
            gw_net_id = ext_net['network']['id']
            tenant_net_id = int_net['network']['id']
            fixed_port_data = {'port':
                               {'name': 'test',
                                'network_id': tenant_net_id,
                                'tenant_id': tenant_id,
                                'admin_state_up': True,
                                'device_id': _uuid(),
                                'device_owner': 'compute:nova',
                                'mac_address': n_const.ATTR_NOT_SPECIFIED,
                                'fixed_ips': n_const.ATTR_NOT_SPECIFIED,
                                portbindings.HOST_ID: 'test-host'}}
            fixed_port = self.plugin.create_port(self.context,
                                                 fixed_port_data)
            self.plugin.create_or_update_agent(self.context,
                                               {'agent_type': 'L3 agent',
                                                'host': 'test-host',
                                                'binary': 'neutron-l3-agent',
                                                'topic': 'test'})
            fip_gw = self.l3plugin.create_fip_agent_gw_port_if_not_exists(
                                                                 self.context,
                                                                 gw_net_id,
                                                                 'test-host')
            fip_data = {'floatingip': {'floating_network_id': gw_net_id,
                                       'tenant_id': tenant_id,
                                       'port_id': fixed_port['id']}}
            fip = self.l3plugin.create_floatingip(self.context, fip_data)
            fip_prefix = fip['floating_ip_address'] + '/32'
            with self.bgp_speaker(4, 1234, networks=[gw_net_id]) as speaker:
                bgp_speaker_id = speaker['id']
                routes = self.bgp_plugin._get_dvr_fip_host_routes_by_binding(
                                                               self.context,
                                                               gw_net_id,
                                                               bgp_speaker_id)
                routes = list(routes)
                dvr_gw_ip = fip_gw['fixed_ips'][0]['ip_address']
                self.assertEqual(1, len(routes))
                self.assertEqual(dvr_gw_ip, routes[0]['next_hop'])
                self.assertEqual(fip_prefix, routes[0]['destination'])

    def test__get_dvr_fip_host_routes_by_router(self):
        gw_prefix = '172.16.10.0/24'
        tenant_prefix = '10.10.10.0/24'
        tenant_id = _uuid()
        scope_data = {'tenant_id': tenant_id, 'ip_version': 4,
                      'shared': True, 'name': 'bgp-scope'}
        scope = self.plugin.create_address_scope(
                                                self.context,
                                                {'address_scope': scope_data})
        with self.router_with_external_and_tenant_networks(
                                               tenant_id=tenant_id,
                                               gw_prefix=gw_prefix,
                                               tenant_prefix=tenant_prefix,
                                               address_scope=scope,
                                               distributed=True) as res:
            router, ext_net, int_net = res
            gw_net_id = ext_net['network']['id']
            tenant_net_id = int_net['network']['id']
            fixed_port_data = {'port':
                               {'name': 'test',
                                'network_id': tenant_net_id,
                                'tenant_id': tenant_id,
                                'admin_state_up': True,
                                'device_id': _uuid(),
                                'device_owner': 'compute:nova',
                                'mac_address': n_const.ATTR_NOT_SPECIFIED,
                                'fixed_ips': n_const.ATTR_NOT_SPECIFIED,
                                portbindings.HOST_ID: 'test-host'}}
            fixed_port = self.plugin.create_port(self.context,
                                                 fixed_port_data)
            self.plugin.create_or_update_agent(self.context,
                                               {'agent_type': 'L3 agent',
                                                'host': 'test-host',
                                                'binary': 'neutron-l3-agent',
                                                'topic': 'test'})
            fip_gw = self.l3plugin.create_fip_agent_gw_port_if_not_exists(
                                                                 self.context,
                                                                 gw_net_id,
                                                                 'test-host')
            fip_data = {'floatingip': {'floating_network_id': gw_net_id,
                                       'tenant_id': tenant_id,
                                       'port_id': fixed_port['id']}}
            fip = self.l3plugin.create_floatingip(self.context, fip_data)
            fip_prefix = fip['floating_ip_address'] + '/32'
            with self.bgp_speaker(4, 1234, networks=[gw_net_id]) as speaker:
                bgp_speaker_id = speaker['id']
                routes = self.bgp_plugin._get_dvr_fip_host_routes_by_router(
                                                               self.context,
                                                               bgp_speaker_id,
                                                               router['id'])
                routes = list(routes)
                dvr_gw_ip = fip_gw['fixed_ips'][0]['ip_address']
                self.assertEqual(1, len(routes))
                self.assertEqual(dvr_gw_ip, routes[0]['next_hop'])
                self.assertEqual(fip_prefix, routes[0]['destination'])

    def test_get_routes_by_bgp_speaker_binding_with_fip(self):
        gw_prefix = '172.16.10.0/24'
        tenant_prefix = '10.10.10.0/24'
        tenant_id = _uuid()
        scope_data = {'tenant_id': tenant_id, 'ip_version': 4,
                      'shared': True, 'name': 'bgp-scope'}
        scope = self.plugin.create_address_scope(
                                                self.context,
                                                {'address_scope': scope_data})
        with self.router_with_external_and_tenant_networks(
                                               tenant_id=tenant_id,
                                               gw_prefix=gw_prefix,
                                               tenant_prefix=tenant_prefix,
                                               address_scope=scope) as res:
            router, ext_net, int_net = res
            ext_gw_info = router['external_gateway_info']
            gw_net_id = ext_net['network']['id']
            tenant_net_id = int_net['network']['id']
            fixed_port_data = {'port':
                               {'name': 'test',
                                'network_id': tenant_net_id,
                                'tenant_id': tenant_id,
                                'admin_state_up': True,
                                'device_id': _uuid(),
                                'device_owner': 'compute:nova',
                                'mac_address': n_const.ATTR_NOT_SPECIFIED,
                                'fixed_ips': n_const.ATTR_NOT_SPECIFIED}}
            fixed_port = self.plugin.create_port(self.context,
                                                 fixed_port_data)
            fip_data = {'floatingip': {'floating_network_id': gw_net_id,
                                       'tenant_id': tenant_id,
                                       'port_id': fixed_port['id']}}
            fip = self.l3plugin.create_floatingip(self.context, fip_data)
            fip_prefix = fip['floating_ip_address'] + '/32'
            with self.bgp_speaker(4, 1234, networks=[gw_net_id]) as speaker:
                bgp_speaker_id = speaker['id']
                routes = self.bgp_plugin.get_routes_by_bgp_speaker_binding(
                                                               self.context,
                                                               bgp_speaker_id,
                                                               gw_net_id)
                routes = list(routes)
                next_hop = ext_gw_info['external_fixed_ips'][0]['ip_address']
                self.assertEqual(2, len(routes))
                tenant_prefix_found = False
                fip_prefix_found = False
                for route in routes:
                    self.assertEqual(next_hop, route['next_hop'])
                    if route['destination'] == tenant_prefix:
                        tenant_prefix_found = True
                    if route['destination'] == fip_prefix:
                        fip_prefix_found = True
                self.assertTrue(tenant_prefix_found)
                self.assertTrue(fip_prefix_found)

    def test__bgp_speakers_for_gateway_network_by_ip_version(self):
        with self.gw_network(external=True) as ext_net,\
            self.bgp_speaker(6, 1234) as s1,\
            self.bgp_speaker(6, 4321) as s2:
            gw_net_id = ext_net['network']['id']
            self.bgp_plugin.add_gateway_network(self.context,
                                                s1['id'],
                                                {'network_id': gw_net_id})
            self.bgp_plugin.add_gateway_network(self.context,
                                                s2['id'],
                                                {'network_id': gw_net_id})
            speakers = self.bgp_plugin._bgp_speakers_for_gw_network_by_family(
                                                                 self.context,
                                                                 gw_net_id,
                                                                 6)
            self.assertEqual(2, len(speakers))

    def test__bgp_speakers_for_gateway_network_by_ip_version_no_binding(self):
        with self.gw_network(external=True) as ext_net,\
            self.bgp_speaker(6, 1234),\
            self.bgp_speaker(6, 4321):
            gw_net_id = ext_net['network']['id']
            speakers = self.bgp_plugin._bgp_speakers_for_gw_network_by_family(
                                                                 self.context,
                                                                 gw_net_id,
                                                                 6)
            self.assertTrue(not speakers)

    def _create_scenario_test_l3_agents(self, agent_confs):
        for item in agent_confs:
            self.plugin.create_or_update_agent(
                self.context,
                {'agent_type': 'L3 agent',
                 'host': item['host'],
                 'binary': 'neutron-l3-agent',
                 'topic': 'test',
                 'configurations': {"agent_mode": item['mode']}})

    def _create_scenario_test_ports(self, tenant_id, port_configs):
        ports = []
        for item in port_configs:
            port_data = {
                'port': {'name': 'test1',
                         'network_id': item['net_id'],
                         'tenant_id': tenant_id,
                         'admin_state_up': True,
                         'device_id': _uuid(),
                         'device_owner': 'compute:nova',
                         'mac_address': n_const.ATTR_NOT_SPECIFIED,
                         'fixed_ips': n_const.ATTR_NOT_SPECIFIED,
                         portbindings.HOST_ID: item['host']}}
            port = self.plugin.create_port(self.context, port_data)
            ports.append(port)
        return ports

    def _create_scenario_test_fips(self, ext_net_id,
                                   tenant_id, port_ids):
        fips = []
        for port_id in port_ids:
            fip_data = {'floatingip': {'floating_network_id': ext_net_id,
                                       'tenant_id': tenant_id,
                                       'port_id': port_id}}
            fip = self.l3plugin.create_floatingip(self.context, fip_data)
            fips.append(fip)
        return fips

    def test_floatingip_update_callback(self):
        gw_prefix = '172.16.10.0/24'
        tenant_prefix = '10.10.10.0/24'
        tenant_id = _uuid()
        agent_confs = [{"host": "network1", "mode": "legacy"}]
        self._create_scenario_test_l3_agents(agent_confs)
        with self.router_with_external_and_tenant_networks(
                tenant_id=tenant_id,
                gw_prefix=gw_prefix,
                tenant_prefix=tenant_prefix) as res:
            router, ext_net, int_net = res
            gw_net_id = ext_net['network']['id']
            ext_gw_info = router['external_gateway_info']
            next_hop = ext_gw_info[
                'external_fixed_ips'][0]['ip_address']

            port_configs = [{'net_id': int_net['network']['id'],
                             'host': 'compute1'}]
            ports = self._create_scenario_test_ports(tenant_id, port_configs)
            port_ids = [port['id'] for port in ports]
            with self.bgp_speaker(4, 1234, networks=[gw_net_id]) as speaker:
                with mock.patch.object(
                    self.bgp_plugin,
                    'start_route_advertisements') as start_adv:
                    with mock.patch.object(
                        self.bgp_plugin,
                        'stop_route_advertisements') as stop_adv:
                        bgp_speaker_id = speaker['id']
                        # Create and associate floating IP
                        fips = self._create_scenario_test_fips(
                            gw_net_id, tenant_id, port_ids)
                        fip_id = fips[0]['id']
                        fip_addr = fips[0]['floating_ip_address']
                        host_route = {'destination': fip_addr + '/32',
                                      'next_hop': next_hop}
                        start_adv.assert_called_once_with(
                            mock.ANY,
                            mock.ANY,
                            bgp_speaker_id,
                            [host_route])
                        fip_data = {'floatingip': {'port_id': None}}
                        fip = self.l3plugin.update_floatingip(
                            self.context,
                            fip_id,
                            fip_data)
                        self.assertIsNone(fip['port_id'])
                        # Dissociate floating IP,
                        # withdraw route with next_hop None
                        host_route['next_hop'] = None
                        stop_adv.assert_called_once_with(
                            mock.ANY,
                            mock.ANY,
                            bgp_speaker_id,
                            [host_route])

    def _test_legacy_router_fips_next_hop(self, router_ha=False):
        if router_ha:
            cfg.CONF.set_override('l3_ha', True)
            cfg.CONF.set_override('max_l3_agents_per_router', 2)
        gw_prefix = '172.16.10.0/24'
        tenant_prefix = '10.10.10.0/24'
        tenant_id = _uuid()

        agent_confs = [{"host": "compute1", "mode": "dvr"},
                       {"host": "compute2", "mode": "dvr"},
                       {"host": "network1", "mode": "dvr_snat"}]
        if router_ha:
            agent_confs.append({"host": "network2", "mode": "dvr_snat"})

        self._create_scenario_test_l3_agents(agent_confs)
        with self.router_with_external_and_tenant_networks(
                tenant_id=tenant_id,
                gw_prefix=gw_prefix,
                tenant_prefix=tenant_prefix,
                ha=router_ha) as res:
            router, ext_net, int_net = res
            gw_net_id = ext_net['network']['id']
            ext_gw_info = router['external_gateway_info']

            self.l3plugin.create_fip_agent_gw_port_if_not_exists(
                self.context, gw_net_id, 'compute1')
            self.l3plugin.create_fip_agent_gw_port_if_not_exists(
                self.context, gw_net_id, 'compute2')

            port_configs = [{'net_id': int_net['network']['id'],
                             'host': 'compute1'},
                            {'net_id': int_net['network']['id'],
                             'host': 'compute2'}]
            ports = self._create_scenario_test_ports(tenant_id, port_configs)
            port_ids = [port['id'] for port in ports]
            self._create_scenario_test_fips(gw_net_id, tenant_id, port_ids)

            next_hop = ext_gw_info[
                'external_fixed_ips'][0]['ip_address']
            with self.bgp_speaker(4, 1234, networks=[gw_net_id]) as speaker:
                bgp_speaker_id = speaker['id']
                routes = self.bgp_plugin.get_routes_by_bgp_speaker_id(
                    self.context, bgp_speaker_id)
                routes = list(routes)
                self.assertEqual(2, len(routes))
                for route in routes:
                    self.assertEqual(next_hop, route['next_hop'])

    def test_legacy_router_fips_has_no_next_hop_to_fip_agent_gateway(self):
        self._test_legacy_router_fips_next_hop()

    def test_ha_router_fips_has_no_next_hop_to_fip_agent_gateway(self):
        self._test_legacy_router_fips_next_hop(router_ha=True)

    def _test__get_fip_next_hop(self, distributed=False):
        gw_prefix = '172.16.10.0/24'
        tenant_prefix = '10.10.10.0/24'
        tenant_id = _uuid()
        agent_confs = [{"host": "compute1", "mode": "dvr"},
                       {"host": "network1", "mode": "dvr_snat"}]
        self._create_scenario_test_l3_agents(agent_confs)
        with self.router_with_external_and_tenant_networks(
                tenant_id=tenant_id,
                gw_prefix=gw_prefix,
                tenant_prefix=tenant_prefix,
                distributed=distributed) as res:
            router, ext_net, int_net = res
            ext_gw_info = router['external_gateway_info']
            legacy_gw_ip = ext_gw_info[
                'external_fixed_ips'][0]['ip_address']
            gw_net_id = ext_net['network']['id']
            # Whatever the router type is, we always create such dvr fip agent
            # gateway port, in order to make sure that legacy router fip bgp
            # route next_hop is not the dvr_fip_agent_gw.
            fip_gw = self.l3plugin.create_fip_agent_gw_port_if_not_exists(
                self.context, gw_net_id, 'compute1')
            port_configs = [{'net_id': int_net['network']['id'],
                             'host': 'compute1'}]
            ports = self._create_scenario_test_ports(tenant_id, port_configs)
            dvr_gw_ip = fip_gw['fixed_ips'][0]['ip_address']
            fip_data = {'floatingip': {'floating_network_id': gw_net_id,
                                       'tenant_id': tenant_id,
                                       'port_id': ports[0]['id']}}
            fip = self.l3plugin.create_floatingip(self.context, fip_data)
            fip_address = fip['floating_ip_address']
            with self.bgp_speaker(4, 1234, networks=[gw_net_id]):
                next_hop = self.bgp_plugin._get_fip_next_hop(
                    self.context, router['id'], fip_address)
                if distributed:
                    self.assertEqual(dvr_gw_ip, next_hop)
                else:
                    self.assertEqual(legacy_gw_ip, next_hop)

    def test__get_fip_next_hop_legacy(self):
        self._test__get_fip_next_hop()

    def test__get_fip_next_hop_dvr(self):
        self._test__get_fip_next_hop(distributed=True)

    def _test__get_dvr_fixed_ip_routes_by_bgp_speaker(self,
                                                      ext_use_scope,
                                                      tenant_use_scope):
        gw_prefix = '172.16.10.0/24'
        tenant_prefix = '10.10.10.0/24'
        tenant_id = _uuid()
        scope_data = {'tenant_id': tenant_id, 'ip_version': 4,
                      'shared': True, 'name': 'bgp-scope'}
        scope = self.plugin.create_address_scope(
                                            self.context,
                                            {'address_scope': scope_data})
        with self.router_with_external_and_tenant_networks(
                        tenant_id=tenant_id,
                        gw_prefix=gw_prefix,
                        tenant_prefix=tenant_prefix,
                        address_scope=scope,
                        distributed=True,
                        ext_net_use_addr_scope=ext_use_scope,
                        tenant_net_use_addr_scope=tenant_use_scope) as res:
            router, ext_net, int_net = res
            gw_net_id = ext_net['network']['id']
            tenant_net_id = int_net['network']['id']
            fixed_port_data = {'port':
                               {'name': 'test',
                                'network_id': tenant_net_id,
                                'tenant_id': tenant_id,
                                'admin_state_up': True,
                                'device_id': _uuid(),
                                'device_owner': 'compute:nova',
                                'mac_address': n_const.ATTR_NOT_SPECIFIED,
                                'fixed_ips': n_const.ATTR_NOT_SPECIFIED,
                                portbindings.HOST_ID: 'test-host'}}
            fixed_port = self.plugin.create_port(self.context,
                                             fixed_port_data)
            fixed_ip_prefix = fixed_port['fixed_ips'][0]['ip_address'] + '/32'
            self.plugin.create_or_update_agent(self.context,
                                           {'agent_type': 'L3 agent',
                                            'host': 'test-host',
                                            'binary': 'neutron-l3-agent',
                                            'topic': 'test'})
            fip_gw = self.l3plugin.create_fip_agent_gw_port_if_not_exists(
                                                             self.context,
                                                             gw_net_id,
                                                             'test-host')
            with self.bgp_speaker(4, 1234, networks=[gw_net_id]) as speaker:
                bgp_speaker_id = speaker['id']
                routes = self.bgp_plugin._get_dvr_fixed_ip_routes_by_bgp_speaker(  # noqa
                                                           self.context,
                                                           bgp_speaker_id)
                routes = list(routes)
                dvr_gw_ip = fip_gw['fixed_ips'][0]['ip_address']
                if ext_use_scope and tenant_use_scope:
                    self.assertEqual(1, len(routes))
                    self.assertEqual(dvr_gw_ip, routes[0]['next_hop'])
                    self.assertEqual(fixed_ip_prefix, routes[0]['destination'])
                else:
                    self.assertEqual(0, len(routes))

    def test__get_dvr_fixed_ip_routes_by_bgp_speaker_same_scope(self):
        self._test__get_dvr_fixed_ip_routes_by_bgp_speaker(True, True)

    def test__get_dvr_fixed_ip_routes_by_bgp_speaker_different_scope(self):
        self._test__get_dvr_fixed_ip_routes_by_bgp_speaker(True, False)
        self._test__get_dvr_fixed_ip_routes_by_bgp_speaker(False, True)

    def test__get_dvr_fixed_ip_routes_by_bgp_speaker_no_scope(self):
        self._test__get_dvr_fixed_ip_routes_by_bgp_speaker(False, False)

    def test_get_external_networks_for_port_same_address_scope_v4(self):
        tenant_id = _uuid()
        scope_data = {'tenant_id': tenant_id, 'ip_version': 4,
                      'shared': True, 'name': 'bgp-scope'}
        self._test_get_external_networks_for_port('172.10.2.0/24',
                                                  '10.0.0.0/24',
                                                  scope_data, tenant_id,
                                                  True, True)
        self._test_get_external_networks_for_port('172.10.2.0/24',
                                                  '10.0.0.0/24',
                                                  scope_data, tenant_id,
                                                  True, True, False)

    def test_get_external_networks_for_port_different_address_scope_v4(self):
        tenant_id = _uuid()
        scope_data = {'tenant_id': tenant_id, 'ip_version': 4,
                      'shared': True, 'name': 'bgp-scope'}
        self._test_get_external_networks_for_port('172.10.2.0/24',
                                                  '10.0.0.0/24',
                                                  scope_data, tenant_id,
                                                  True, False)
        self._test_get_external_networks_for_port('172.10.2.0/24',
                                                  '10.0.0.0/24',
                                                  scope_data, tenant_id,
                                                  True, False, False)
        self._test_get_external_networks_for_port('172.10.2.0/24',
                                                  '10.0.0.0/24',
                                                  scope_data, tenant_id,
                                                  False, True)
        self._test_get_external_networks_for_port('172.10.2.0/24',
                                                  '10.0.0.0/24',
                                                  scope_data, tenant_id,
                                                  False, True, False)

    def test_get_external_networks_for_port_same_address_scope_v6(self):
        tenant_id = _uuid()
        scope_data = {'tenant_id': tenant_id, 'ip_version': 6,
                      'shared': True, 'name': 'bgp-scope'}
        self._test_get_external_networks_for_port('2001:1234:1234::/64',
                                                  '2001:1234:4321::/64',
                                                  scope_data, tenant_id,
                                                  True, True)
        self._test_get_external_networks_for_port('2001:1234:1234::/64',
                                                  '2001:1234:4321::/64',
                                                  scope_data, tenant_id,
                                                  True, True, False)

    def test_get_external_networks_for_port_different_address_scope_v6(self):
        tenant_id = _uuid()
        scope_data = {'tenant_id': tenant_id, 'ip_version': 6,
                      'shared': True, 'name': 'bgp-scope'}
        self._test_get_external_networks_for_port('2001:1234:1234::/64',
                                                  '2001:1234:4321::/64',
                                                  scope_data, tenant_id,
                                                  True, False)
        self._test_get_external_networks_for_port('2001:1234:1234::/64',
                                                  '2001:1234:4321::/64',
                                                  scope_data, tenant_id,
                                                  True, False, False)
        self._test_get_external_networks_for_port('2001:1234:1234::/64',
                                                  '2001:1234:4321::/64',
                                                  scope_data, tenant_id,
                                                  False, True)
        self._test_get_external_networks_for_port('2001:1234:1234::/64',
                                                  '2001:1234:4321::/64',
                                                  scope_data, tenant_id,
                                                  False, True, False)

    def _test_get_external_networks_for_port(self, gw_prefix, tenant_prefix,
                                             scope_data, tenant_id,
                                             external_use_address_scope,
                                             project_use_address_scope,
                                             match_address_scopes=True):
        scope = None
        if scope_data:
            scope = self.plugin.create_address_scope(
                                            self.context,
                                            {'address_scope': scope_data})

        with self.router_with_external_and_tenant_networks(
                tenant_id=tenant_id,
                gw_prefix=gw_prefix,
                tenant_prefix=tenant_prefix,
                address_scope=scope,
                distributed=True,
                ext_net_use_addr_scope=external_use_address_scope,
                tenant_net_use_addr_scope=project_use_address_scope) as res:
            router, ext_net, int_net = res
            gw_net_id = ext_net['network']['id']
            tenant_net_id = int_net['network']['id']
            fixed_port_data = {'port':
                               {'name': 'test',
                                'network_id': tenant_net_id,
                                'tenant_id': tenant_id,
                                'admin_state_up': True,
                                'device_id': _uuid(),
                                'device_owner': 'compute:nova',
                                'mac_address': n_const.ATTR_NOT_SPECIFIED,
                                'fixed_ips': n_const.ATTR_NOT_SPECIFIED,
                                portbindings.HOST_ID: 'test-host'}}
            fixed_port = self.plugin.create_port(self.context,
                                             fixed_port_data)
            self.plugin.create_or_update_agent(self.context,
                                           {'agent_type': 'L3 agent',
                                            'host': 'test-host',
                                            'binary': 'neutron-l3-agent',
                                            'topic': 'test'})
            ext_nets = self.bgp_plugin.get_external_networks_for_port(
                                    self.context,
                                    fixed_port,
                                    match_address_scopes=match_address_scopes)

            if not match_address_scopes:
                self.assertEqual(1, len(ext_nets))
                self.assertEqual(gw_net_id, ext_nets[0])
            elif external_use_address_scope and project_use_address_scope:
                self.assertEqual(1, len(ext_nets))
                self.assertEqual(gw_net_id, ext_nets[0])
            else:
                self.assertEqual(0, len(ext_nets))


class Ml2BgpTests(test_plugin.Ml2PluginV2TestCase,
                  BgpTests):
    fmt = 'json'

    def setup_parent(self):
        self.l3_plugin = ('neutron_dynamic_routing.tests.unit.db.test_bgp_db.'
                          'TestL3Plugin')
        super(Ml2BgpTests, self).setup_parent()

    def setUp(self):
        super(Ml2BgpTests, self).setUp()
        self.l3plugin = directory.get_plugin(plugin_constants.L3)
        self.bgp_plugin = bgp_plugin.BgpPlugin()
        self.plugin = directory.get_plugin()
        # Extend network HA extension.
        rname = network_ha.COLLECTION_NAME
        attributes.RESOURCES[rname].update(
            network_ha.RESOURCE_ATTRIBUTE_MAP[rname])
