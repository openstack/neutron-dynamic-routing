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

from neutron_lib.api import extensions as api_extensions

from neutron_dynamic_routing.extensions import bgp as bgp_ext
from neutron_dynamic_routing.services.bgp.common import constants as bgp_consts


BGP_4BYTE_ASN_EXT_ALIAS = 'bgp_4byte_asn'


RESOURCE_ATTRIBUTE_MAP = {
    'bgp-speakers': {
        'local_as': {'allow_post': True, 'allow_put': False,
                     'validate': {'type:range': (bgp_consts.MIN_ASNUM,
                                                 bgp_consts.MAX_4BYTE_ASNUM)},
                     'is_visible': True, 'default': None,
                     'required_by_policy': False,
                     'enforce_policy': False}
    },
    'bgp-peers': {
        'remote_as': {'allow_post': True, 'allow_put': False,
                     'validate': {'type:range': (bgp_consts.MIN_ASNUM,
                                                 bgp_consts.MAX_4BYTE_ASNUM)},
                     'is_visible': True, 'default': None,
                     'required_by_policy': False,
                     'enforce_policy': False}
    }
}


class Bgp_4byte_asn(api_extensions.ExtensionDescriptor):
    """Extension class supporting bgp 4-byte AS numbers.
    """
    @classmethod
    def get_name(cls):
        return "BGP 4-byte AS numbers"

    @classmethod
    def get_alias(cls):
        return BGP_4BYTE_ASN_EXT_ALIAS

    @classmethod
    def get_description(cls):
        return "Support bgp 4-byte AS numbers"

    @classmethod
    def get_updated(cls):
        return "2017-09-07T00:00:00-00:00"

    @classmethod
    def get_resources(cls):
        return []

    def get_extended_resources(self, version):
        if version == "2.0":
            return RESOURCE_ATTRIBUTE_MAP
        else:
            return {}

    def get_required_extensions(self):
        return [bgp_ext.BGP_EXT_ALIAS]
