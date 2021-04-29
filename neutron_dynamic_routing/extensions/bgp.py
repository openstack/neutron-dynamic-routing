# Copyright 2016 Hewlett Packard Development Coompany LP
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
#

from neutron_lib.api.definitions import bgp as bgp_api_def
from neutron_lib.api import extensions as api_ext
from neutron_lib import exceptions as n_exc

from neutron.api.v2 import resource_helper as rh

from neutron_dynamic_routing._i18n import _


# Dynamic Routing Exceptions
class BgpSpeakerNotFound(n_exc.NotFound):
    message = _("BGP speaker %(id)s could not be found.")


class BgpPeerNotFound(n_exc.NotFound):
    message = _("BGP peer %(id)s could not be found.")


class BgpPeerNotAuthenticated(n_exc.NotFound):
    message = _("BGP peer %(bgp_peer_id)s not authenticated.")


class BgpSpeakerPeerNotAssociated(n_exc.NotFound):
    message = _("BGP peer %(bgp_peer_id)s is not associated with "
                "BGP speaker %(bgp_speaker_id)s.")


class BgpSpeakerNetworkNotAssociated(n_exc.NotFound):
    message = _("Network %(network_id)s is not associated with "
                "BGP speaker %(bgp_speaker_id)s.")


class BgpSpeakerNetworkBindingError(n_exc.Conflict):
    message = _("Network %(network_id)s is already bound to BgpSpeaker "
                "%(bgp_speaker_id)s.")


class NetworkNotBound(n_exc.NotFound):
    message = _("Network %(network_id)s is not bound to a BgpSpeaker.")


class DuplicateBgpPeerIpException(n_exc.Conflict):
    message = _("BGP Speaker %(bgp_speaker_id)s is already configured to "
                "peer with a BGP Peer at %(peer_ip)s, it cannot peer with "
                "BGP Peer %(bgp_peer_id)s.")


class InvalidBgpPeerMd5Authentication(n_exc.BadRequest):
    message = _("A password must be supplied when using auth_type md5.")


class NetworkNotBoundForIpVersion(NetworkNotBound):
    message = _("Network %(network_id)s is not bound to a IPv%(ip_version)s "
                "BgpSpeaker.")


class Bgp(api_ext.APIExtensionDescriptor):
    api_definition = bgp_api_def

    @classmethod
    def get_resources(cls):
        plural_mappings = rh.build_plural_mappings(
            {}, bgp_api_def.RESOURCE_ATTRIBUTE_MAP)
        exts = rh.build_resource_info(plural_mappings,
                                      bgp_api_def.RESOURCE_ATTRIBUTE_MAP,
                                      bgp_api_def.ALIAS,
                                      action_map=bgp_api_def.ACTION_MAP)

        return exts
