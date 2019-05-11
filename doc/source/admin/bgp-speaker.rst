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

BGP Speaker
===========
BGP Speaker acts as a route server using BGP routing protocol. It advertises
routes to the BGP peers which are added to the BGP Speaker. Now there is a
framework that allows different `BGP drivers <../contributor/dragent-drivers.html>`_
to be plugged into a `dynamic routing agent <./agent-scheduler.html>`_.

Currently, BGP Speaker only advertises routes for a network to which it is associated.
A BGP Speaker requires association with a "gateway" network to determine eligible routes.
In Neutron, a "gateway" network connects Neutron routers to the upstream routers. An
external network is best for being used as a gateway network. The association builds a
list of all virtual routers with gateways on provider and self-service networks within
the same address scope. Hence, the BGP speaker advertises self-service network prefixes
with the corresponding router as the next-hop IP address.
For details refer to `Route advertisement <./route-advertisement.html>`_.

Address Scopes
--------------
`Address scopes <https://opendev.org/openstack/neutron/src/branch/master/doc/source/contributor/internals/address_scopes.rst>`_
provide flexible control as well as decoupling of address overlap from tenancy,
so this kind control can provide a routable domain, the domain has itself route
and no overlap address, it means an address scope define "a L3 routing domain".

BGP Speaker will associate the external networks and advertise the tenant's
networks routes. Those networks should reside in the same address scope.
Neutron can route the tenant network directly without NAT. Then Neutron can
host globally routable IPv4 and IPv6 tenant networks. For determining which
tenant networks prefixes should be advertised, Neutron will identify all routers
with gateway ports on the network which had been bounded with BGP Speaker,
check the address scope of the subnets on all connected networks, then begin
advertising nexthops for all tenant networks to routers on the bound network.

BGP Peer
--------
BGP peer defined in Neutron represents real BGP infrastructure such as
routers, route reflectors and route servers. When a BGP peer is defined and
associated with a BGP Speaker, Neutron will attempt to open a BGP peering
session with the mentioned remote peer. It is this session, using which Neutron
announces it's routes.

How to configure a remote peer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A remote peer can be real or virtual e.g. vRouters or real routers.
The remote peer should be configured to handle peering with Neutron in passive
mode. The peer needs to waits for the Neutron dynamic routing agent to
initiate the peering session. Also, the remote peer can be configured in active
mode, but it still can speak BGP until the complete initialization of BGP Speaker
running on Neutron dynamic routing agent.

Configuring BGP Speaker:
One needs to ensure below points for setting a BGP connection.

* Host running Neutron dynamic agent MUST connect to the external router.
* BGP configuration on the router should be proper.

  ``bgp router-id XX.XX.XX.XX``
      This must be an IP address, the unique identifier of BGP routers actually
      and can be virtual. If one doesn't configure the router-id, it will be selected
      automatically as the highest IP address configured for the local interfaces.
      Just a suggestion, please make sure that it is the same as the ``peer_ip``
      which you configure in Neutron for distinguishing easily.

 ``local_as``
     Autonomous System number can be same or different from the AS_id of external
     BGP router. AS_id will be same for iBGP and different for eBGP sessions.

Setting BGP peer:
::

  neighbor A.B.C.D remote-as AS_ID
  A.B.C.D is the host IP which run Neutron dynamic routing agent.

A Sample Quagga router configuration file forming BGP peering with Neutron:
::

    !
    password zebra
    log file /var/log/quagga/bgpd.log
    !
    debug bgp events
    debug bgp keepalives
    debug bgp updates
    debug bgp fsm
    debug bgp filters
    !
    bgp multiple-instance
    !
    router bgp <BgpPeer remote_as> view test-as
     bgp router-id <quagga router IP address>
     neighbor <dr_agent IP address> remote-as <BgpSpeaker local_as>
     neighbor <dr_agent IP address> passive
    !
    line vty
    !

BGP Speaker Architecture
------------------------
Dynamic routing project saves BGP Speaker configuration as per the defined
`data model <https://opendev.org/openstack/neutron-dynamic-routing/src/branch/master/neutron_dynamic_routing/db/bgp_db.py#n85>`_.
and pass on the configuration request to the dynamic routing agent for further processing.
The implementation of a BGP Speaker is driver specific. During the driver interface
initialization process, needed configurations are read from the configuration file
and BGP Speaker object instance is created. For details refer to
`BGP drivers <../contributor/dragent-drivers.html>`_.

BGP Speaker Life Cycle
~~~~~~~~~~~~~~~~~~~~~~
Now we support OsKenBgpDriver, BGP Speaker will be processed by Dragent. When
associating a BGP Speaker with an active Dragent, the plugin will send an RPC
message to the agent for calling driver in order to create a BGP Speaker instance.

In OsKenBgpDriver, the created instance ``BGP Speaker`` will setup by router-id
and ASN, then os-ken will setup new context with speaker configuration and listeners
which monitor whether the related peers are alive.

Then the following operation could be done.

* Add peers to BGP Speaker
  When BGP Speaker is not associated with an active Dragent, there is no real speaker
  instance, so it will be still the db operation until the speaker is associated with
  dragent, and all the peers connection before will be setup by ``BGP Speaker``
  creation. If add peers into speaker which is running, Dragent will call driver
  to add peer dynamically. For OsKenBgpDriver, it will register a new neighbor
  based on your peer configuration and try to establish a session with the peer.

* Delete peers from BGP Speaker
  The same logic with below, but it is reverse.

If you don't want use the specific BGP Speaker anymore, you can use CLI:
``neutron bgp-speaker-delete <SPEAKER NAME/ID>``

BGP Plugin will find all the associated Dragent and send RPC ``bgp_speaker_remove_end``
to make the Dragents to clean the ``BGP Speaker`` instances. This is the same
with CLI:
``neutron bgp-dragent-speaker-remove <DRAGENT ID> <SPEAKER NAME/ID>``
BGP Plugin just send rpc ``bgp_speaker_remove_end`` to the specific Dragent.

Advertisement
~~~~~~~~~~~~~
For details refer to `Route Advertisement <./route-advertisement.html>`_.

How to work
-----------
For details refer to `Testing <../contributor/testing.html>`_.
