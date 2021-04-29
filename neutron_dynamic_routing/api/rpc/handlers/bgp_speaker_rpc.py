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

from neutron_lib.api.definitions import bgp as bgp_ext
from neutron_lib.plugins import directory
import oslo_messaging


class BgpSpeakerRpcCallback(object):
    """BgpDrAgent RPC callback in plugin implementations.

    This class implements the server side of an RPC interface.
    The client side of this interface can be found in
    neutron_dynamic_routing.services.bgp.agent.bgp_dragent.BgpDrPluginApi.
    For more information about changing RPC interfaces,
    see https://docs.openstack.org/neutron/latest/
    contributor/internals/rpc_api.html.
    """

    # API version history:
    # 1.0 BGPDRPluginApi BASE_RPC_API_VERSION
    target = oslo_messaging.Target(version='1.0')

    @property
    def plugin(self):
        if not hasattr(self, '_plugin'):
            self._plugin = directory.get_plugin(bgp_ext.ALIAS)
        return self._plugin

    def get_bgp_speaker_info(self, context, bgp_speaker_id):
        """Return BGP Speaker details such as peer list and local_as.

        Invoked by the BgpDrAgent to lookup the details of a BGP Speaker.
        """
        return self.plugin.get_bgp_speaker_with_advertised_routes(
                                context, bgp_speaker_id)

    def get_bgp_peer_info(self, context, bgp_peer_id):
        """Return BgpPeer details such as IP, remote_as, and credentials.

        Invoked by the BgpDrAgent to lookup the details of a BGP peer.
        """
        return self.plugin.get_bgp_peer(context, bgp_peer_id,
                                        ['peer_ip', 'remote_as',
                                         'auth_type', 'password'])

    def get_bgp_speakers(self, context, host=None, **kwargs):
        """Returns the list of all BgpSpeakers.

        Typically invoked by the BgpDrAgent as part of its bootstrap process.
        """
        return self.plugin.get_bgp_speakers_for_agent_host(context, host)
