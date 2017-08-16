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

from tempest import config

from neutron_dynamic_routing.tests.tempest.scenario import base

from ryu.tests.integrated.common import docker_base as ctn_base

CONF = config.CONF


class BgpSpeakerProtoTestBase(base.BgpSpeakerScenarioTestJSONBase):

    def _test_check_neighbor_established(self, ip_version):
        self.bgp_peer_args[0]['peer_ip'] = self.r_as_ip[0].split('/')[0]
        num, subnet = self.tnet_gen.next()
        mask = '/' + str(self.TPool.prefixlen)
        TNet = base.Net(name='', net=subnet, mask=self.TPool.prefixlen,
                        cidr=subnet + mask, router=None)
        TSubNet = base.SubNet(name='', cidr=TNet.cidr, mask=TNet.mask)
        MyRouter = base.Router(name='my-router' + str(num), gw='')
        ext_net_id = self.create_bgp_network(
            ip_version, self.MyScope,
            self.PNet, self.PPool, self.PSubNet,
            self.TPool, [[TNet, TSubNet, MyRouter]])
        speaker_id, peers_ids = self.create_and_add_peers_to_speaker(
            ext_net_id,
            self.bgp_speaker_args,
            [self.bgp_peer_args[0]])
        self.check_remote_as_state(self.dr, self.r_ass[0],
                                   ctn_base.BGP_FSM_ESTABLISHED)

    def _test_check_advertised_tenant_network(self, ip_version):
        self.bgp_peer_args[0]['peer_ip'] = self.r_as_ip[0].split('/')[0]
        num, subnet = self.tnet_gen.next()
        mask = '/' + str(self.TPool.prefixlen)
        TNet = base.Net(name='', net=subnet, mask=self.TPool.prefixlen,
                        cidr=subnet + mask, router=None)
        TSubNet = base.SubNet(name='', cidr=TNet.cidr, mask=TNet.mask)
        MyRouter = base.Router(name='my-router' + str(num), gw='')
        ext_net_id = self.create_bgp_network(
            ip_version, self.MyScope,
            self.PNet, self.PPool, self.PSubNet,
            self.TPool, [[TNet, TSubNet, MyRouter]])
        speaker_id, peers_ids = self.create_and_add_peers_to_speaker(
            ext_net_id,
            self.bgp_speaker_args,
            [self.bgp_peer_args[0]])
        self.check_remote_as_state(self.dr, self.r_ass[0],
                                   ctn_base.BGP_FSM_ESTABLISHED)
        rf = 'ipv' + str(ip_version)
        self.check_remote_as_rib(self.r_ass[0], TNet.cidr, rf,
                                 'nexthop',
                                 self.get_next_hop(speaker_id, TNet.cidr))

    def _test_check_advertised_multiple_tenant_network(self, ip_version):
        self.bgp_peer_args[0]['peer_ip'] = self.r_as_ip[0].split('/')[0]
        tnets = []
        tnets_cidr = []
        for i in range(0, 3):
            num, subnet = self.tnet_gen.next()
            mask = '/' + str(self.TPool.prefixlen)
            TNet = base.Net(name='', net=subnet, mask=self.TPool.prefixlen,
                            cidr=subnet + mask, router=None)
            TSubNet = base.SubNet(name='', cidr=TNet.cidr, mask=TNet.mask)
            MyRouter = base.Router(name='my-router' + str(num), gw='')
            tnets.append([TNet, TSubNet, MyRouter])
            tnets_cidr.append(TNet.cidr)
        ext_net_id = self.create_bgp_network(
            ip_version, self.MyScope,
            self.PNet, self.PPool, self.PSubNet,
            self.TPool, tnets)
        speaker_id, peers_ids = self.create_and_add_peers_to_speaker(
            ext_net_id,
            self.bgp_speaker_args,
            [self.bgp_peer_args[0]])
        self.check_remote_as_state(self.dr, self.r_ass[0],
                                   ctn_base.BGP_FSM_ESTABLISHED)
        rf = 'ipv' + str(ip_version)
        for cidr in tnets_cidr:
            self.check_remote_as_rib(self.r_ass[0], cidr, rf,
                                     'nexthop',
                                     self.get_next_hop(speaker_id, cidr))

    def _test_check_neighbor_established_with_multiple_peers(
            self, ip_version):
        for (bgp_peer_args, r_as_ip) in zip(self.bgp_peer_args,
                                            self.r_as_ip):
            bgp_peer_args['peer_ip'] = r_as_ip.split('/')[0]
        num, subnet = self.tnet_gen.next()
        mask = '/' + str(self.TPool.prefixlen)
        TNet = base.Net(name='', net=subnet, mask=self.TPool.prefixlen,
                        cidr=subnet + mask, router=None)
        TSubNet = base.SubNet(name='', cidr=TNet.cidr, mask=TNet.mask)
        MyRouter = base.Router(name='my-router' + str(num), gw='')
        ext_net_id = self.create_bgp_network(
            ip_version, self.MyScope,
            self.PNet, self.PPool, self.PSubNet,
            self.TPool, [[TNet, TSubNet, MyRouter]])
        speaker_id, peers_ids = self.create_and_add_peers_to_speaker(
            ext_net_id,
            self.bgp_speaker_args,
            self.bgp_peer_args)
        self.check_multi_remote_as_state(self.dr, self.r_ass,
                                         ctn_base.BGP_FSM_ESTABLISHED)

    def _test_check_advertised_tenant_network_with_multiple_peers(
            self, ip_version):
        for (bgp_peer_args, r_as_ip) in zip(self.bgp_peer_args,
                                            self.r_as_ip):
            bgp_peer_args['peer_ip'] = r_as_ip.split('/')[0]
        num, subnet = self.tnet_gen.next()
        mask = '/' + str(self.TPool.prefixlen)
        TNet = base.Net(name='', net=subnet, mask=self.TPool.prefixlen,
                        cidr=subnet + mask, router=None)
        TSubNet = base.SubNet(name='', cidr=TNet.cidr, mask=TNet.mask)
        MyRouter = base.Router(name='my-router' + str(num), gw='')
        ext_net_id = self.create_bgp_network(
            ip_version, self.MyScope,
            self.PNet, self.PPool, self.PSubNet,
            self.TPool, [[TNet, TSubNet, MyRouter]])
        speaker_id, peers_ids = self.create_and_add_peers_to_speaker(
            ext_net_id,
            self.bgp_speaker_args,
            self.bgp_peer_args)
        self.check_multi_remote_as_state(self.dr, self.r_ass,
                                         ctn_base.BGP_FSM_ESTABLISHED)
        rf = 'ipv' + str(ip_version)
        next_hop = self.get_next_hop(speaker_id, TNet.cidr)
        self.check_multi_remote_as_rib(self.r_ass, TNet.cidr, rf,
                                       'nexthop', next_hop)
