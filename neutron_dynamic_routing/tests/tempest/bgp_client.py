# Copyright 2016 Hewlett Packard Enterprise Development Company LP
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

from oslo_serialization import jsonutils
from tempest.lib.common import rest_client


class BgpSpeakerClientJSON(rest_client.RestClient):

    def create_bgp_speaker(self, post_data):
        post_body = jsonutils.dumps(post_data)
        resp, body = self.post('v2.0/bgp-speakers', post_body)
        body = jsonutils.loads(body)
        self.expected_success(201, resp.status)
        return rest_client.ResponseBody(resp, body)

    def get_bgp_speaker(self, id):
        uri = 'v2.0/bgp-speakers/{0}'.format(id)
        resp, body = self.get(uri)
        body = jsonutils.loads(body)
        self.expected_success(200, resp.status)
        return rest_client.ResponseBody(resp, body)

    def get_bgp_speakers(self):
        uri = self.get_uri("bgp-speakers")
        resp, body = self.get(uri)
        body = jsonutils.loads(body)
        self.expected_success(200, resp.status)
        return rest_client.ResponseBodyList(resp, body)

    def update_bgp_speaker(self, id, put_data):
        uri = 'v2.0/bgp-speakers/{0}'.format(id)
        update_body = {'bgp_speaker': put_data}
        update_body = jsonutils.dumps(update_body)
        resp, body = self.put(uri, update_body)
        body = jsonutils.loads(body)
        self.expected_success(200, resp.status)
        return rest_client.ResponseBody(resp, body)

    def delete_bgp_speaker(self, id):
        uri = 'v2.0/bgp-speakers/{0}'.format(id)
        resp, body = self.delete(uri)
        self.expected_success(204, resp.status)
        return rest_client.ResponseBody(resp, body)

    def create_bgp_peer(self, post_data):
        post_body = jsonutils.dumps(post_data)
        resp, body = self.post('v2.0/bgp-peers', post_body)
        body = jsonutils.loads(body)
        self.expected_success(201, resp.status)
        return rest_client.ResponseBody(resp, body)

    def get_bgp_peer(self, id):
        uri = 'v2.0/bgp-peers/{0}'.format(id)
        resp, body = self.get(uri)
        body = jsonutils.loads(body)
        self.expected_success(200, resp.status)
        return rest_client.ResponseBody(resp, body)

    def delete_bgp_peer(self, id):
        uri = 'v2.0/bgp-peers/{0}'.format(id)
        resp, body = self.delete(uri)
        self.expected_success(204, resp.status)
        return rest_client.ResponseBody(resp, body)

    def add_bgp_peer_with_id(self, bgp_speaker_id, bgp_peer_id):
        uri = 'v2.0/bgp-speakers/%s/add_bgp_peer' % bgp_speaker_id
        update_body = {"bgp_peer_id": bgp_peer_id}
        update_body = jsonutils.dumps(update_body)
        resp, body = self.put(uri, update_body)
        self.expected_success(200, resp.status)
        body = jsonutils.loads(body)
        return rest_client.ResponseBody(resp, body)

    def remove_bgp_peer_with_id(self, bgp_speaker_id, bgp_peer_id):
        uri = 'v2.0/bgp-speakers/%s/remove_bgp_peer' % bgp_speaker_id
        update_body = {"bgp_peer_id": bgp_peer_id}
        update_body = jsonutils.dumps(update_body)
        resp, body = self.put(uri, update_body)
        self.expected_success(200, resp.status)
        body = jsonutils.loads(body)
        return rest_client.ResponseBody(resp, body)

    def add_bgp_gateway_network(self, bgp_speaker_id, network_id):
        uri = 'v2.0/bgp-speakers/%s/add_gateway_network' % bgp_speaker_id
        update_body = {"network_id": network_id}
        update_body = jsonutils.dumps(update_body)
        resp, body = self.put(uri, update_body)
        self.expected_success(200, resp.status)
        body = jsonutils.loads(body)
        return rest_client.ResponseBody(resp, body)

    def remove_bgp_gateway_network(self, bgp_speaker_id, network_id):
        uri = 'v2.0/bgp-speakers/%s/remove_gateway_network' % bgp_speaker_id
        update_body = {"network_id": network_id}
        update_body = jsonutils.dumps(update_body)
        resp, body = self.put(uri, update_body)
        self.expected_success(200, resp.status)
        body = jsonutils.loads(body)
        return rest_client.ResponseBody(resp, body)

    def get_bgp_advertised_routes(self, bgp_speaker_id):
        base_uri = 'v2.0/bgp-speakers/%s/get_advertised_routes'
        uri = base_uri % bgp_speaker_id
        resp, body = self.get(uri)
        body = jsonutils.loads(body)
        self.expected_success(200, resp.status)
        return rest_client.ResponseBody(resp, body)

    def list_dragents_for_bgp_speaker(self, bgp_speaker_id):
        uri = 'v2.0/bgp-speakers/%s/bgp-dragents' % bgp_speaker_id
        resp, body = self.get(uri)
        self.expected_success(200, resp.status)
        body = jsonutils.loads(body)
        return rest_client.ResponseBody(resp, body)

    def add_bgp_speaker_to_dragent(self, agent_id, bgp_speaker_id):
        uri = 'v2.0/agents/%s/bgp-drinstances' % agent_id
        update_body = {"bgp_speaker_id": bgp_speaker_id}
        update_body = jsonutils.dumps(update_body)
        resp, body = self.post(uri, update_body)
        self.expected_success(201, resp.status)
        body = jsonutils.loads(body)
        return rest_client.ResponseBody(resp, body)

    def remove_bgp_speaker_from_dragent(self, agent_id, bgp_speaker_id):
        uri = 'v2.0/agents/%s/bgp-drinstances/%s' % (agent_id, bgp_speaker_id)
        resp, body = self.delete(uri)
        self.expected_success(204, resp.status)
        return rest_client.ResponseBody(resp, body)
