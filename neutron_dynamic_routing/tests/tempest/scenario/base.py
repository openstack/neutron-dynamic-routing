# Copyright (C) 2016 VA Linux Systems Japan K.K.
# Copyright (C) 2016 Fumihiko Kakuma <kakuma at valinux co jp>
# All Rights Reserved.
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

import collections
import threading
import time

import netaddr

from tempest.common import utils
from tempest import config

from neutron_tempest_plugin.api import base
from ryu.tests.integrated.common import docker_base as ctn_base

from neutron_dynamic_routing.tests.tempest import bgp_client

CONF = config.CONF

Scope = collections.namedtuple('Scope', 'name')
Pool = collections.namedtuple('Pool', 'name, prefixlen, prefixes')
Net = collections.namedtuple('Net', 'name, net, mask, cidr, router')
SubNet = collections.namedtuple('SubNet', 'name, cidr, mask')
Router = collections.namedtuple('Router', 'name, gw')
AS = collections.namedtuple('AS', 'asn, router_id, adv_net')
CHECKTIME = 180
CHECKTIME_INFO = 60
CHECKTIME_INT = 1
BRIDGE_TYPE = ctn_base.BRIDGE_TYPE_DOCKER


def _setup_client_args(auth_provider):
    """Set up ServiceClient arguments using config settings. """
    service = CONF.network.catalog_type or 'network'
    region = CONF.network.region or 'regionOne'
    endpoint_type = CONF.network.endpoint_type
    build_interval = CONF.network.build_interval
    build_timeout = CONF.network.build_timeout

    # The disable_ssl appears in identity
    disable_ssl_certificate_validation = (
        CONF.identity.disable_ssl_certificate_validation)
    ca_certs = None

    # Trace in debug section
    trace_requests = CONF.debug.trace_requests

    return [auth_provider, service, region, endpoint_type,
            build_interval, build_timeout,
            disable_ssl_certificate_validation, ca_certs,
            trace_requests]


class BgpSpeakerScenarioTestJSONBase(base.BaseAdminNetworkTest):

    def setUp(self):
        self.addCleanup(self.net_resource_cleanup)
        super(BgpSpeakerScenarioTestJSONBase, self).setUp()

    @classmethod
    def _setup_bgp_non_admin_client(cls):
        mgr = cls.get_client_manager()
        auth_provider = mgr.auth_provider
        client_args = _setup_client_args(auth_provider)
        cls.bgp_client = bgp_client.BgpSpeakerClientJSON(*client_args)

    @classmethod
    def _setup_bgp_admin_client(cls):
        mgr = cls.get_client_manager(credential_type='admin')
        auth_provider = mgr.auth_provider
        client_args = _setup_client_args(auth_provider)
        cls.bgp_adm_client = bgp_client.BgpSpeakerClientJSON(*client_args)

    @classmethod
    def resource_setup(cls):
        super(BgpSpeakerScenarioTestJSONBase, cls).resource_setup()
        if not utils.is_extension_enabled('bgp', 'network'):
            msg = "BGP Speaker extension is not enabled."
            raise cls.skipException(msg)

        cls.images = []
        cls.containers = []
        cls.r_ass = []
        cls.r_as_ip = []
        cls.bridges = []
        cls.admin_routerports = []
        cls.admin_floatingips = []
        cls.admin_routers = []
        cls.admin_router_ip = []
        cls.resource_setup_container()
        cls._setup_bgp_admin_client()
        cls._setup_bgp_non_admin_client()
        cls.lock = threading.Lock()

    @classmethod
    def resource_cleanup(cls):
        for ctn in cls.containers:
            try:
                ctn.stop()
            except ctn_base.CommandError:
                pass
            ctn.remove()
        for br in cls.bridges:
            br.delete()
        super(BgpSpeakerScenarioTestJSONBase, cls).resource_cleanup()

    @classmethod
    def get_subnet(self, start='10.10.1.0', end='10.10.255.0', step=256):
        subnet_gen = netaddr.iter_iprange(start, end, step=step)
        i = 1
        while True:
            with self.lock:
                try:
                    yield (i, str(subnet_gen.next()))
                except StopIteration:
                    subnet_gen = netaddr.iter_iprange(start, end, step=step)
                    yield (i, str(subnet_gen.next()))
                i += 1

    def net_resource_cleanup(self):
        for floatingip in self.admin_floatingips:
            self._try_delete_resource(self.admin_client.delete_floatingip,
                                      floatingip['id'])
        for routerport in self.admin_routerports:
            self._try_delete_resource(
                self.admin_client.remove_router_interface_with_subnet_id,
                routerport['router_id'], routerport['subnet_id'])
        for router in self.admin_routers:
            self._try_delete_resource(self.admin_client.delete_router,
                                      router['id'])

    def create_bgp_speaker(self, auto_delete=True, **args):
        data = {'bgp_speaker': args}
        bgp_speaker = self.bgp_adm_client.create_bgp_speaker(data)
        bgp_speaker_id = bgp_speaker['bgp_speaker']['id']
        if auto_delete:
            self.addCleanup(self.bgp_adm_client.delete_bgp_speaker,
                            bgp_speaker_id)
        return bgp_speaker['bgp_speaker']

    def delete_bgp_speaker(self, id):
        return self.bgp_adm_client.delete_bgp_speaker(id)

    def create_bgp_peer(self, auto_delete=True, **args):
        bgp_peer = self.bgp_adm_client.create_bgp_peer({'bgp_peer': args})
        bgp_peer_id = bgp_peer['bgp_peer']['id']
        if auto_delete:
            self.addCleanup(self.bgp_adm_client.delete_bgp_peer,
                            bgp_peer_id)
        return bgp_peer['bgp_peer']

    def delete_bgp_peer(self, id):
        return self.bgp_adm_client.delete_bgp_peer(id)

    def get_dragent_id(self):
        agents = self.admin_client.list_agents(
            agent_type="BGP dynamic routing agent")
        self.assertTrue(agents['agents'][0]['alive'])
        return agents['agents'][0]['id']

    def add_bgp_speaker_to_dragent(self, agent_id, speaker_id):
        self.bgp_adm_client.add_bgp_speaker_to_dragent(agent_id, speaker_id)

    # tnets[[net1, subnet1, router1], [net2, subnet2, router2], ...]
    def create_bgp_network(self, ip_version, scope,
                           exnet, expool, exsubnet,
                           tpool, tnets):
        addr_scope = self.create_address_scope(scope.name,
                                               ip_version=ip_version)
        # external network
        ext_net = self.create_shared_network(**{'router:external': True})
        ext_net_id = ext_net['id']
        ext_subnetpool = self.create_subnetpool(
            expool.name,
            is_admin=True,
            default_prefixlen=expool.prefixlen,
            address_scope_id=addr_scope['id'],
            prefixes=expool.prefixes)
        self.create_subnet(
            {'id': ext_net_id},
            cidr=netaddr.IPNetwork(exsubnet.cidr),
            mask_bits=exsubnet.mask,
            ip_version=ip_version,
            client=self.admin_client,
            subnetpool_id=ext_subnetpool['id'],
            reserve_cidr=False)
        # tenant network
        tenant_subnetpool = self.create_subnetpool(
            tpool.name,
            default_prefixlen=tpool.prefixlen,
            address_scope_id=addr_scope['id'],
            prefixes=tpool.prefixes)
        for tnet, tsubnet, router in tnets:
            tenant_net = self.create_network()
            tenant_subnet = self.create_subnet(
                {'id': tenant_net['id']},
                cidr=netaddr.IPNetwork(tsubnet.cidr),
                mask_bits=tsubnet.mask,
                ip_version=ip_version,
                subnetpool_id=tenant_subnetpool['id'],
                reserve_cidr=False)
            # router
            ext_gw_info = {'network_id': ext_net_id}
            router_cr = self.admin_client.create_router(
                router.name,
                external_gateway_info=ext_gw_info)['router']
            self.admin_routers.append(router_cr)
            self.admin_client.add_router_interface_with_subnet_id(
                router_cr['id'],
                tenant_subnet['id'])
            self.admin_routerports.append({'router_id': router_cr['id'],
                                           'subnet_id': tenant_subnet['id']})
            router = self.admin_client.show_router(router_cr['id'])['router']
            fixed_ips = router['external_gateway_info']['external_fixed_ips']
            self.admin_router_ip.append(fixed_ips[0]['ip_address'])
        return ext_net_id

    def create_and_add_peers_to_speaker(self, ext_net_id,
                                        speaker_info, peer_infos,
                                        auto_delete=True):
        speaker = self.create_bgp_speaker(auto_delete=auto_delete,
                                          **speaker_info)
        speaker_id = speaker['id']
        self.bgp_adm_client.add_bgp_gateway_network(speaker_id,
                                                    ext_net_id)
        peer_ids = []
        for peer_args in peer_infos:
            peer = self.create_bgp_peer(auto_delete=auto_delete,
                                        **peer_args)
            peer_id = peer['id']
            peer_ids.append(peer_id)
            self.bgp_adm_client.add_bgp_peer_with_id(speaker_id,
                                                     peer_id)
        return (speaker_id, peer_ids)

    def get_remote_as_state(self, l_as, r_as,
                            expected_state,
                            init_state=ctn_base.BGP_FSM_IDLE,
                            checktime=CHECKTIME,
                            checktime_int=CHECKTIME_INT):
        neighbor_state = init_state
        for i in range(0, checktime):
            neighbor_state = r_as.get_neighbor_state(l_as)
            if neighbor_state == expected_state:
                break
            time.sleep(checktime_int)
        return neighbor_state

    def check_remote_as_state(self, l_as, r_as,
                              expected_state,
                              init_state=ctn_base.BGP_FSM_IDLE,
                              checktime=CHECKTIME,
                              checktime_int=CHECKTIME_INT):
        neighbor_state = self.get_remote_as_state(l_as, r_as,
                                                  expected_state,
                                                  init_state=init_state,
                                                  checktime=checktime,
                                                  checktime_int=checktime_int)
        self.assertEqual(neighbor_state, expected_state)

    def get_remote_as_of_state_ok(self, l_as, r_ass,
                                  expected_state,
                                  init_state=ctn_base.BGP_FSM_IDLE,
                                  checktime=CHECKTIME,
                                  checktime_int=CHECKTIME_INT):
        neighbor_state = init_state
        ras_list = []
        ras_max = len(r_ass)
        for r_as in r_ass:
            ras_list.append({'as': r_as, 'check': False})
        ok_ras = []
        for i in range(0, checktime):
            for ras in ras_list:
                if ras['check']:
                    continue
                neighbor_state = ras['as'].get_neighbor_state(l_as)
                if neighbor_state == expected_state:
                    ras['check'] = True
                    ok_ras.append(ras['as'])
            if len(ok_ras) >= ras_max:
                break
            time.sleep(checktime_int)
        return ok_ras

    def check_multi_remote_as_state(self, l_as, r_ass,
                                    expected_state,
                                    init_state=ctn_base.BGP_FSM_IDLE,
                                    checktime=CHECKTIME,
                                    checktime_int=CHECKTIME_INT):
        ok_ras = self.get_remote_as_of_state_ok(
            l_as, r_ass,
            expected_state,
            init_state=init_state,
            checktime=checktime,
            checktime_int=checktime_int)
        self.assertEqual(len(ok_ras), len(r_ass))

    def get_remote_as_rib(self, r_as, prefix, rf, key, expected_item,
                          checktime=CHECKTIME_INFO,
                          checktime_int=CHECKTIME_INT):
        item = None
        for i in range(0, checktime):
            rib = r_as.get_global_rib(prefix=prefix, rf=rf)
            if rib and key in rib[0]:
                if expected_item == rib[0][key]:
                    item = rib[0][key]
                    break
            time.sleep(checktime_int)
        return item

    def check_remote_as_rib(self, r_as, prefix, rf, key, expected_item,
                            checktime=CHECKTIME_INFO,
                            checktime_int=CHECKTIME_INT):
        item = self.get_remote_as_rib(r_as=r_as, prefix=prefix, rf=rf,
                                      key=key, expected_item=expected_item,
                                      checktime=checktime,
                                      checktime_int=checktime_int)
        self.assertEqual(expected_item, item)

    def get_remote_as_of_rib_ok(self, r_ass, prefix, rf, key, expected_item,
                                checktime=CHECKTIME_INFO,
                                checktime_int=CHECKTIME_INT):
        ras_list = []
        ras_max = len(r_ass)
        for r_as in r_ass:
            ras_list.append({'as': r_as, 'check': False})
        ok_ras = []
        for i in range(0, checktime):
            for ras in ras_list:
                if ras['check']:
                    continue
                rib = r_as.get_global_rib(prefix=prefix, rf=rf)
                if rib and key in rib[0]:
                    if expected_item == rib[0][key]:
                        ras['check'] = True
                        ok_ras.append(ras['as'])
            if len(ok_ras) >= ras_max:
                break
            time.sleep(checktime_int)
        return ok_ras

    def check_multi_remote_as_rib(self, r_ass, prefix, rf, key, expected_item,
                                  checktime=CHECKTIME_INFO,
                                  checktime_int=CHECKTIME_INT):
        ok_ras = self.get_remote_as_of_rib_ok(
                   r_ass=r_ass, prefix=prefix, rf=rf,
                   key=key, expected_item=expected_item,
                   checktime=checktime,
                   checktime_int=checktime_int)
        self.assertEqual(len(ok_ras), len(r_ass))

    def get_next_hop(self, speaker_id, dest_addr):
        routes = self.bgp_adm_client.get_bgp_advertised_routes(speaker_id)
        next_hop = ''
        for route in routes['advertised_routes']:
            if route['destination'] == dest_addr:
                next_hop = route['next_hop']
                break
        return next_hop
