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

DRAgent Drivers
===============

Introduction
------------
The Neutron dynamic routing drivers are used to support different dynamic
routing protocol stacks which implement the dynamic routing functionality.

As shown in the following figure, the drivers are managed by `DRAgent <./agent-scheduler.html>`_
through a "Driver Manager" which provides consistent APIs to realize the
functionality of a dynamic routing protocol::

                 Neutron Dynamic Routing Drivers
                +-------------------------------+
                |          DRAgent              |
                |                               |
                |  +-------------------------+  |
                |  |    Driver Manager       |  |
                |  +-------------------------+  |
                |  |    Common Driver API    |  |
                |  +-------------------------+  |
                |               |               |
                |               |               |
                |  +------------+------------+  |
                |  |  os-ken    |  Other     |  |
                |  |  Driver    |  Drivers   |  |
                |  +------------+------------+  |
                |                               |
                +-------------------------------+

.. note::
 Currently only the integration with os-ken is supported
 BGP is the only protocol supported.


Configuration
-------------
Driver configurations are done in a separate configuration file.

BGP Driver
~~~~~~~~~~
There are two configuration parameters related to BGP which are specified in ``bgp_dragent.ini``.

* bgp_speaker_driver, to define BGP speaker driver class. Default is os-ken
  (neutron_dynamic_routing.services.bgp.agent.driver.os_ken.driver.OsKenBgpDriver).
* bgp_router_id, to define BGP identity (typically an IPv4 address). Default is
  a unique loopback interface IP address.

Common Driver API
-----------------
Common Driver API is needed to provide a generic and consistent interface
to different drivers. Each driver need to implement the provided
`base driver class <https://opendev.org/openstack/neutron-dynamic-routing/src/branch/master/neutron_dynamic_routing/services/bgp/agent/driver/base.py>`_.


BGP
~~~
Following interfaces need to be implemented by a driver for realizing BGP
functionality.

+--------------------------------+-----------------------------------------+
|API name                        |Description                              |
+================================+=========================================+
|add_bgp_speaker()               |Add a BGP Speaker                        |
+--------------------------------+-----------------------------------------+
|delete_bgp_speaker()            |Delete a BGP speaker                     |
+--------------------------------+-----------------------------------------+
|add_bgp_peer()                  |Add a BGP peer                           |
+--------------------------------+-----------------------------------------+
|delete_bgp_peer()               |Delete a BGP peer                        |
+--------------------------------+-----------------------------------------+
|advertise_route()               |Add a new prefix to advertise            |
+--------------------------------+-----------------------------------------+
|withdraw_route()                |Withdraw an advertised prefix            |
+--------------------------------+-----------------------------------------+
|get_bgp_speaker_statistics()    |Collect BGP Speaker statistics           |
+--------------------------------+-----------------------------------------+
|get_bgp_peer_statistics()       |Collect BGP Peer statistics              |
+--------------------------------+-----------------------------------------+
