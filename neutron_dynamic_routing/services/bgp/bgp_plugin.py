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

from netaddr import IPAddress

from neutron_lib.api.definitions import bgp as bgp_ext
from neutron_lib.api.definitions import bgp_4byte_asn
from neutron_lib.api.definitions import bgp_dragentscheduler as dras_ext
from neutron_lib.api.definitions import portbindings
from neutron_lib.callbacks import events
from neutron_lib.callbacks import registry
from neutron_lib.callbacks import resources
from neutron_lib import constants as n_const
from neutron_lib import context
from neutron_lib import rpc as n_rpc
from neutron_lib.services import base as service_base
from oslo_config import cfg
from oslo_log import log as logging
from oslo_utils import importutils

from neutron_dynamic_routing.api.rpc.agentnotifiers import bgp_dr_rpc_agent_api  # noqa
from neutron_dynamic_routing.api.rpc.callbacks import resources as dr_resources
from neutron_dynamic_routing.api.rpc.handlers import bgp_speaker_rpc as bs_rpc
from neutron_dynamic_routing.db import bgp_db
from neutron_dynamic_routing.db import bgp_dragentscheduler_db
from neutron_dynamic_routing.services.bgp.common import constants as bgp_consts

PLUGIN_NAME = bgp_ext.ALIAS + '_svc_plugin'
LOG = logging.getLogger(__name__)


class BgpPlugin(service_base.ServicePluginBase,
                bgp_db.BgpDbMixin,
                bgp_dragentscheduler_db.BgpDrAgentSchedulerDbMixin):

    supported_extension_aliases = [bgp_ext.ALIAS,
                                   dras_ext.ALIAS,
                                   bgp_4byte_asn.ALIAS]

    def __init__(self):
        super(BgpPlugin, self).__init__()
        self.bgp_drscheduler = importutils.import_object(
            cfg.CONF.bgp_drscheduler_driver)
        self.agent_notifiers[bgp_consts.AGENT_TYPE_BGP_ROUTING] = (
            bgp_dr_rpc_agent_api.BgpDrAgentNotifyApi()
        )
        self._bgp_rpc = self.agent_notifiers[bgp_consts.AGENT_TYPE_BGP_ROUTING]
        self._register_callbacks()
        self.add_periodic_dragent_status_check()

    def get_plugin_type(self):
        return bgp_ext.ALIAS

    def get_plugin_description(self):
        """returns string description of the plugin."""
        return ("BGP dynamic routing service for announcement of next-hops "
                "for project networks, floating IP's, and DVR host routes.")

    def start_rpc_listeners(self):
        self.topic = bgp_consts.BGP_PLUGIN
        self.conn = n_rpc.Connection()
        self.endpoints = [bs_rpc.BgpSpeakerRpcCallback()]
        self.conn.create_consumer(self.topic, self.endpoints,
                                  fanout=False)
        return self.conn.consume_in_threads()

    def _register_callbacks(self):
        registry.subscribe(self.floatingip_update_callback,
                           resources.FLOATING_IP,
                           events.AFTER_CREATE)
        registry.subscribe(self.floatingip_update_callback,
                           resources.FLOATING_IP,
                           events.AFTER_UPDATE)
        registry.subscribe(self.router_interface_callback,
                           resources.ROUTER_INTERFACE,
                           events.AFTER_CREATE)
        registry.subscribe(self.router_interface_callback,
                           resources.ROUTER_INTERFACE,
                           events.BEFORE_CREATE)
        registry.subscribe(self.router_interface_callback,
                           resources.ROUTER_INTERFACE,
                           events.AFTER_DELETE)
        registry.subscribe(self.router_gateway_callback,
                           resources.ROUTER_GATEWAY,
                           events.AFTER_CREATE)
        registry.subscribe(self.router_gateway_callback,
                           resources.ROUTER_GATEWAY,
                           events.AFTER_DELETE)
        registry.subscribe(self.port_callback,
                           resources.PORT,
                           events.AFTER_UPDATE)

    def get_bgp_speakers(self, context, filters=None, fields=None,
                         sorts=None, limit=None, marker=None,
                         page_reverse=False):
        return super(BgpPlugin, self).get_bgp_speakers(
                                                    context,
                                                    filters=filters,
                                                    fields=fields,
                                                    sorts=sorts,
                                                    limit=limit,
                                                    marker=marker,
                                                    page_reverse=page_reverse)

    def get_bgp_speaker(self, context, bgp_speaker_id, fields=None):
        return super(BgpPlugin, self).get_bgp_speaker(context,
                                                      bgp_speaker_id,
                                                      fields=fields)

    def create_bgp_speaker(self, context, bgp_speaker):
        bgp_speaker = super(BgpPlugin, self).create_bgp_speaker(context,
                                                                bgp_speaker)
        registry.publish(dr_resources.BGP_SPEAKER, events.AFTER_CREATE,
                         self, payload=events.DBEventPayload(
                                   context,
                                   metadata={'plugin': self},
                                   states=(bgp_speaker,)))
        return bgp_speaker

    def update_bgp_speaker(self, context, bgp_speaker_id, bgp_speaker):
        return super(BgpPlugin, self).update_bgp_speaker(context,
                                                         bgp_speaker_id,
                                                         bgp_speaker)

    def delete_bgp_speaker(self, context, bgp_speaker_id):
        hosted_bgp_dragents = self.get_dragents_hosting_bgp_speakers(
                                                             context,
                                                             [bgp_speaker_id])
        super(BgpPlugin, self).delete_bgp_speaker(context, bgp_speaker_id)
        for agent in hosted_bgp_dragents:
            self._bgp_rpc.bgp_speaker_removed(context,
                                              bgp_speaker_id,
                                              agent.host)

    def get_bgp_peers(self, context, fields=None, filters=None, sorts=None,
                      limit=None, marker=None, page_reverse=False):
        return super(BgpPlugin, self).get_bgp_peers(
                                                 context, fields=fields,
                                                 filters=filters, sorts=sorts,
                                                 limit=limit, marker=marker,
                                                 page_reverse=page_reverse)

    def get_bgp_peer(self, context, bgp_peer_id, fields=None):
        return super(BgpPlugin, self).get_bgp_peer(context,
                                                   bgp_peer_id,
                                                   fields=fields)

    def create_bgp_peer(self, context, bgp_peer):
        return super(BgpPlugin, self).create_bgp_peer(context, bgp_peer)

    def update_bgp_peer(self, context, bgp_peer_id, bgp_peer):
        return super(BgpPlugin, self).update_bgp_peer(context,
                                                      bgp_peer_id,
                                                      bgp_peer)

    def delete_bgp_peer(self, context, bgp_peer_id):
        super(BgpPlugin, self).delete_bgp_peer(context, bgp_peer_id)

    def add_bgp_peer(self, context, bgp_speaker_id, bgp_peer_info):
        ret_value = super(BgpPlugin, self).add_bgp_peer(context,
                                                        bgp_speaker_id,
                                                        bgp_peer_info)
        hosted_bgp_dragents = self.get_dragents_hosting_bgp_speakers(
                                                             context,
                                                             [bgp_speaker_id])
        for agent in hosted_bgp_dragents:
            self._bgp_rpc.bgp_peer_associated(context, bgp_speaker_id,
                                              ret_value['bgp_peer_id'],
                                              agent.host)
        return ret_value

    def remove_bgp_peer(self, context, bgp_speaker_id, bgp_peer_info):
        hosted_bgp_dragents = self.get_dragents_hosting_bgp_speakers(
            context, [bgp_speaker_id])

        ret_value = super(BgpPlugin, self).remove_bgp_peer(context,
                                                           bgp_speaker_id,
                                                           bgp_peer_info)

        for agent in hosted_bgp_dragents:
            self._bgp_rpc.bgp_peer_disassociated(context,
                                                 bgp_speaker_id,
                                                 ret_value['bgp_peer_id'],
                                                 agent.host)

    def add_bgp_speaker_to_dragent(self, context, agent_id, speaker_id):
        super(BgpPlugin, self).add_bgp_speaker_to_dragent(context,
                                                          agent_id,
                                                          speaker_id)

    def remove_bgp_speaker_from_dragent(self, context, agent_id, speaker_id):
        super(BgpPlugin, self).remove_bgp_speaker_from_dragent(context,
                                                               agent_id,
                                                               speaker_id)

    def list_bgp_speaker_on_dragent(self, context, agent_id):
        return super(BgpPlugin, self).list_bgp_speaker_on_dragent(context,
                                                                  agent_id)

    def list_dragent_hosting_bgp_speaker(self, context, speaker_id):
        return super(BgpPlugin, self).list_dragent_hosting_bgp_speaker(
                                                                   context,
                                                                   speaker_id)

    def add_gateway_network(self, context, bgp_speaker_id, network_info):
        return super(BgpPlugin, self).add_gateway_network(context,
                                                          bgp_speaker_id,
                                                          network_info)

    def remove_gateway_network(self, context, bgp_speaker_id, network_info):
        return super(BgpPlugin, self).remove_gateway_network(context,
                                                             bgp_speaker_id,
                                                             network_info)

    def get_advertised_routes(self, context, bgp_speaker_id):
        return super(BgpPlugin, self).get_advertised_routes(context,
                                                            bgp_speaker_id)

    def floatingip_update_callback(self, resource, event, trigger, payload):
        if event not in [events.AFTER_CREATE, events.AFTER_UPDATE]:
            return
        ctx = context.get_admin_context()
        new_fip = payload.latest_state
        new_router_id = new_fip['router_id']
        floating_ip_address = new_fip['floating_ip_address']
        dest = str(floating_ip_address) + '/32'
        bgp_speakers = self._bgp_speakers_for_gw_network_by_family(
            ctx,
            new_fip['floating_network_id'],
            n_const.IP_VERSION_4)
        last_router_id = None
        if event == events.AFTER_UPDATE:
            old_fip = payload.states[0]
            last_router_id = old_fip['router_id']

        if last_router_id and new_router_id != last_router_id:
            # Here gives the old route next_hop a `None` value, then
            # the DR agent side will withdraw it.
            old_host_route = {'destination': dest, 'next_hop': None}
            for bgp_speaker in bgp_speakers:
                self.stop_route_advertisements(ctx, self._bgp_rpc,
                                               bgp_speaker.id,
                                               [old_host_route])

        if new_router_id and new_router_id != last_router_id:
            next_hop = self._get_fip_next_hop(
                ctx, new_router_id, floating_ip_address)
            new_host_route = {'destination': dest, 'next_hop': next_hop}
            for bgp_speaker in bgp_speakers:
                self.start_route_advertisements(ctx, self._bgp_rpc,
                                                bgp_speaker.id,
                                                [new_host_route])

    def router_interface_callback(self, resource, event, trigger,
                                  payload=None):
        if event == events.AFTER_CREATE:
            self._handle_router_interface_after_create(payload)
        if event == events.AFTER_DELETE:
            gw_network = payload.metadata.get('network_id')
            next_hops = self._next_hops_from_gateway_ips(
                payload.metadata.get('gateway_ips'))
            ctx = context.get_admin_context()
            speakers = self._bgp_speakers_for_gateway_network(ctx, gw_network)
            for speaker in speakers:
                routes = self._route_list_from_prefixes_and_next_hop(
                    payload.metadata['cidrs'], next_hops[speaker.ip_version])
                self._handle_router_interface_after_delete(gw_network, routes)

    def _handle_router_interface_after_create(self, payload):
        gw_network = payload.metadata.get('network_id')
        if not gw_network:
            return

        ctx = context.get_admin_context()
        with ctx.session.begin(subtransactions=True):
            speakers = self._bgp_speakers_for_gateway_network(ctx,
                                                              gw_network)
            next_hops = self._next_hops_from_gateway_ips(
                payload.metadata.get('gateway_ips'))

            for speaker in speakers:
                prefixes = self._tenant_prefixes_by_router(
                    ctx, payload.resource_id, speaker.id)
                next_hop = next_hops.get(speaker.ip_version)
                if next_hop:
                    rl = self._route_list_from_prefixes_and_next_hop(prefixes,
                                                                     next_hop)
                    self.start_route_advertisements(ctx,
                                                    self._bgp_rpc,
                                                    speaker.id,
                                                    rl)

    def router_gateway_callback(self, resource, event, trigger, payload=None):
        if event == events.AFTER_CREATE:
            self._handle_router_gateway_after_create(payload)
        if event == events.AFTER_DELETE:
            gw_network = payload.metadata.get('network_id')
            router_id = payload.resource_id
            next_hops = self._next_hops_from_gateway_ips(
                payload.metadata.get('gateway_ips'))
            ctx = context.get_admin_context()
            speakers = self._bgp_speakers_for_gateway_network(ctx, gw_network)
            for speaker in speakers:
                if speaker.ip_version in next_hops:
                    next_hop = next_hops[speaker.ip_version]
                    prefixes = self._tenant_prefixes_by_router(ctx,
                                                               router_id,
                                                               speaker.id)
                    routes = self._route_list_from_prefixes_and_next_hop(
                                                                     prefixes,
                                                                     next_hop)
                self._handle_router_interface_after_delete(gw_network, routes)

    def _handle_router_gateway_after_create(self, payload):
        ctx = context.get_admin_context()
        gw_network = payload.metadata.get('network_id')
        router_id = payload.resource_id
        with ctx.session.begin(subtransactions=True):
            speakers = self._bgp_speakers_for_gateway_network(ctx,
                                                              gw_network)
            next_hops = self._next_hops_from_gateway_ips(
                payload.metadata.get('gateway_ips'))

            for speaker in speakers:
                if speaker.ip_version in next_hops:
                    next_hop = next_hops[speaker.ip_version]
                    prefixes = self._tenant_prefixes_by_router(ctx,
                                                               router_id,
                                                               speaker.id)
                    routes = self._route_list_from_prefixes_and_next_hop(
                                                                     prefixes,
                                                                     next_hop)
                    self.start_route_advertisements(ctx, self._bgp_rpc,
                                                    speaker.id, routes)

    def _handle_router_interface_after_delete(self, gw_network, routes):
        if gw_network and routes:
            ctx = context.get_admin_context()
            speakers = self._bgp_speakers_for_gateway_network(ctx, gw_network)
            for speaker in speakers:
                self.stop_route_advertisements(ctx, self._bgp_rpc,
                                               speaker.id, routes)

    def port_callback(self, resource, event, trigger, payload):
        if event != events.AFTER_UPDATE:
            return

        original_port = payload.states[0]
        updated_port = payload.latest_state
        if not updated_port.get('fixed_ips'):
            return

        original_host = original_port.get(portbindings.HOST_ID)
        updated_host = updated_port.get(portbindings.HOST_ID)
        device_owner = updated_port.get('device_owner')

        # if host in the port binding has changed, update next-hops
        if original_host != updated_host and bool('compute:' in device_owner):
            ctx = context.get_admin_context()
            with ctx.session.begin(subtransactions=True):
                ext_nets = self.get_external_networks_for_port(ctx,
                                                               updated_port)
                for ext_net in ext_nets:
                    bgp_speakers = (
                        self._get_bgp_speaker_ids_by_binding_network(
                            ctx, ext_nets))

                    # Refresh any affected BGP speakers
                    for bgp_speaker in bgp_speakers:
                        routes = self.get_advertised_routes(ctx, bgp_speaker)
                        self.start_route_advertisements(ctx, self._bgp_rpc,
                                                        bgp_speaker, routes)

    def _next_hops_from_gateway_ips(self, gw_ips):
        if gw_ips:
            return {IPAddress(ip).version: ip for ip in gw_ips}
        return {}

    def start_route_advertisements(self, ctx, bgp_rpc,
                                   bgp_speaker_id, routes):
        agents = self.list_dragent_hosting_bgp_speaker(ctx, bgp_speaker_id)
        for agent in agents['agents']:
            bgp_rpc.bgp_routes_advertisement(ctx,
                                             bgp_speaker_id,
                                             routes,
                                             agent['host'])

        msg = "Starting route advertisements for %s on BgpSpeaker %s"
        self._debug_log_for_routes(msg, routes, bgp_speaker_id)

    def stop_route_advertisements(self, ctx, bgp_rpc,
                                  bgp_speaker_id, routes):
        agents = self.list_dragent_hosting_bgp_speaker(ctx, bgp_speaker_id)
        for agent in agents['agents']:
            bgp_rpc.bgp_routes_withdrawal(ctx,
                                          bgp_speaker_id,
                                          routes,
                                          agent['host'])

        msg = "Stopping route advertisements for %s on BgpSpeaker %s"
        self._debug_log_for_routes(msg, routes, bgp_speaker_id)

    def _debug_log_for_routes(self, msg, routes, bgp_speaker_id):

        # Could have a large number of routes passed, check log level first
        if LOG.isEnabledFor(logging.DEBUG):
            for route in routes:
                LOG.debug(msg, route, bgp_speaker_id)
