========
BGP Peer
========

BGP Peer Create
---------------

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

**Positional arguments:**

``NAME``
  Name of the BGP peer to create

``--peer-ip PEER_IP_ADDRESS``
  Peer IP address.

``--remote-as PEER_REMOTE_AS``
  Peer AS number. (Integer in [1, 65535] is allowed.)

**Optional arguments:**

``-h, --help``
  show this help message and exit

``--auth-type PEER_AUTH_TYPE``
  Authentication algorithm. Supported algorithms:
  none(default), md5

``--password AUTH_PASSWORD``
  Authentication password.

BGP Peer List
-------------

.. code-block:: console

    usage: neutron bgp-peer-list [-h]
                                 [-f {csv,html,json,json,table,value,yaml,yaml}]
                                 [-c COLUMN] [--max-width <integer>] [--noindent]
                                 [--quote {all,minimal,none,nonnumeric}]
                                 [--request-format {json}] [-D] [-F FIELD]
                                 [-P SIZE] [--sort-key FIELD]
                                 [--sort-dir {asc,desc}]

List BGP peers.

**Optional arguments:**

``-h, --help``
  show this help message and exit

``-D, --show-details``
  Show detailed information.

``-F FIELD, --field FIELD``
  Specify the field(s) to be returned by server. You can
  repeat this option.

BGP Peer Show
-------------

.. code-block:: console

    usage: neutron bgp-peer-show [-h]
                                 [-f {html,json,json,shell,table,value,yaml,yaml}]
                                 [-c COLUMN] [--max-width <integer>] [--noindent]
                                 [--prefix PREFIX] [--request-format {json}] [-D]
                                 [-F FIELD]
                                 BGP_PEER

Show information of a given BGP peer.

**Positional arguments:**

``BGP_PEER``
  ID or name of the BGP peer to look up.

**Optional arguments:**

``-h, --help``
  show this help message and exit

``-D, --show-details``
  Show detailed information.

``-F FIELD, --field FIELD``
  Specify the field(s) to be returned by server. You can
  repeat this option.

BGP Peer Delete
---------------

.. code-block:: console

    usage: neutron bgp-peer-delete [-h] [--request-format {json}] BGP_PEER

Delete a BGP peer.

**Positional arguments:**

``BGP_PEER``
  ID or name of the BGP peer to delete.

**Optional arguments:**

``-h, --help``
  show this help message and exit

BGP Peer Update
---------------

.. code-block:: console

    usage: neutron bgp-peer-update [-h] [--request-format {json}] [--name NAME]
                                   [--password AUTH_PASSWORD]
                                   BGP_PEER

Update BGP Peer's information.

**Positional arguments:**

``BGP_PEER``
  ID or name of the BGP peer to update.

**Optional arguments:**

``-h, --help``
  show this help message and exit

``--name NAME``
  Updated name of the BGP peer.

``--password AUTH_PASSWORD``
  Updated authentication password.

Add Peer to BGP Speaker
-----------------------

.. code-block:: console

    usage: neutron bgp-speaker-peer-add [-h] [--request-format {json}]
                                        BGP_SPEAKER BGP_PEER

Add a peer to the BGP speaker.

**Positional arguments:**

``BGP_SPEAKER``
  ID or name of the BGP speaker.

``BGP_PEER``
  ID or name of the BGP peer to add.

**Optional arguments:**

``-h, --help``
  show this help message and exit

Delete Peer from BGP Speaker
----------------------------

.. code-block:: console

    usage: neutron bgp-speaker-peer-remove [-h] [--request-format {json}]
                                           BGP_SPEAKER BGP_PEER

Remove a peer from the BGP speaker.

**Positional arguments:**

``BGP_SPEAKER``
  ID or name of the BGP speaker.

``BGP_PEER``
  ID or name of the BGP peer to remove.

**Optional arguments:**

``-h, --help``
  show this help message and exit
