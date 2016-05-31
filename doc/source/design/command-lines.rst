..
      Copyright 2016 Huawei Technologies India Pvt Limited.

      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.


      Convention for heading levels in Neutron devref:
      =======  Heading 0 (reserved for the title in a document)
      -------  Heading 1
      ~~~~~~~  Heading 2
      +++++++  Heading 3
      '''''''  Heading 4
      (Avoid deeper levels because they do not render well.)

Command Lines
=============

Neutron client has provided the command-line interfaces (CLI) to realize dynamic routing
services supported by neutron-dynamic-routing project.

Current implementation only supports the command line interfaces for BGP functionality.
For query on what specific :command:`neutron bgp` commands are supported,
enter:

.. code-block:: console

    $ neutron help | grep bgp

BGP
---

BGP Speaker Create
~~~~~~~~~~~~~~~~~~

.. code-block:: console

    usage: neutron bgp-speaker-create [-h]
                                      [-f {html,json,json,shell,table,value,yaml,yaml}]
                                      [-c COLUMN] [--max-width <integer>]
                                      [--noindent] [--prefix PREFIX]
                                      [--request-format {json}]
                                      [--tenant-id TENANT_ID] --local-as LOCAL_AS
                                      [--ip-version {4,6}]
                                      [--advertise-floating-ip-host-routes {True,False}]
                                      [--advertise-tenant-networks {True,False}]
                                      NAME

Create a BGP Speaker with a specified NAME.

Positional Arguments
++++++++++++++++++++

``NAME``
  Name of the BGP speaker to create.

Optional Arguments
++++++++++++++++++

``-h, --help``
  show this help message and exit

``--local-as LOCAL_AS``
  Local AS number. (Integer in [1, 65535] is allowed.)

``--ip-version {4,6}``
  IP version for the BGP speaker (default is 4)

``--advertise-floating-ip-host-routes {True,False}``
  Whether to enable or disable the advertisement of
  floating-ip host routes by the BGP speaker. By default
  floating ip host routes will be advertised by the BGP
  speaker.

``--advertise-tenant-networks {True,False}``
  Whether to enable or disable the advertisement of
  tenant network routes by the BGP speaker. By default
  tenant network routes will be advertised by the BGP
  speaker.

BGP Speaker List
~~~~~~~~~~~~~~~~

.. code-block:: console

    usage: neutron bgp-speaker-list [-h]
                                    [-f {csv,html,json,json,table,value,yaml,yaml}]
                                    [-c COLUMN] [--max-width <integer>]
                                    [--noindent]
                                    [--quote {all,minimal,none,nonnumeric}]
                                    [--request-format {json}] [-D] [-F FIELD]
                                    [-P SIZE] [--sort-key FIELD]
                                    [--sort-dir {asc,desc}]

List BGP speakers.

Optional Arguments
++++++++++++++++++

``-h, --help``
  show this help message and exit

``-D, --show-details``
  Show detailed information.

``-F FIELD, --field FIELD``
  Specify the field(s) to be returned by server. You can
  repeat this option.

BGP Speaker Show
----------------

.. code-block:: console

    usage: neutron bgp-speaker-show [-h]
                                    [-f {html,json,json,shell,table,value,yaml,yaml}]
                                    [-c COLUMN] [--max-width <integer>]
                                    [--noindent] [--prefix PREFIX]
                                    [--request-format {json}] [-D] [-F FIELD]
                                    BGP_SPEAKER

Show information of a given BGP speaker.

Positional Arguments
++++++++++++++++++++

``BGP_SPEAKER``
  ID or name of the BGP speaker to look up.

Optional Arguments
++++++++++++++++++

``-h, --help``
  show this help message and exit

``-D, --show-details``
  Show detailed information.

``-F FIELD, --field FIELD``
  Specify the field(s) to be returned by server. You can
  repeat this option.

BGP Speaker Delete
~~~~~~~~~~~~~~~~~~

.. code-block:: console

    usage: neutron bgp-speaker-delete [-h] [--request-format {json}] BGP_SPEAKER

Delete a BGP speaker.

Positional Arguments
++++++++++++++++++++

``BGP_SPEAKER``
  ID or name of the BGP speaker to delete.

Optional Arguments
++++++++++++++++++

``-h, --help``
  show this help message and exit

BGP Speaker Update
~~~~~~~~~~~~~~~~~~

.. code-block:: console

    usage: neutron bgp-speaker-update [-h] [--request-format {json}] [--name NAME]
                                      [--advertise-floating-ip-host-routes {True,False}]
                                      [--advertise-tenant-networks {True,False}]
                                      BGP_SPEAKER

Update BGP Speaker's information.

Positional Arguments
++++++++++++++++++++

``BGP_SPEAKER``
  ID or name of the BGP speaker to update.

Optional Arguments
++++++++++++++++++

``-h, --help``
  show this help message and exit

``--name NAME``
  Name of the BGP speaker to update.

``--advertise-floating-ip-host-routes {True,False}``
  Whether to enable or disable the advertisement of
  floating-ip host routes by the BGP speaker. By default
  floating ip host routes will be advertised by the BGP
  speaker.

``--advertise-tenant-networks {True,False}``
  Whether to enable or disable the advertisement of
  tenant network routes by the BGP speaker. By default
  tenant network routes will be advertised by the BGP
  speaker.

Add Network to BGP Speaker
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    usage: neutron bgp-speaker-network-add [-h] [--request-format {json}]
                                           BGP_SPEAKER NETWORK

Add a network to the BGP speaker.

Positional Arguments
++++++++++++++++++++

``BGP_SPEAKER``
  ID or name of the BGP speaker.

``NETWORK``
  ID or name of the network to add.

Optional Arguments
++++++++++++++++++

``-h, --help``
  show this help message and exit

Delete Network from BGP Speaker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    usage: neutron bgp-speaker-network-remove [-h] [--request-format {json}]
                                              BGP_SPEAKER NETWORK

Remove a network from the BGP speaker.

Positional Arguments
++++++++++++++++++++

``BGP_SPEAKER``
  ID or name of the BGP speaker.

``NETWORK``
  ID or name of the network to remove.

Optional Arguments
++++++++++++++++++

``-h, --help``
  show this help message and exit

BGP Advertised Routes List
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    usage: neutron bgp-speaker-advertiseroute-list [-h]
                                                   [-f {csv,html,json,json,table,value,yaml,yaml}]
                                                   [-c COLUMN]
                                                   [--max-width <integer>]
                                                   [--noindent]
                                                   [--quote {all,minimal,none,nonnumeric}]
                                                   [--request-format {json}] [-D]
                                                   [-F FIELD] [-P SIZE]
                                                   [--sort-key FIELD]
                                                   [--sort-dir {asc,desc}]
                                                   BGP_SPEAKER

List routes advertised by a given BGP speaker.

Positional Arguments
++++++++++++++++++++

``BGP_SPEAKER``
  ID or name of the BGP speaker.

Optional Arguments
++++++++++++++++++

``-h, --help``
  show this help message and exit

``-D, --show-details``
  Show detailed information.

``-F FIELD, --field FIELD``
  Specify the field(s) to be returned by server. You can
  repeat this option.

BGP Peer Create
~~~~~~~~~~~~~~~

.. code-block:: console

    usage: neutron bgp-peer-create [-h]
                                   [-f {html,json,json,shell,table,value,yaml,yaml}]
                                   [-c COLUMN] [--max-width <integer>]
                                   [--noindent] [--prefix PREFIX]
                                   [--request-format {json}]
                                   [--tenant-id TENANT_ID] --peer-ip
                                   PEER_IP_ADDRESS --remote-as PEER_REMOTE_AS
                                   [--auth-type PEER_AUTH_TYPE]
                                   [--password AUTH_PASSWORD]
                                   NAME

Create a BGP Peer.

positional Arguments
++++++++++++++++++++

``NAME``
  Name of the BGP peer to create

``--peer-ip PEER_IP_ADDRESS``
  Peer IP address.

``--remote-as PEER_REMOTE_AS``
  Peer AS number. (Integer in [1, 65535] is allowed.)

Optional Arguments
++++++++++++++++++

``-h, --help``
  show this help message and exit

``--auth-type PEER_AUTH_TYPE``
  Authentication algorithm. Supported algorithms:
  none(default), md5

``--password AUTH_PASSWORD``
  Authentication password.

BGP Peer List
~~~~~~~~~~~~~

.. code-block:: console

    usage: neutron bgp-peer-list [-h]
                                 [-f {csv,html,json,json,table,value,yaml,yaml}]
                                 [-c COLUMN] [--max-width <integer>] [--noindent]
                                 [--quote {all,minimal,none,nonnumeric}]
                                 [--request-format {json}] [-D] [-F FIELD]
                                 [-P SIZE] [--sort-key FIELD]
                                 [--sort-dir {asc,desc}]

List BGP peers.

Optional Arguments
++++++++++++++++++

``-h, --help``
  show this help message and exit

``-D, --show-details``
  Show detailed information.

``-F FIELD, --field FIELD``
  Specify the field(s) to be returned by server. You can
  repeat this option.

BGP Peer Show
~~~~~~~~~~~~~

.. code-block:: console

    usage: neutron bgp-peer-show [-h]
                                 [-f {html,json,json,shell,table,value,yaml,yaml}]
                                 [-c COLUMN] [--max-width <integer>] [--noindent]
                                 [--prefix PREFIX] [--request-format {json}] [-D]
                                 [-F FIELD]
                                 BGP_PEER

Show information of a given BGP peer.

Positional Arguments
++++++++++++++++++++

``BGP_PEER``
  ID or name of the BGP peer to look up.

Optional Arguments
++++++++++++++++++

``-h, --help``
  show this help message and exit

``-D, --show-details``
  Show detailed information.

``-F FIELD, --field FIELD``
  Specify the field(s) to be returned by server. You can
  repeat this option.

BGP Peer Delete
~~~~~~~~~~~~~~~

.. code-block:: console

    usage: neutron bgp-peer-delete [-h] [--request-format {json}] BGP_PEER

Delete a BGP peer.

Positional Arguments
++++++++++++++++++++

``BGP_PEER``
  ID or name of the BGP peer to delete.

Optional Arguments
++++++++++++++++++

``-h, --help``
  show this help message and exit

BGP Peer Update
~~~~~~~~~~~~~~~

.. code-block:: console

    usage: neutron bgp-peer-update [-h] [--request-format {json}] [--name NAME]
                                   [--password AUTH_PASSWORD]
                                   BGP_PEER

Update BGP Peer's information.

Positional Arguments
++++++++++++++++++++

``BGP_PEER``
  ID or name of the BGP peer to update.

Optional Arguments
++++++++++++++++++

``-h, --help``
  show this help message and exit

``--name NAME``
  Updated name of the BGP peer.

``--password AUTH_PASSWORD``
  Updated authentication password.

Add Peer to BGP Speaker
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    usage: neutron bgp-speaker-peer-add [-h] [--request-format {json}]
                                        BGP_SPEAKER BGP_PEER

Add a peer to the BGP speaker.

Positional Arguments
++++++++++++++++++++

``BGP_SPEAKER``
  ID or name of the BGP speaker.

``BGP_PEER``
  ID or name of the BGP peer to add.

Optional Arguments
++++++++++++++++++

``-h, --help``
  show this help message and exit

Delete Peer from BGP Speaker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    usage: neutron bgp-speaker-peer-remove [-h] [--request-format {json}]
                                           BGP_SPEAKER BGP_PEER

Remove a peer from the BGP speaker.

Positional Arguments
++++++++++++++++++++

``BGP_SPEAKER``
  ID or name of the BGP speaker.

``BGP_PEER``
  ID or name of the BGP peer to remove.

Optional Arguments
++++++++++++++++++

``-h, --help``
  show this help message and exit

Add BGP Speaker to Dynamic Routing Agent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    usage: neutron bgp-dragent-speaker-add [-h] [--request-format {json}]
                                           BGP_DRAGENT_ID BGP_SPEAKER

Add a BGP speaker to a Dynamic Routing agent.

Positional Arguments
++++++++++++++++++++

``BGP_DRAGENT_ID``
  ID of the Dynamic Routing agent.

``BGP_SPEAKER``
  ID or name of the BGP speaker.

Optional Arguments
++++++++++++++++++

``-h, --help``
  show this help message and exit

Delete BGP Speaker from Dynamic Routing Agent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    usage: neutron bgp-dragent-speaker-remove [-h] [--request-format {json}]
                                              BGP_DRAGENT_ID BGP_SPEAKER

Removes a BGP speaker from a Dynamic Routing agent.

Positional Arguments
++++++++++++++++++++

``BGP_DRAGENT_ID``
  ID of the Dynamic Routing agent.

``BGP_SPEAKER``
  ID or name of the BGP speaker.

Optional Arguments
++++++++++++++++++

``-h, --help``
  show this help message and exit

List BGP Speakers hosted by a Dynamic Routing Agent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    usage: neutron bgp-speaker-list-on-dragent [-h]
                                               [-f {csv,html,json,json,table,value,yaml,yaml}]
                                               [-c COLUMN] [--max-width <integer>]
                                               [--noindent]
                                               [--quote {all,minimal,none,nonnumeric}]
                                               [--request-format {json}] [-D]
                                               [-F FIELD]
                                               BGP_DRAGENT_ID

List BGP speakers hosted by a Dynamic Routing agent.

Positional Arguments
++++++++++++++++++++

``BGP_DRAGENT_ID``
  ID of the Dynamic Routing agent.

Optional Arguments
++++++++++++++++++

``-h, --help``
  show this help message and exit

``-D, --show-details``
  Show detailed information.

``-F FIELD, --field FIELD``
  Specify the field(s) to be returned by server. You can
  repeat this option.

List Dynamic Routing Agents Hosting a BGP Speaker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    usage: neutron bgp-dragent-list-hosting-speaker [-h]
                                                    [-f {csv,html,json,json,table,value,yaml,yaml}]
                                                    [-c COLUMN]
                                                    [--max-width <integer>]
                                                    [--noindent]
                                                    [--quote {all,minimal,none,nonnumeric}]
                                                    [--request-format {json}] [-D]
                                                    [-F FIELD]
                                                    BGP_SPEAKER

List Dynamic Routing agents hosting a BGP speaker.

Positional Arguments
++++++++++++++++++++

``BGP_SPEAKER``
  ID or name of the BGP speaker.

Optional Arguments
++++++++++++++++++

``-h, --help``
  show this help message and exit

``-D, --show-details``
  Show detailed information.

``-F FIELD, --field FIELD``
  Specify the field(s) to be returned by server. You can
  repeat this option.