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
from tempest.lib import decorators

from neutron_dynamic_routing.tests.tempest.scenario import base
from neutron_dynamic_routing.tests.tempest.scenario import base_test_proto as test_base  # noqa

from ryu.tests.integrated.common import docker_base as ctn_base
from ryu.tests.integrated.common import quagga

CONF = config.CONF


class BgpSpeakerIpv6Test(test_base.BgpSpeakerProtoTestBase):

    RAS_MAX = 3
    ip_version = 6
    public_gw = '2001:db8:a000::1'
    MyScope = base.Scope(name='my-scope')
    PNet = base.Net(name='', net='2001:db8::', mask=64,
                    cidr='2001:db8::/64', router=None)
    PPool = base.Pool(name='test-pool-ext', prefixlen=PNet.mask,
                      prefixes=[PNet.net + '/8'])
    PSubNet = base.SubNet(name='', cidr=PNet.cidr, mask=PNet.mask)
    TPool = base.Pool(name='tenant-test-pool', prefixlen=64,
                      prefixes=['2001:db8:8000::/48'])
    L_AS = base.AS(asn='64512', router_id='192.168.0.2', adv_net='')
    ras_l = [
        base.AS(asn='64522', router_id='192.168.0.12',
                adv_net='2001:db8:9002::/48'),
        base.AS(asn='64523', router_id='192.168.0.13',
                adv_net='2001:db8:9003::/48'),
        base.AS(asn='64524', router_id='192.168.0.14',
                adv_net='2001:db8:9004::/48')
    ]

    bgp_speaker_args = {
        'local_as': L_AS.asn,
        'ip_version': ip_version,
        'name': 'my-bgp-speaker1',
        'advertise_floating_ip_host_routes': True,
        'advertise_tenant_networks': True
    }
    bgp_peer_args = [
        {'remote_as': ras_l[0].asn,
         'name': 'my-bgp-peer1',
         'peer_ip': None,
         'auth_type': 'none'},
        {'remote_as': ras_l[1].asn,
         'name': 'my-bgp-peer2',
         'peer_ip': None,
         'auth_type': 'none'},
        {'remote_as': ras_l[2].asn,
         'name': 'my-bgp-peer3',
         'peer_ip': None,
         'auth_type': 'none'}
    ]

    def setUp(self):
        super(BgpSpeakerIpv6Test, self).setUp()

    @classmethod
    def resource_setup_container(cls):
        cls.brdc = ctn_base.Bridge(name='br-docker-ipv6',
                                   subnet='2001:db8:a000::/64',
                                   start_ip='2001:db8:a000::8000',
                                   end_ip='2001:db8:a000::fffe',
                                   self_ip=True,
                                   fixed_ip=cls.public_gw + '/64',
                                   br_type=base.BRIDGE_TYPE)
        cls.bridges.append(cls.brdc)
        # This is dummy container object for a dr service.
        # This keeps data which passes to a quagga container.
        cls.dr = ctn_base.BGPContainer(name='dr', asn=int(cls.L_AS.asn),
                                       router_id=cls.L_AS.router_id)
        cls.dr.set_addr_info(bridge='br-docker-ipv6', ipv6=cls.public_gw)
        # quagga container
        cls.dockerimg = ctn_base.DockerImage()
        cls.q_img = cls.dockerimg.create_quagga(check_exist=True)
        cls.images.append(cls.q_img)
        for i in range(cls.RAS_MAX):
            qg = quagga.QuaggaBGPContainer(name='q' + str(i + 1),
                                           asn=int(cls.ras_l[i].asn),
                                           router_id=cls.ras_l[i].router_id,
                                           ctn_image_name=cls.q_img)
            cls.containers.append(qg)
            cls.r_ass.append(qg)
            qg.add_route(cls.ras_l[i].adv_net, route_info={'rf': 'ipv6'})
            qg.run(wait=True)
            cls.r_as_ip.append(cls.brdc.addif(qg))
            qg.add_peer(cls.dr, bridge=cls.brdc.name, v6=True,
                        peer_info={'passive': True})
        cls.tnet_gen = cls.get_subnet(start='2001:db8:8000:1::',
                                      end='2001:db8:8000:ffff::',
                                      step=65536 * 65536 * 65536 * 65536)

    @decorators.idempotent_id('5194a8e2-95bd-49f0-872d-1e3e875ede32')
    def test_check_neighbor_established(self):
        self._test_check_neighbor_established(self.ip_version)

    @decorators.idempotent_id('6a3483fc-8c8a-4387-bda6-c7061410e04b')
    def test_check_advertised_tenant_network(self):
        self._test_check_advertised_tenant_network(self.ip_version)

    @decorators.idempotent_id('aca5d678-c249-4de5-921b-6b6ba621e4f7')
    def test_check_advertised_multiple_tenant_network(self):
        self._test_check_advertised_multiple_tenant_network(self.ip_version)

    @decorators.idempotent_id('f81012f3-2f7e-4b3c-8c1d-b1778146d712')
    def test_check_neighbor_established_with_multiple_peers(self):
        self._test_check_neighbor_established_with_multiple_peers(
            self.ip_version)

    @decorators.idempotent_id('be710ec1-a338-44c9-8b89-31c3532aae65')
    def test_check_advertised_tenant_network_with_multiple_peers(self):
        self._test_check_advertised_tenant_network_with_multiple_peers(
            self.ip_version)
