===========
BGP Speaker
===========

BGP Speaker Create
------------------

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

**Positional arguments:**

``NAME``
  Name of the BGP speaker to create.

**Optional arguments:**

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
----------------

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

**Optional arguments:**

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

**Positional arguments:**

``BGP_SPEAKER``
  ID or name of the BGP speaker to look up.

**Optional arguments:**

``-h, --help``
  show this help message and exit

``-D, --show-details``
  Show detailed information.

``-F FIELD, --field FIELD``
  Specify the field(s) to be returned by server. You can
  repeat this option.

BGP Speaker Delete
------------------

.. code-block:: console

    usage: neutron bgp-speaker-delete [-h] [--request-format {json}] BGP_SPEAKER

Delete a BGP speaker.

**Positional arguments:**

``BGP_SPEAKER``
  ID or name of the BGP speaker to delete.

**Optional arguments:**

``-h, --help``
  show this help message and exit

BGP Speaker Update
------------------

.. code-block:: console

    usage: neutron bgp-speaker-update [-h] [--request-format {json}] [--name NAME]
                                      [--advertise-floating-ip-host-routes {True,False}]
                                      [--advertise-tenant-networks {True,False}]
                                      BGP_SPEAKER

Update BGP Speaker's information.

**Positional arguments:**

``BGP_SPEAKER``
  ID or name of the BGP speaker to update.

**Optional arguments:**

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
---------------------------

.. code-block:: console

    usage: neutron bgp-speaker-network-add [-h] [--request-format {json}]
                                           BGP_SPEAKER NETWORK

Add a network to the BGP speaker.

**Positional arguments:**

``BGP_SPEAKER``
  ID or name of the BGP speaker.

``NETWORK``
  ID or name of the network to add.

**Optional arguments:**

``-h, --help``
  show this help message and exit

Delete Network from BGP Speaker
-------------------------------

.. code-block:: console

    usage: neutron bgp-speaker-network-remove [-h] [--request-format {json}]
                                              BGP_SPEAKER NETWORK

Remove a network from the BGP speaker.

**Positional arguments:**

``BGP_SPEAKER``
  ID or name of the BGP speaker.

``NETWORK``
  ID or name of the network to remove.

**Optional arguments:**

``-h, --help``
  show this help message and exit

BGP Advertised Routes List
--------------------------

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

**Positional arguments:**

``BGP_SPEAKER``
  ID or name of the BGP speaker.

**Optional arguments:**

``-h, --help``
  show this help message and exit

``-D, --show-details``
  Show detailed information.

``-F FIELD, --field FIELD``
  Specify the field(s) to be returned by server. You can
  repeat this option.
