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

Testing
=======

Dynamic routing enables advertisement of self-service network prefixes to physical network
devices that support a dynamic routing protocol, such as routers. The Neutron dynamic routing project
consists of a service plugin-in and an agent that can advertise Neutron private network to outside of
OpenStack. This document will describe how to test the Dynamic Routing functionalities, introduce
what the environment architecture is for dynamic routing test and show how to setup dynamic routing
environment using Devstack.

Environment Architecture
-------------------------

Use the following example architecture as a test environment to deploy neutron-dynamic-routing in
your environment. The example architecture will deploy an all-in-one OpenStack and connect to an Ubuntu
VM running Quagga as a router outside of OpenStack. See following::



                                                                    +--------------+
                                                       10.156.18.20 |              |
                                 +----------------------------------|   Quagga     |
                                 | BGP Peering Session              |   Router     |
                                 |                                  |  172.24.4.3  |
                                 |                                  +--------------+
                                 |                                         |
                                 |10.156.18.21                             |       External Network(172.24.4.0/24)
                --------------------------------------------------------------------------------------------------
                                 |eth0
                        +---------------------------------------+
                        |        |                              |
                        |        |        br-ex                 |
                        |        +----------------+             |
                        |        |                |172.24.4.1   |
                        |  +------------+     +-------+         |
                        |  |            |     |Router |         |
                        |  |  Dr-Agent  |     |       |         |
                        |  |            |     +-------+         |
                        |  +------------+         |             |
                        |                  ----------------     |
                        |                  Tenant Network       |
                        |                   (10.0.0.0/24)       |
                        |                                       |
                        +---------------------------------------+
                        All-In-One OpenStack Installation


Devstack Setup
--------------

1. Download devstack::

    git clone https://opendev.org/openstack/devstack.git

2. Enable neutron-dynamic-routing by including this in your local.conf file::

    [[local|localrc]]
    enable_plugin neutron-dynamic-routing https://opendev.org/openstack/neutron-dynamic-routing

3. Run devstack::

    ./stack.sh

Quagga Configure
----------------

Quagga is a network routing software available in most GNU/Linux, Solaris, FreeBSD, and NetBSD. It provides
the implementation of OSPF, RIP, BGP and IS-IS. This section shows you how to install Quagga and then configure
it on Ubuntu Linux.

1. Install Quagga using apt-get::

    $ sudo apt-get install quagga quagga-doc

2. Create an empty file (/etc/quagga/zebra.conf) and set permissions.

   The Quagga files and configurations will be stored in /etc/quagga::

    $ sudo touch /etc/quagga/zebra.conf
    $ sudo chown quagga.quagga /etc/quagga/zebra.conf
    $ sudo chmod 640 /etc/quagga/zebra.conf

3. Update quagga daemon file.

   You can enable/disable the daemons routing in the /etc/quagga/daemons file. Update /etc/quagga/daemons to enable zebra and bgp::

    zebra=yes
    bgpd=yes
    ospfd=no
    ospf6d=no
    ripd=no
    ripngd=no
    isisd=no

4. Update /etc/quagga/zebra.conf::

    # Zebra configuration
    # name of the router
    hostname quagga_1
    password zebra

    # log
    log file /var/log/quagga/zebra.log

5. Update /etc/quagga/bgpd.conf::

    # declare a router with local-as 1000
    router bgp 1000

    # set router-id to the network address we announce
    bgp router-id 10.156.18.20

    # expose neighbor network which dynamic routing agent is using
    neighbor 10.156.18.21 remote-as 12345

    # treat neutron dynamic routing agent as a passive peer in case
    # quagga keeps making futile connection attempts
    neighbor 10.156.18.21 passive

    # log
    log file /var/log/quagga/bgpd.log

    debug bgp events
    debug bgp filters
    debug bgp fsm
    debug bgp keepalives
    debug bgp updates

6. Restart the Quagga daemon::

    $ sudo systemcl restart bgpd

Service Test
-------------

1. As the dynamic routing is only supported by admin, source the devstack admin credentials::

    $ . devstack/openrc admin admin

2. Verify that the neutron dynamic routing agent is running.

    .. code-block:: console

        $ openstack network agent list --agent-type bgp
        +--------------------+--------------------+--------------------+-------------------+-------+-------+---------------------+
        | ID                 | Agent Type         | Host               | Availability Zone | Alive | State | Binary              |
        +--------------------+--------------------+--------------------+-------------------+-------+-------+---------------------+
        | 69ad386f-e055-4284 | BGP dynamic        | devstack-bgp-dr    |                   | :-)   | UP    | neutron-bgp-dragent |
        | -8c8e-ef9bd540705c | routing agent      |                    |                   |       |       |                     |
        +--------------------+--------------------+--------------------+-------------------+-------+-------+---------------------+

3. Create an address scope.

   The provider(external) and tenant networks must belong to the same address scope
   for the agent to advertise those tenant network prefixes.

    .. code-block:: console

        $ openstack address scope create --ip-version 4 --share public
        +------------+--------------------------------------+
        | Field      | Value                                |
        +------------+--------------------------------------+
        | id         | c02c358a-9d35-43ea-8313-986b3e4a91c0 |
        | ip_version | 4                                    |
        | name       | public                               |
        | project_id | b3ac05ef10bf441fbf4aa17f16ae1e6d     |
        | shared     | True                                 |
        +------------+--------------------------------------+

4. Create subnet pools. The provider and tenant networks use different pools.

    * Create the provider network pool.

    .. code-block:: console

        $ openstack subnet pool create --pool-prefix 172.24.4.0/24 \
          --address-scope public provider
        +-------------------+--------------------------------------+
        | Field             | Value                                |
        +-------------------+--------------------------------------+
        | address_scope_id  | 18f74828-5f38-4d84-b030-ed642f2157c5 |
        | created_at        | 2020-08-28T15:12:11Z                 |
        | default_prefixlen | 8                                    |
        | default_quota     | None                                 |
        | description       |                                      |
        | id                | d812a10e-5981-4686-90c4-d6fff454b38a |
        | ip_version        | 4                                    |
        | is_default        | False                                |
        | max_prefixlen     | 32                                   |
        | min_prefixlen     | 8                                    |
        | name              | provider                             |
        | prefixes          | 172.24.4.0/24                        |
        | project_id        | 17c884da94bc4259b20ace3da6897297     |
        | revision_number   | 0                                    |
        | shared            | False                                |
        | tags              |                                      |
        | updated_at        | 2020-08-28T15:12:11Z                 |
        +-------------------+--------------------------------------+

    * Create tenant network pool.

    .. code-block:: console

        $ openstack subnet pool create --pool-prefix 10.0.0.0/16 \
          --address-scope public --share selfservice
        +-------------------+--------------------------------------+
        | Field             | Value                                |
        +-------------------+--------------------------------------+
        | address_scope_id  | 18f74828-5f38-4d84-b030-ed642f2157c5 |
        | created_at        | 2020-08-28T15:15:31Z                 |
        | default_prefixlen | 8                                    |
        | default_quota     | None                                 |
        | description       |                                      |
        | id                | 8b9d1c9b-6aba-416f-8d10-1e7a0f6052f6 |
        | ip_version        | 4                                    |
        | is_default        | False                                |
        | max_prefixlen     | 32                                   |
        | min_prefixlen     | 8                                    |
        | name              | selfservice                          |
        | prefixes          | 10.0.0.0/16                          |
        | project_id        | 17c884da94bc4259b20ace3da6897297     |
        | revision_number   | 0                                    |
        | shared            | True                                 |
        | tags              |                                      |
        | updated_at        | 2020-08-28T15:15:31Z                 |
        +-------------------+--------------------------------------+

5. Create the provider and tenant networks.

    * Create the provider network.

    .. code-block:: console

        $ openstack network create --external --provider-network-type flat \
          --provider-physical-network public provider
        +---------------------------+--------------------------------------+
        | Field                     | Value                                |
        +---------------------------+--------------------------------------+
        | admin_state_up            | UP                                   |
        | availability_zone_hints   |                                      |
        | availability_zones        |                                      |
        | created_at                | 2020-08-28T15:24:07Z                 |
        | description               |                                      |
        | dns_domain                |                                      |
        | id                        | 18f9a9c0-f8f5-4360-822a-b687c1008bf7 |
        | ipv4_address_scope        | None                                 |
        | ipv6_address_scope        | None                                 |
        | is_default                | False                                |
        | is_vlan_transparent       | None                                 |
        | mtu                       | 1500                                 |
        | name                      | provider                             |
        | port_security_enabled     | True                                 |
        | project_id                | 17c884da94bc4259b20ace3da6897297     |
        | provider:network_type     | flat                                 |
        | provider:physical_network | public                               |
        | provider:segmentation_id  | None                                 |
        | qos_policy_id             | None                                 |
        | revision_number           | 1                                    |
        | router:external           | External                             |
        | segments                  | None                                 |
        | shared                    | False                                |
        | status                    | ACTIVE                               |
        | subnets                   |                                      |
        | tags                      |                                      |
        | updated_at                | 2020-08-28T15:24:07Z                 |
        +---------------------------+--------------------------------------+

    * Create a subnet on the provider network using an IP address allocation from the provider subnet pool.

    .. code-block:: console

        $ openstack subnet create --network provider --subnet-pool provider \
          --prefix-length 24 provider
        +----------------------+--------------------------------------+
        | Field                | Value                                |
        +----------------------+--------------------------------------+
        | allocation_pools     | 172.24.4.2-172.24.4.254              |
        | cidr                 | 172.24.4.0/24                        |
        | created_at           | 2020-08-28T15:27:00Z                 |
        | description          |                                      |
        | dns_nameservers      |                                      |
        | dns_publish_fixed_ip | False                                |
        | enable_dhcp          | True                                 |
        | gateway_ip           | 172.24.4.1                           |
        | host_routes          |                                      |
        | id                   | 4ed8ac88-2c19-4f94-9362-7b301e743438 |
        | ip_version           | 4                                    |
        | ipv6_address_mode    | None                                 |
        | ipv6_ra_mode         | None                                 |
        | name                 | provider                             |
        | network_id           | 18f9a9c0-f8f5-4360-822a-b687c1008bf7 |
        | prefix_length        | 24                                   |
        | project_id           | 17c884da94bc4259b20ace3da6897297     |
        | revision_number      | 0                                    |
        | segment_id           | None                                 |
        | service_types        |                                      |
        | subnetpool_id        | a8fecc3d-a489-46ca-87fb-dff4e3371503 |
        | tags                 |                                      |
        | updated_at           | 2020-08-28T15:27:00Z                 |
        +----------------------+--------------------------------------+

    * Create the tenant network.

    .. code-block:: console

        $ openstack network create private
        +---------------------------+--------------------------------------+
        | Field                     | Value                                |
        +---------------------------+--------------------------------------+
        | admin_state_up            | UP                                   |
        | availability_zone_hints   |                                      |
        | availability_zones        |                                      |
        | created_at                | 2020-08-28T15:28:06Z                 |
        | description               |                                      |
        | dns_domain                |                                      |
        | id                        | 43643543-6edb-4c2b-a087-4553b75b6799 |
        | ipv4_address_scope        | None                                 |
        | ipv6_address_scope        | None                                 |
        | is_default                | False                                |
        | is_vlan_transparent       | None                                 |
        | mtu                       | 1442                                 |
        | name                      | private                              |
        | port_security_enabled     | True                                 |
        | project_id                | 17c884da94bc4259b20ace3da6897297     |
        | provider:network_type     | geneve                               |
        | provider:physical_network | None                                 |
        | provider:segmentation_id  | 1                                    |
        | qos_policy_id             | None                                 |
        | revision_number           | 1                                    |
        | router:external           | Internal                             |
        | segments                  | None                                 |
        | shared                    | False                                |
        | status                    | ACTIVE                               |
        | subnets                   |                                      |
        | tags                      |                                      |
        | updated_at                | 2020-08-28T15:28:06Z                 |
        +---------------------------+--------------------------------------+

    * Create a subnet on the tenant network using an IP address allocation from the private subnet pool.

    .. code-block:: console

        $ openstack subnet create --network private --subnet-pool selfservice \
          --prefix-length 24 selfservice
        +----------------------+--------------------------------------+
        | Field                | Value                                |
        +----------------------+--------------------------------------+
        | allocation_pools     | 10.0.0.2-10.0.0.254                  |
        | cidr                 | 10.0.0.0/24                          |
        | created_at           | 2020-08-28T15:29:20Z                 |
        | description          |                                      |
        | dns_nameservers      |                                      |
        | dns_publish_fixed_ip | False                                |
        | enable_dhcp          | True                                 |
        | gateway_ip           | 10.0.0.1                             |
        | host_routes          |                                      |
        | id                   | 12eec8cb-8303-4829-8b16-e9a75072fcb0 |
        | ip_version           | 4                                    |
        | ipv6_address_mode    | None                                 |
        | ipv6_ra_mode         | None                                 |
        | name                 | selfservice                          |
        | network_id           | 43643543-6edb-4c2b-a087-4553b75b6799 |
        | prefix_length        | 24                                   |
        | project_id           | 17c884da94bc4259b20ace3da6897297     |
        | revision_number      | 0                                    |
        | segment_id           | None                                 |
        | service_types        |                                      |
        | subnetpool_id        | 574f9d33-65b6-49a1-ab43-866085d06804 |
        | tags                 |                                      |
        | updated_at           | 2020-08-28T15:29:20Z                 |
        +----------------------+--------------------------------------+

6. Create and configure router

    * Create a router.

    .. code-block:: console

        $ openstack router create router
        +-------------------------+--------------------------------------+
        | Field                   | Value                                |
        +-------------------------+--------------------------------------+
        | admin_state_up          | UP                                   |
        | availability_zone_hints |                                      |
        | availability_zones      |                                      |
        | created_at              | 2020-08-28T15:30:09Z                 |
        | description             |                                      |
        | external_gateway_info   | null                                 |
        | flavor_id               | None                                 |
        | id                      | 250e5cc1-4cfc-4dff-a3a3-eb206c071621 |
        | name                    | router                               |
        | project_id              | 17c884da94bc4259b20ace3da6897297     |
        | revision_number         | 1                                    |
        | routes                  |                                      |
        | status                  | ACTIVE                               |
        | tags                    |                                      |
        | updated_at              | 2020-08-28T15:30:09Z                 |
        +-------------------------+--------------------------------------+

    * Add the private subnet as an interface on the router.

    .. code-block:: console

        $ openstack router add subnet router selfservice

    * Add the provide network as a gateway on the router

    .. code-block:: console

        $ openstack router set --external-gateway provider router

    * Verify router ports. Note: from this result, you can see what the advertised routes are.

    .. code-block:: console

        $ openstack port list --router router
        +--------------------------------------+------+-------------------+----------------------------------------------------------------------------+--------+
        | ID                                   | Name | MAC Address       | Fixed IP Addresses                                                         | Status |
        +--------------------------------------+------+-------------------+----------------------------------------------------------------------------+--------+
        | 218c455f-f565-4e37-a2ac-999da24efa66 |      | fa:16:3e:74:d8:61 | ip_address='10.0.0.1', subnet_id='12eec8cb-8303-4829-8b16-e9a75072fcb0'    | ACTIVE |
        | 44dcb7d3-b444-4177-82a1-233b1f3bed23 |      | fa:16:3e:5b:4b:2d | ip_address='172.24.4.24', subnet_id='4ed8ac88-2c19-4f94-9362-7b301e743438' | ACTIVE |
        +--------------------------------------+------+-------------------+----------------------------------------------------------------------------+--------+

7. Create and configure the BGP speaker

   The BGP speaker advertised the next-hop IP address for the tenant network prefix.

    * Create the BGP speaker.

    Replace LOCAL_AS with an appropriate local autonomous system number. The example configuration uses AS 12345.

    .. code-block:: console

        $ openstack bgp speaker create  --ip-version 4 \
          --local-as LOCAL_AS bgp-speaker
        +-----------------------------------+--------------------------------------+
        | Field                             | Value                                |
        +-----------------------------------+--------------------------------------+
        | advertise_floating_ip_host_routes | True                                 |
        | advertise_tenant_networks         | True                                 |
        | id                                | 19cdf669-4d4d-442f-bbf6-510a97ad8cd8 |
        | ip_version                        | 4                                    |
        | local_as                          | 12345                                |
        | name                              | bgp-speaker                          |
        | networks                          | []                                   |
        | peers                             | []                                   |
        | project_id                        | 17c884da94bc4259b20ace3da6897297     |
        +-----------------------------------+--------------------------------------+

    * Associate the BGP speaker with the provider network.

    A BGP speaker requires association with a provider network to determine eligible
    prefixes. After the association, the BGP speaker can advertise the tenant network
    prefixes with the corresponding router as the next-hop IP address.

    .. code-block:: console

        $ openstack bgp speaker add network bgp-speaker provider

    * Verify the association of the provider network with the BGP speaker.

    Checking the ``networks`` attribute.

    .. code-block:: console

        $ openstack bgp speaker show bgp-speaker
        +-----------------------------------+------------------------------------------+
        | Field                             | Value                                    |
        +-----------------------------------+------------------------------------------+
        | advertise_floating_ip_host_routes | True                                     |
        | advertise_tenant_networks         | True                                     |
        | id                                | 19cdf669-4d4d-442f-bbf6-510a97ad8cd8     |
        | ip_version                        | 4                                        |
        | local_as                          | 12345                                    |
        | name                              | bgp-speaker                              |
        | networks                          | ['18f9a9c0-f8f5-4360-822a-b687c1008bf7'] |
        | peers                             | []                                       |
        | project_id                        | 17c884da94bc4259b20ace3da6897297         |
        +-----------------------------------+------------------------------------------+

    * Verify the prefixes and next-hop ip addresses that the BGP speaker advertises.

    .. code-block:: console

        $ openstack bgp speaker list advertised routes bgp-speaker
        +-------------+------------+
        | destination | next_hop   |
        +-------------+------------+
        | 10.0.0.0/24 | 172.24.4.3 |
        +-------------+------------+

    * Create a BGP peer.

    Here the BGP peer is pointed to the quagga VM. Replace REMOTE_AS with an appropriate
    remote autonomous system number. The example configuration uses AS 12345 which triggers
    iBGP peering.

    .. code-block:: console

        $ openstack bgp peer create --peer-ip 10.156.18.20 \
          --remote-as REMOTE_AS bgp-peer
        +------------+--------------------------------------+
        | Field      | Value                                |
        +------------+--------------------------------------+
        | auth_type  | none                                 |
        | id         | 37291604-de77-4333-8f27-4ca336e021f2 |
        | name       | bgp-peer                             |
        | peer_ip    | 10.156.18.20                         |
        | project_id | 17c884da94bc4259b20ace3da6897297     |
        | remote_as  | 12345                                |
        +------------+--------------------------------------+

    * Add a BGP peer to the BGP speaker.

    .. code-block:: console

        $ openstack bgp speaker add peer bgp-speaker bgp-peer

    * Verify the association of the BGP peer with the BGP speaker.

    Checking the ``peers`` attribute.

    .. code-block:: console

        $ openstack bgp speaker show bgp-speaker
        +-----------------------------------+------------------------------------------+
        | Field                             | Value                                    |
        +-----------------------------------+------------------------------------------+
        | advertise_floating_ip_host_routes | True                                     |
        | advertise_tenant_networks         | True                                     |
        | id                                | 19cdf669-4d4d-442f-bbf6-510a97ad8cd8     |
        | ip_version                        | 4                                        |
        | local_as                          | 12345                                    |
        | name                              | bgp-speaker                              |
        | networks                          | ['18f9a9c0-f8f5-4360-822a-b687c1008bf7'] |
        | peers                             | ['37291604-de77-4333-8f27-4ca336e021f2'] |
        | project_id                        | 17c884da94bc4259b20ace3da6897297         |
        +-----------------------------------+------------------------------------------+

8. Schedule the BGP speaker to an agent.

    * Schedule the BGP speaker to ``BGP dynamic routing agent``

    With the default scheduler configuration, the first BGP speaker is
    scheduled to the first dynamic routing agent automatically.
    So for a simple setup, there is nothing to be done here.

    * Verify scheduling of the BGP speaker to the agent.

    .. code-block:: console

        $ openstack bgp dragent list --bgp-speaker bgp-speaker
        +--------------------------------------+---------------------------+----------------+-------+
        | id                                   | host                      | admin_state_up | alive |
        +--------------------------------------+---------------------------+----------------+-------+
        | 239996c8-2d59-4131-98b8-d64372c812cc | devstack-bgp-dr           | True           | :-)   |
        +--------------------------------------+---------------------------+----------------+-------+
