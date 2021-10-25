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

=====
Agent
=====

Neutron-dynamic-routing implements a new agent named "DRAgent". The agent talks
to the neutron-dynamic-routing plugin which resides in the neutron server to get
routing entity configuration. DRAgent interacts with the back-end driver to
realize the required dynamic routing protocol functionality. For details,
please refer to the system design document :doc:`system-design`

.. note::
 One DRAgent can support multiple drivers but currently ONLY os-ken is
 integrated successfully.


Scheduler
=========

Neutron-dynamic-routing scheduler, schedules a routing entity to a proper DRAgent.

BGP Scheduler
-------------

BGP Speaker and DRAgent has 1:N association which means one BGP speaker can be
scheduled on multiple DRAgents.

There are different options for the scheduling algorithm to be used, these can
be selected via the ``bgp_drscheduler_driver`` configuration option.

StaticScheduler
~~~~~~~~~~~~~~~

This is the most simple option, which does no automatic scheduling at all.
Instead it relies on API requests to explicitly associate BGP speaker with
DRAgents and to disassociate them again.

Sample configuration::

    bgp_drscheduler_driver = neutron_dynamic_routing.services.bgp.scheduler.bgp_dragent_scheduler.StaticScheduler

Here is an example to associate/disassociate a BGP Speaker to/from a DRAgent.

.. TODO(frickler): update the examples to use OSC

::

  (neutron) bgp-speaker-list
  +--------------------------------------+------+----------+------------+
  | id                                   | name | local_as | ip_version |
  +--------------------------------------+------+----------+------------+
  | 0967eb04-59e5-4ca6-a0b0-d584d8d4a132 | bgp2 |      200 |          4 |
  | a73432c3-a3fc-4b1e-9be2-6c32a61df579 | bgp1 |      100 |          4 |
  +--------------------------------------+------+----------+------------+

  (neutron) agent-list
  +--------------------------------------+---------------------------+---------------------+-------------------+-------+----------------+---------------------------+
  | id                                   | agent_type                | host                | availability_zone | alive | admin_state_up | binary                    |
  +--------------------------------------+---------------------------+---------------------+-------------------+-------+----------------+---------------------------+
  | 0c21a829-4fd6-4375-8e65-36db4dc434ac | DHCP agent                | steve-devstack-test | nova              | :-)   | True           | neutron-dhcp-agent        |
  | 0f9d6886-910d-4af4-b248-673b22eb9e78 | Metadata agent            | steve-devstack-test |                   | :-)   | True           | neutron-metadata-agent    |
  | 5908a304-b9d9-4e8c-a0af-96a066a7c87e | Open vSwitch agent        | steve-devstack-test |                   | :-)   | True           | neutron-openvswitch-agent |
  | ae74e375-6a75-4ebe-b85c-6628d2baf02f | L3 agent                  | steve-devstack-test | nova              | :-)   | True           | neutron-l3-agent          |
  | dbd9900e-9d16-444d-afc4-8d0035df5ed5 | BGP dynamic routing agent | steve-devstack-test |                   | :-)   | True           | neutron-bgp-dragent       |
  +--------------------------------------+---------------------------+---------------------+-------------------+-------+----------------+---------------------------+

  (neutron) bgp-dragent-speaker-add dbd9900e-9d16-444d-afc4-8d0035df5ed5 bgp1
  Associated BGP speaker bgp1 to the Dynamic Routing agent.

  (neutron) bgp-speaker-list-on-dragent dbd9900e-9d16-444d-afc4-8d0035df5ed5
  +--------------------------------------+------+----------+------------+
  | id                                   | name | local_as | ip_version |
  +--------------------------------------+------+----------+------------+
  | a73432c3-a3fc-4b1e-9be2-6c32a61df579 | bgp1 |      100 |          4 |
  +--------------------------------------+------+----------+------------+

  (neutron) bgp-dragent-speaker-remove dbd9900e-9d16-444d-afc4-8d0035df5ed5 bgp1
  Disassociated BGP speaker bgp1 from the Dynamic Routing agent.

  (neutron) bgp-speaker-list-on-dragent dbd9900e-9d16-444d-afc4-8d0035df5ed5

  (neutron)

ReST API's for neutron-dynamic-routing scheduler are defined as part of the
`Neutron API reference`_.

.. _Neutron API reference: https://docs.openstack.org/api-ref/network/#bgp-dynamic-routing

ChanceScheduler
~~~~~~~~~~~~~~~

This is the default option. It will automatically schedule newly created BGP
speakers to one of the active DRAgents. When a DRAgent goes down, the BGP
speaker will be disassociated from it and an attempt is made to schedule
it to a different agent. Note that this action will override any manual
associations that have been performed via the API, so you will want to use
this scheduler only in very basic deployments.

Sample configuration::

    bgp_drscheduler_driver = neutron_dynamic_routing.services.bgp.scheduler.bgp_dragent_scheduler.ChanceScheduler

