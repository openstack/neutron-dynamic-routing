# Copyright 2016 Huawei Technologies India Pvt. Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from neutron_lib import constants as lib_consts

from neutron.tests import base

from neutron_dynamic_routing.services.bgp.agent.driver import exceptions as bgp_driver_exc  # noqa
from neutron_dynamic_routing.services.bgp.agent.driver import utils as bgp_driver_utils  # noqa
from neutron_dynamic_routing.services.bgp.common import constants as bgp_consts  # noqa

FAKE_IP = '2.2.2.5'
FAKE_IPV6 = '2001:db8::'
FAKE_LOCAL_AS = 12345
FAKE_OS_KEN_SPEAKER = {}
EXC_INV_PARAMTYPE = "Parameter %(param)s must be of %(param_type)s type."
EXC_INV_PARAMRANGE = "%(param)s must be in %(range)s range."
EXC_PASSWORD_NOTSPEC = "Password not specified for authentication " + \
                       "type=%(auth_type)s."
EXC_INV_AUTHTYPE = "Authentication type not supported. Requested " + \
                   "type=%(auth_type)s."


class TestValidateMethod(base.BaseTestCase):

    def setUp(self):
        super(TestValidateMethod, self).setUp()

    def test_validate_as_num_with_valid_as_num(self):
        self.assertIsNone(bgp_driver_utils.validate_as_num('local_as',
                                                           64512))

    def test_validate_as_num_with_string_as_num(self):
        with self.assertRaisesRegex(
                bgp_driver_exc.InvalidParamType,
                EXC_INV_PARAMTYPE % {'param': 'local_as',
                                     'param_type': 'integer'}):
            bgp_driver_utils.validate_as_num('local_as', '64512')

    def test_validate_as_num_with_invalid_max_range(self):
        allowed_range = ('\\[' +
                         str(bgp_consts.MIN_ASNUM) + '-' +
                         str(bgp_consts.MAX_4BYTE_ASNUM) +
                         '\\]')
        with self.assertRaisesRegex(
                bgp_driver_exc.InvalidParamRange,
                EXC_INV_PARAMRANGE % {'param': 'local_as',
                                      'range': allowed_range}):
            bgp_driver_utils.validate_as_num('local_as',
                                             bgp_consts.MAX_4BYTE_ASNUM + 1)

    def test_validate_as_num_with_invalid_min_range(self):
        allowed_range = ('\\[' +
                         str(bgp_consts.MIN_ASNUM) + '-' +
                         str(bgp_consts.MAX_4BYTE_ASNUM) +
                         '\\]')
        with self.assertRaisesRegex(
                bgp_driver_exc.InvalidParamRange,
                EXC_INV_PARAMRANGE % {'param': 'local_as',
                                      'range': allowed_range}):
            bgp_driver_utils.validate_as_num('local_as', 0)

    def test_validate_auth_with_valid_auth_type(self):
        passwords = [None, 'password']
        for (auth_type, passwd) in zip(bgp_consts.SUPPORTED_AUTH_TYPES,
                                       passwords):
            self.assertIsNone(bgp_driver_utils.validate_auth(auth_type,
                                                             passwd))

    def test_validate_auth_with_integer_password(self):
        auth_type = bgp_consts.SUPPORTED_AUTH_TYPES[1]
        with self.assertRaisesRegex(
                bgp_driver_exc.InvalidParamType,
                EXC_INV_PARAMTYPE % {'param': '12345',
                                     'param_type': 'string'}):
            bgp_driver_utils.validate_auth(auth_type, 12345)

    def test_validate_auth_with_invalid_auth_type(self):
        auth_type = 'abcde'
        with self.assertRaisesRegex(
                bgp_driver_exc.InvaildAuthType,
                EXC_INV_AUTHTYPE % {'auth_type': auth_type}):
            bgp_driver_utils.validate_auth(auth_type, 'password')

    def test_validate_auth_with_not_none_auth_type_and_none_password(self):
        auth_type = bgp_consts.SUPPORTED_AUTH_TYPES[1]
        with self.assertRaisesRegex(
                bgp_driver_exc.PasswordNotSpecified,
                EXC_PASSWORD_NOTSPEC % {'auth_type': auth_type}):
            bgp_driver_utils.validate_auth(auth_type, None)

    def test_validate_auth_with_none_auth_type_and_not_none_password(self):
        auth_type = None
        with self.assertRaisesRegex(
                bgp_driver_exc.InvaildAuthType,
                EXC_INV_AUTHTYPE % {'auth_type': auth_type}):
            bgp_driver_utils.validate_auth(auth_type, 'password')

    def test_validate_ip_addr_with_ipv4_address(self):
        self.assertEqual(lib_consts.IP_VERSION_4,
                         bgp_driver_utils.validate_ip_addr(FAKE_IP))

    def test_validate_ip_addr_with_ipv6_address(self):
        self.assertEqual(lib_consts.IP_VERSION_6,
                         bgp_driver_utils.validate_ip_addr(FAKE_IPV6))

    def test_validate_ip_addr_with_integer_ip(self):
        with self.assertRaisesRegex(
                bgp_driver_exc.InvalidParamType,
                EXC_INV_PARAMTYPE % {'param': '12345',
                                     'param_type': 'ip-address'}):
            bgp_driver_utils.validate_ip_addr(12345)

    def test_validate_ip_addr_with_invalid_ipv4_type(self):
        with self.assertRaisesRegex(
                bgp_driver_exc.InvalidParamType,
                EXC_INV_PARAMTYPE % {'param': '1.2.3.a',
                                     'param_type': 'ip-address'}):
            bgp_driver_utils.validate_ip_addr('1.2.3.a')

    def test_validate_ip_addr_with_invalid_ipv6_type(self):
        with self.assertRaisesRegex(
                bgp_driver_exc.InvalidParamType,
                EXC_INV_PARAMTYPE % {'param': '2001:db8::ggg',
                                     'param_type': 'ip-address'}):
            bgp_driver_utils.validate_ip_addr('2001:db8::ggg')

    def test_validate_string_with_string(self):
        self.assertIsNone(bgp_driver_utils.validate_string(FAKE_IP))

    def test_validate_string_with_integer_param(self):
        with self.assertRaisesRegex(
                bgp_driver_exc.InvalidParamType,
                EXC_INV_PARAMTYPE % {'param': '12345',
                                     'param_type': 'string'}):
            bgp_driver_utils.validate_string(12345)


class TestBgpMultiSpeakerCache(base.BaseTestCase):

    def setUp(self):
        super(TestBgpMultiSpeakerCache, self).setUp()
        self.expected_cache = {FAKE_LOCAL_AS: FAKE_OS_KEN_SPEAKER}
        self.bs_cache = bgp_driver_utils.BgpMultiSpeakerCache()

    def test_put_bgp_speaker(self):
        self.bs_cache.put_bgp_speaker(FAKE_LOCAL_AS, FAKE_OS_KEN_SPEAKER)
        self.assertEqual(self.expected_cache, self.bs_cache.cache)

    def test_remove_bgp_speaker(self):
        self.bs_cache.put_bgp_speaker(FAKE_LOCAL_AS, FAKE_OS_KEN_SPEAKER)
        self.assertEqual(1, len(self.bs_cache.cache))
        self.bs_cache.remove_bgp_speaker(FAKE_LOCAL_AS)
        self.assertEqual(0, len(self.bs_cache.cache))

    def test_get_bgp_speaker(self):
        self.bs_cache.put_bgp_speaker(FAKE_LOCAL_AS, FAKE_OS_KEN_SPEAKER)
        self.assertEqual(
            FAKE_OS_KEN_SPEAKER,
            self.bs_cache.get_bgp_speaker(FAKE_LOCAL_AS))

    def test_get_hosted_bgp_speakers_count(self):
        self.bs_cache.put_bgp_speaker(FAKE_LOCAL_AS, FAKE_OS_KEN_SPEAKER)
        self.assertEqual(1, self.bs_cache.get_hosted_bgp_speakers_count())
