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

import netaddr

from neutron_lib import constants as lib_consts

from neutron_dynamic_routing.services.bgp.agent.driver import exceptions as bgp_driver_exc  # noqa
from neutron_dynamic_routing.services.bgp.common import constants as bgp_consts  # noqa


# Parameter validation functions provided are provided by the base.
def validate_as_num(param, as_num):
    if not isinstance(as_num, int):
        raise bgp_driver_exc.InvalidParamType(param=param,
                                              param_type='integer')

    if not (bgp_consts.MIN_ASNUM <= as_num <= bgp_consts.MAX_4BYTE_ASNUM):
        # Must be in [AS_NUM_MIN, MAX_4BYTE_ASNUM] range.
        allowed_range = ('[' +
                         str(bgp_consts.MIN_ASNUM) + '-' +
                         str(bgp_consts.MAX_4BYTE_ASNUM) +
                         ']')
        raise bgp_driver_exc.InvalidParamRange(param=param,
                                               range=allowed_range)


def validate_auth(auth_type, password):
    validate_string(password)
    if auth_type in bgp_consts.SUPPORTED_AUTH_TYPES:
        if auth_type != 'none' and password is None:
            raise bgp_driver_exc.PasswordNotSpecified(auth_type=auth_type)
        if auth_type == 'none' and password is not None:
            raise bgp_driver_exc.InvaildAuthType(auth_type=auth_type)
    else:
        raise bgp_driver_exc.InvaildAuthType(auth_type=auth_type)


def validate_ip_addr(ip_addr):
    if netaddr.valid_ipv4(ip_addr):
        return lib_consts.IP_VERSION_4
    elif netaddr.valid_ipv6(ip_addr):
        return lib_consts.IP_VERSION_6
    else:
        raise bgp_driver_exc.InvalidParamType(param=ip_addr,
                                              param_type='ip-address')


def validate_string(param):
    if param is not None:
        if not isinstance(param, str):
            raise bgp_driver_exc.InvalidParamType(param=param,
                                                  param_type='string')


class BgpMultiSpeakerCache(object):
    """Class for saving multiple BGP speakers information.

    Version history:
        1.0 - Initial version for caching multiple BGP speaker information.
    """
    def __init__(self):
        self.cache = {}

    def get_hosted_bgp_speakers_count(self):
        return len(self.cache)

    def put_bgp_speaker(self, local_as, speaker):
        self.cache[local_as] = speaker

    def get_bgp_speaker(self, local_as):
        return self.cache.get(local_as)

    def remove_bgp_speaker(self, local_as):
        self.cache.pop(local_as, None)
