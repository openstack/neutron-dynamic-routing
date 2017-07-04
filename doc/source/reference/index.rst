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

API
===

Introduction
------------
Neutron dynamic routing project adds the support for dynamic routing protocols
in neutron. Using the ReST interface, a cloud administrator can define routing
peers and advertise neutron routes outside the OpenStack domain.

.. note::

   Currently, only the support for BGP dynamic routing protocol is available.

Data Model
----------
New data models are defined for supporting routing protocols. Below models are defined for
different protocols.

BGP
~~~

BGP Speaker
+++++++++++
* ``id``
  The uuid of BGP Speaker.
* ``name``
  The name of BGP Speaker.
* ``local_as``
  The local AS value, ranges from 1 to 65535.
* ``ip_version``
  The ip address version for BGP Speaker. 4 by default.
* ``peers``
  The remote peer connection which supports BGP.
* ``networks``
  The tenant networks connected to the BGP Speaker.
* ``advertise_floating_ip_host_routes``
  Whether to enable or disable the advertisement of floating ip host routes by
  the BGP Speaker. True by default.
* ``advertise_tenant_networks``
  Whether to enable or disable the advertisement of tenant network routes by
  the BGP Speaker. True by default.

BGP Peer
++++++++
* ``id``
  The uuid of BGP peer.
* ``name``
  The name of BGP peer.
* ``peer_ip``
  The IP address of BGP peer.
* ``remote_as``
  The remote AS value, ranges from 1 to 65535.
* ``auth_type``
  The authentication algorithm. Supported algorithms: none and md5, none by
  default.
* ``password``
  The authentication password for the specified authentication type.


ReST Interface
--------------
Different ReST interface are exposed for realizing different dynamic protocol
functionality.

.. note::

   Only an administrator have the access to the exposed API's.


BGP
~~~

BGP Speaker
+++++++++++

Create
''''''
Issue a ``POST`` request to ``/v2.0/bgp-speakers`` with following JSON-encoded
data to create a BGP Speaker: ::

  {
     "bgp_speaker":{
        "ip_version":4,
        "local_as":"1000",
        "name":"bgp-speaker"
     }
  }

  Response body:

  {
     "bgp_speaker":{
        "peers":[
        ],
        "name":"bgp-speaker",
        "tenant_id":"34a6e17a48cf414ebc890367bf42266b",
        "local_as":1000,
        "advertise_tenant_networks":true,
        "networks":[
        ],
        "ip_version":4,
        "advertise_floating_ip_host_routes":true,
        "id":"5e08db80-db77-4b5c-a56d-dbca0b284f2c"
     }
  }

  Return code: 201

List
''''
Issue a ``GET`` request to ``/v2.0/bgp-speakers`` to retrieve this list of available
BGP Speakers. ::

  Response body:

  {
     "bgp_speakers":[
        {
           "peers":[
           ],
           "name":"bgp-speaker-1",
           "tenant_id":"34a6e17a48cf414ebc890367bf42266b",
           "local_as":1001,
           "advertise_tenant_networks":true,
           "networks":[
           ],
           "ip_version":4,
           "advertise_floating_ip_host_routes":true,
           "id":"5e08db80-db77-4b5c-a56d-dbca0b284f2c"
        },
        {
           "peers":[
           ],
           "name":"bgp-speaker",
           "tenant_id":"34a6e17a48cf414ebc890367bf42266b",
           "local_as":1000,
           "advertise_tenant_networks":true,
           "networks":[
           ],
           "ip_version":4,
           "advertise_floating_ip_host_routes":true,
           "id":"b759b2a1-27f4-4a6b-bb61-f2c9a22c9902"
        }
     ]
  }

  Return code: 200

Show
''''
Issue a ``GET`` request to ``/v2.0/bgp-speakers/<bgp-speaker-id>`` to retrieve the
detail about a specific BGP Speaker. ::

  Response body:

  {
     "bgp_speaker":{
        "peers":[
        ],
        "name":"bgp-speaker",
        "tenant_id":"34a6e17a48cf414ebc890367bf42266b",
        "local_as":1000,
        "advertise_tenant_networks":true,
        "networks":[
        ],
        "ip_version":4,
        "advertise_floating_ip_host_routes":true,
        "id":"b759b2a1-27f4-4a6b-bb61-f2c9a22c9902"
     }
  }

  Return code: 200

Update
''''''
Issue ``PUT`` request to ``/v2.0/bgp-speakers/<bgp-speaker-id>`` to update a
specific BGP Speaker. Following attributes can be updated.

* ``name``
  The name of BGP Speaker.
* ``advertise_floating_ip_host_routes``
  Whether to enable or disable the advertisement of floating ip host routes by
  the BGP Speaker. True by default.
* ``advertise_tenant_networks``
  Whether to enable or disable the advertisement of tenant network routes by
  the BGP Speaker. True by default.

Delete
''''''
Issue ``DELETE`` request to ``/v2.0/bgp-speakers/<bgp-speaker-id>`` to delete
a specific BGP Speaker. ::

  No response body

  Return code: 204

BGP Peer
++++++++

Create
''''''
Issue a ``POST`` request to ``/v2.0/bgp-peers`` with following JSON-encoded data
to create a BGP peer: ::

  {
     "bgp_peer":{
        "auth_type":"none",
        "remote_as":"1001",
        "name":"bgp-peer",
        "peer_ip":"10.0.0.3"
     }
  }

  Response body:

  {
     "bgp_peer":{
        "auth_type":"none",
        "remote_as":"1001",
        "name":"bgp-peer",
        "tenant_id":"34a6e17a48cf414ebc890367bf42266b",
        "peer_ip":"10.0.0.3",
        "id":"a7193581-a31c-4ea5-8218-b3052758461f"
     }
  }

  Return code: 201

List
''''
Issue a ``GET`` request to ``/v2.0/bgp-peers`` to retrieve the list of available
BGP peers. ::

  Response body:

  {
     "bgp_peers":[
        {
           "auth_type":"none",
           "remote_as":1001,
           "name":"bgp-peer",
           "tenant_id":"34a6e17a48cf414ebc890367bf42266b",
           "peer_ip":"10.0.0.3",
           "id":"a7193581-a31c-4ea5-8218-b3052758461f"
        }
     ]
  }

  Return code: 200

Show
''''
Issue a ``GET`` request to ``/v2.0/bgp-peers/<bgp-peer-id>`` to retrieve the detail about a
specific BGP peer. ::

  Response body:

  {
     "bgp_peer":{
        "auth_type":"none",
        "remote_as":1001,
        "name":"bgp-peer",
        "tenant_id":"34a6e17a48cf414ebc890367bf42266b",
        "peer_ip":"10.0.0.3",
        "id":"a7193581-a31c-4ea5-8218-b3052758461f"
     }
  }

  Return code: 200

Update
''''''
Issue ``PUT`` request to ``/v2.0/bgp-peers/<bgp-peer-id>`` to update
a specific BGP peer. Following attributes can be updated.

* ``name``
  The name of BGP peer.
* ``password``
  The authentication password.


Delete
''''''
Issue ``DELETE`` request to ``/v2.0/bgp-peers/<bgp-peer-id>`` to delete
a specific BGP peer. ::

  No response body

  Return code: 204


BGP Speaker and Peer binding
++++++++++++++++++++++++++++

Add BGP Peer to a BGP Speaker
'''''''''''''''''''''''''''''
Issue a ``PUT`` request to ``/v2.0/bgp-speakers/<bgp-speaker-id>/add-bgp-peer``
to bind the BGP peer to the specified BGP Seaker with following JSON-encoded data: ::

  {
     "bgp_peer_id":"a7193581-a31c-4ea5-8218-b3052758461f"
  }

  Response body: ::

  {
     "bgp_peer_id":"a7193581-a31c-4ea5-8218-b3052758461f"
  }

  Return code: 200

Remove BGP Peer from a BGP Speaker
''''''''''''''''''''''''''''''''''
Issue a ``DELETE`` request with following data to ``/v2.0/bgp-speakers/<bgp-speaker-id>/remove-bgp-peer``
to unbind the BGP peer: ::

  {
     "bgp_peer_id":"a7193581-a31c-4ea5-8218-b3052758461f"
  }

  No response body

  Return code: 200


BGP Speaker and Network binding
+++++++++++++++++++++++++++++++

Add Network to a BGP Speaker
''''''''''''''''''''''''''''
Issue a ``PUT`` request with following data to ``/v2.0/bgp-speakers/<bgp-speaker-id>/add_gateway_network``
to add a network to the specified BGP speaker: ::

  {
     "network_id":"f2269b61-6755-4174-8f64-5e318617b204"
  }

  Response body:

  {
     "network_id":"f2269b61-6755-4174-8f64-5e318617b204"
  }

  Return code: 200

Delete Network from a BGP Speaker
'''''''''''''''''''''''''''''''''
Issue a ``DELETE`` request with following data to ``/v2.0/bgp-speakers/<bgp-speaker-id>/remove_gateway_network``
to delete a network from a specified BGP speaker. ::

  No response body

  Return code: 200

BGP Speaker Advertised Routes
+++++++++++++++++++++++++++++

List routes advertised by a BGP Speaker
'''''''''''''''''''''''''''''''''''''''
Issue ``GET`` request to ```/v2.0/bgp-speakers/<bgp-speaker-id>/get_advertised_routes``
to list all routes advertised by the specified BGP Speaker. ::

  Response body:

  {
     "advertised_routes":[
        {
           "cidr":"192.168.10.0/24",
           "nexthop":"10.0.0.1"
        }
     ]
  }

  Return code: 200

BGP Speaker and Dynamic Routing Agent interaction
+++++++++++++++++++++++++++++++++++++++++++++++++

Add BGP Speaker to a Dynamic Routing Agent
''''''''''''''''''''''''''''''''''''''''''
Issue a ``POST`` request to ``/v2.0/agents/<bgp-agent-id>/bgp-drinstances`` to
add a BGP Speaker to the specified dynamic routing agent. The following is
the request body: ::

  {
    "bgp_speaker_id": "5639072c-49eb-480a-9f11-953386589bc8"
  }

  No response body

  Return code: 201

List BGP speakers hosted by a Dynamic Routing Agent
'''''''''''''''''''''''''''''''''''''''''''''''''''
Issue a ``GET`` request to ``/v2.0/agents/<bgp-dragent-id>/bgp-drinstances`` to
list all BGP Seakers hosted on the specified dynamic routing agent. ::

  Response body:

  {
     "bgp_speakers":[
        {
           "peers":[
           ],
           "name":"bgp-speaker",
           "tenant_id":"34a6e17a48cf414ebc890367bf42266b",
           "local_as":1000,
           "advertise_tenant_networks":true,
           "networks":[
           ],
           "ip_version":4,
           "advertise_floating_ip_host_routes":true,
           "id":"b759b2a1-27f4-4a6b-bb61-f2c9a22c9902"
        }
     ]
  }

  Return code: 200

List Dynamic Routing Agents hosting a specific BGP Speaker
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Issue a ``GET`` request to ``/v2.0/bgp-speakers/<bgp-speaker-id>/bgp-dragents``
to list all BGP dynamic agents which are hosting the specified BGP Speaker. ::

  Response body:

  {
     "agents":[
        {
           "binary":"neutron-bgp-dragent",
           "description":null,
           "admin_state_up":true,
           "heartbeat_timestamp":"2016-05-17 03:05:12",
           "availability_zone":null,
           "alive":true,
           "topic":"bgp_dragent",
           "host":"yangyubj-virtual-machine",
           "agent_type":"BGP dynamic routing agent",
           "resource_versions":{
           },
           "created_at":"2016-05-09 07:38:00",
           "started_at":"2016-05-11 09:06:13",
           "id":"af216618-29d3-4ee7-acab-725bdc90e614",
           "configurations":{
              "advertise_routes":0,
              "bgp_peers":0,
              "bgp_speakers":1
           }
        }
     ]
  }

  Return code: 200


Delete BGP Speaker from a Dynamic Routing Agent
'''''''''''''''''''''''''''''''''''''''''''''''
Issue a ``DELETE`` request to ``/v2.0/agents/<bgp-agent-id>/bgp-drinstances/<bgp-speaker-id>``
to delete the BGP Speaker hosted by the specified dynamic routing agent. ::

  No response body

  Return code: 204

Reference
---------
None
