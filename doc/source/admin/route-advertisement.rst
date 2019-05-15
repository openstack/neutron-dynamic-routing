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

Route Advertisement
===================
BGP
---

This page discusses the behavior of BGP dynamic routing about how to advertise
routes and show the routes details in the project.

BGP dynamic routing could advertise 3 classes of routes:

* Host routes for floating IP addresses hosted on non-DVR routers, as floatingip
  address set on the router namespace, it knows how to route the message to the
  correct way, so the next-hop should be the IP address of router gateway port.
* Host routes for floating IP addresses hosted on DVR routers. With DVR-enabled
  routers, the floating IP can be reached directly on the compute node hosting
  a given instance. As such, host routes for the floating IP address should
  advertise the FIP agent gateway on the compute node as the next-hop instead of
  the centralized router. This will keep inbound floating IP traffic from
  encountering the bottleneck of the centralized router.
* Prefix routes for directly routable tenant networks with address scopes, the
  nexthop is the centralized router, the same for DVR and CVR. BGP dynamic
  routing could advertise tenant network prefixes to physical network
  devices(routers which support BGP protocol), called this
  ``Prefixes advertisement``.

When distributed virtual routing (DVR) is enabled on a router, next-hops for
floating IP's and fixed IP's are not advertised as being at the centralized
router. Host routes with the next-hop set to the appropriate compute node
are advertised.

Logical Model
~~~~~~~~~~~~~
::

   +--------+ 1     N +---------------------+
   | Router |---------|  BgpAdvertisedRoute |
   +--------+         +---------------------+
                                | N
                                |
                                | 1
   +---------+ N       N +------------+ N       N +---------+
   | BgpPeer |-----------| BgpSpeaker |-----------| Network |
   +---------+           +------------+           +---------+
                                | N
                                |
                                | 1
                         +--------------+
                         | AddressScope |
                         +--------------+

.. note::
 A BGP Speaker only supports one address family to speak BGP. A dual-stack IPv4
 and IPv6 network needs two BGP Speakers to advertise the routes with BGP, one
 for IPv4 and the other for IPv6. So A network can have N number of BGP
 Speakers bound to it.

BgpAdvertisedRoute represents derived data. As the number of
BgpAdvertisedRoutes can be quite large, storing in a database table is not
feasible. BgpAdvertisedRoute information can be derived by joining data
already available in the Neutron database. And now BGP dynamic routing project
process the Bgpadvertiseroutes which should be advertised to external Router is
basing on the exist Neutron DB tables.
Neutron looks on each of the gateway network for any routers with a gateway port
on that network. For each router identified, Neutron locates each floating IP
and tenant network accessible through the router gateway port. Neutron then
advertises each floating IP and tenant network with the IP address of the router
gateway port as the next hop.

When BGP Plugin is started, it will register callbacks. All callbacks are used for
processing Floating IP, Router Interface and Router Gateway creation or update, this
functions listen the events of these resources for calling Dragent to change the
advertisement routes.

Now we just focus on the resources which may cause route change, the following
callbacks does this work.

* floatingip_update_callback
  This function listens to the Floating IP's AFTER_UPDATE event, it judges whether
  the associated router is changed, and changes the advertisement routes and nexthop
  based on that.
* router_interface_callback
  This function listens to the tenants' network routes change, it listens to AFTER_CREATE
  and AFTER_DELETE events of Router Interface resource. It calls Dragent to advertise
  or stop the prefix routes after a interface attach into a router.
* router_gateway_callback
  This function listens to the router gateway port creation or deletion. It also focuses
  on tenants' network routes change.

You could get the advertisement routes of specific BGP Speaker like:
``neutron bgp-speaker-advertiseroute-list <created-bgp-speaker>``
It does a complicated db query to generate the list of advertised routes.
For more details refer to `route advertisement db lookup <https://opendev.org/openstack/neutron-dynamic-routing/src/branch/master/neutron_dynamic_routing/db/bgp_db.py#n462>`_
