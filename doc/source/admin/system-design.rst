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

System Design
=============

Introduction
------------
Neutron dynamic routing enables advertisement of self-service (private) network
prefixes to physical network devices that support dynamic routing protocols
such as routers, thus removing the conventional dependency on static routes.

It advertises three classes of routes:

* Host routes for floating IP addresses hosted on non-DVR routers, the nexthop is
  the centralized router.
* Host routes for floating IP addresses hosted on DVR routers, the nexthop is
  the appropriate compute node.
* Prefix routes for directly routable tenant networks with address scopes, the
  nexthop is the centralized router, the same for DVR and CVR.

For details refer to `Route Advertisement <./route-advertisement.html>`_.

Neutron dynamic routing consists of `service plug-in <https://docs.openstack.org/neutron/latest/contributor/internals/plugin-api.html>`_
and agent. The service plug-in implements the Networking service extension and
the agent manages dynamic routing protocol peering sessions. The plug-in communicates
with the agent through RPC.

Architecture
------------
The following figure shows the architecture of this feature::

    Neutron dynamic Routing System Architecture
   +---------------------------------------------------------------+
   |                  Dynamic Routing plug-in                      |
   |  +---------------------------------------------------------+  |
   |  |               Dynamic Routing API/Model                 |  |
   |  +---------------------------------------------------------+  |
   |  |               Dynamic Routing Agent Scheduler           |  |
   |  +---------------------------------------------------------+  |
   |                              |                                |
   +------------------------------|--------------------------------+
                                  |
                                  |
                            +-----------+
                            |    RPC    |
                            +-----------+
                                  |
                                  |
           +----------------------|-------------------------+
           |                                                |
           |                                                |
    +---------------------------+     +---------------------------+
    |   Dynamic Routing Agent1  |     |   Dynamic Routing Agent2  |
    |                           |     |                           |
    |  +---------------------+  |     |  +---------------------+  |
    |  |  Driver Manager     |  |     |  |  Driver Manager     |  |
    |  +---------------------+  |     |  +---------------------+  |
    |  |  Common Driver API  |  |     |  |  Common Driver API  |  |
    |  +---------------------+  |     |  +---------------------+  |
    |            |              |     |            |              |
    |  +---------+-----------+  |     |  +---------+-----------+  |
    |  | os-ken  |  Other    |  |     |  | os-ken  |  Other    |  |
    |  | Driver  |  Drivers  |  |     |  | Driver  |  Drivers  |  |
    |  +---------+-----------+  |     |  +---------+-----------+  |
    |                           |     |                           |
    +---------------------------+     +---------------------------+

Dynamic Routing Plug-in
~~~~~~~~~~~~~~~~~~~~~~~
Using dynamic routing plugin one can enable/disable the support of dynamic routing protocols
in neutron.

Dynamic Routing API
~~~~~~~~~~~~~~~~~~~
Dynamic routing API provides APIs to configure dynamic routing. API's for below mentioned dynamic
protocols are supported.

BGP
+++
Three kinds of APIs are available for BGP functionality.For details refer to the
`API document <../reference/index.html>`_.

* BGP Speaker APIs to advertise Neutron routes outside the Openstack network.
* BGP Peer APIs to form peers with the remote routers.
* BGP DRAgentScheduler APIs to schedule BGP Speaker(s) to one or more hosts running the
  dynamic routing agent.

.. note::
 BGP is the only dynamic routing protocol currently supported.

Dynamic Routing Model
~~~~~~~~~~~~~~~~~~~~~
Dynamic routing model maintains the database and communicates with the dynamic routing agent.

Dynamic Routing Agent Scheduler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Dynamic routing agent scheduler, is responsible for scheduling a routing entity. For details refer
to `Agent Scheduler <./agent-scheduler.html>`_.

Dynamic Routing Agent (DR Agent)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Dynamic routing can reside on hosts with or without other Networking service agents.
It manages and configures different dynamic routing stack through
`Common Driver API <../contributor/dragent-drivers.html>`_.

.. note::
 Currently, only integration with `os-ken <https://docs.openstack.org/os-ken/latest/>`_
 is supported.
