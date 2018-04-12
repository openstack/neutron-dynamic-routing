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

"""change size of as number

Revision ID: a589fdb5724c
Revises: 4cf8bc3edb66
Create Date: 2017-08-31 13:50:28.324422

"""

from alembic import op
import sqlalchemy as sa

from neutron.db import migration


# revision identifiers, used by Alembic.
revision = 'a589fdb5724c'
down_revision = '4cf8bc3edb66'

# milestone identifier, used by neutron-db-manage
neutron_milestone = [migration.QUEENS]


def upgrade():
    op.alter_column('bgp_speakers', 'local_as', nullable=False,
                    type_=sa.BigInteger())
    op.alter_column('bgp_peers', 'remote_as', nullable=False,
                    type_=sa.BigInteger())
