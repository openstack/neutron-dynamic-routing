=====================
Dynamic Routing Agent
=====================

Add BGP Speaker to Dynamic Routing Agent
----------------------------------------

.. code-block:: console

    usage: neutron bgp-dragent-speaker-add [-h] [--request-format {json}]
                                           BGP_DRAGENT_ID BGP_SPEAKER

Add a BGP speaker to a Dynamic Routing agent.

**Positional arguments:**

``BGP_DRAGENT_ID``
  ID of the Dynamic Routing agent.

``BGP_SPEAKER``
  ID or name of the BGP speaker.

**Optional arguments:**

``-h, --help``
  show this help message and exit

Delete BGP Speaker from Dynamic Routing Agent
---------------------------------------------

.. code-block:: console

    usage: neutron bgp-dragent-speaker-remove [-h] [--request-format {json}]
                                              BGP_DRAGENT_ID BGP_SPEAKER

Removes a BGP speaker from a Dynamic Routing agent.

**Positional arguments:**

``BGP_DRAGENT_ID``
  ID of the Dynamic Routing agent.

``BGP_SPEAKER``
  ID or name of the BGP speaker.

**Optional arguments:**

``-h, --help``
  show this help message and exit

List BGP Speakers hosted by a Dynamic Routing Agent
---------------------------------------------------

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

**Positional arguments:**

``BGP_DRAGENT_ID``
  ID of the Dynamic Routing agent.

**Optional arguments:**

``-h, --help``
  show this help message and exit

``-D, --show-details``
  Show detailed information.

``-F FIELD, --field FIELD``
  Specify the field(s) to be returned by server. You can
  repeat this option.

List Dynamic Routing Agents Hosting a BGP Speaker
-------------------------------------------------

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
