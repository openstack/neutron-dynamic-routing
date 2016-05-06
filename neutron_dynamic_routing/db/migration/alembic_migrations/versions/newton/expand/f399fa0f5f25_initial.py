#    Copyright 2016 Huawei Technologies India Pvt Limited.
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
#

"""initial

Revision ID: f399fa0f5f25
Revises: None
Create Date: 2016-05-03 08:30:18.421995

"""

from neutron.db import migration
from neutron.db.migration import cli

# revision identifiers, used by Alembic.
revision = 'f399fa0f5f25'
down_revision = 'start_neutron_dynamic_routing'
branch_labels = (cli.EXPAND_BRANCH,)

# milestone identifier, used by neutron-db-manage
neutron_milestone = [migration.NEWTON]


def upgrade():
    pass
