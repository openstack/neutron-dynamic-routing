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

import sys

from oslo_config import cfg
from oslo_service import service

from neutron.common import config as common_config
from neutron.conf.agent import common as config
from neutron import service as neutron_service

from neutron_dynamic_routing.services.bgp.agent import config as bgp_dragent_config  # noqa
from neutron_dynamic_routing.services.bgp.common import constants as bgp_consts  # noqa


def register_options():
    config.register_agent_state_opts_helper(cfg.CONF)
    config.register_root_helper(cfg.CONF)
    cfg.CONF.register_opts(bgp_dragent_config.BGP_DRIVER_OPTS, 'BGP')
    cfg.CONF.register_opts(bgp_dragent_config.BGP_PROTO_CONFIG_OPTS, 'BGP')
    config.register_external_process_opts(cfg.CONF)


def main():
    register_options()
    common_config.register_common_config_options()
    common_config.init(sys.argv[1:])
    config.setup_logging()
    server = neutron_service.Service.create(
        binary='neutron-bgp-dragent',
        topic=bgp_consts.BGP_DRAGENT,
        report_interval=cfg.CONF.AGENT.report_interval,
        manager='neutron_dynamic_routing.services.bgp.agent.bgp_dragent.'
                'BgpDrAgentWithStateReport')
    service.launch(cfg.CONF, server, restart_method='mutate').wait()
