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
devices that support dynamic routing protocol such as routers. Neutron dynamic routing project that
consists of a service plugin-in and agent can advertise neutron private network to outside of
OpenStack. This document will describe how to test the Dynamic Routing functionalities, introduce
what the environment architecture is for dynamic routing test and show how to setup dynamic routing
environment using Devstack.

Environment Architecture
-------------------------

Using the following example architecture as a test environment to deploy neutron-dynamic-routing in
your environment. The example architecture will deploy an all-in-one OpenStack and pick up an Ubuntu
VM running Quagga as a router outside of OpenStack . See following::



                                                                    +--------------+
                                                       10.156.18.20 |              |
                                 +----------------------------------|   Quagga     |
                                 | BGP Peering Session              |   Router     |
                                 |                                  |  172.24.4.3  |
                                 |                                  +--------------+
                                 |                                         |
                                 |10.156.18.21                             |       External Network(172.24.4.0/24)
                --------------------------------------------------------------------------------------------------                                        |ETH0    |br-ex
                        +---------------------------------------+
                        |        |        |                     |
                        |        |        |                     |
                        |        |        +-------+             |
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

    git clone https://git.openstack.org/openstack-dev/devstack.git

2. Enable neutron-dynamic-routing::

    [[local|localrc]]
    enable_plugin neutron-dynamic-routing https://git.openstack.org/openstack/neutron-dynamic-routing

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

3. Update quagga deamon file.

   You can enable/disable the daemons routing in the /etc/quagga/daemons file. Update /etc/quagga/deamons to enable zebra and bgp::

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

    # set router-id to the network address we announce
    bgp router-id 10.156.18.20

    # declare a router with local-as 1000
    router bgp 1000

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

6. Restart the Quagga::

    $ sudo /etc/init.d/quagga restart

Service Test
-------------

1. As the dynamic routing is only supported by admin, source the devstack admin credentials::

    $ . devstack/openrc admin admin

2. Verify the neutron dynamic routing agent is running.

.. code-block:: console

    $ neutron agent-list --agent-type 'BGP dynamic routing agent'
    +--------------------+--------------------+--------------------+-------------------+-------+----------------+---------------------+
    | id                 | agent_type         | host               | availability_zone | alive | admin_state_up | binary              |
    +--------------------+--------------------+--------------------+-------------------+-------+----------------+---------------------+
    | 69ad386f-e055-4284 | BGP dynamic        | yang-devstack-     |                   | :-)   | True           | neutron-bgp-dragent |
    | -8c8e-ef9bd540705c | routing agent      | ubuntu-1604        |                   |       |                |                     |
    +--------------------+--------------------+--------------------+-------------------+-------+----------------+---------------------+


3. Create an address scope.

   The provider(external) and tenant networks must belong to the same address scope
   for the agent to advertise those tenant network prefixes.

    .. code-block:: console

        $ neutron address-scope-create --shared public 4
        Created a new address_scope:
        +------------+--------------------------------------+
        | Field      | Value                                |
        +------------+--------------------------------------+
        | id         | c02c358a-9d35-43ea-8313-986b3e4a91c0 |
        | ip_version | 4                                    |
        | name       | public                               |
        | shared     | True                                 |
        | tenant_id  | b3ac05ef10bf441fbf4aa17f16ae1e6d     |
        +------------+--------------------------------------+

4. Create subnet pools. The provider and tenant networks use different pools.

    * Create the provider network pool.

    .. code-block:: console

        $ neutron subnetpool-create --pool-prefix 172.24.4.0/24 \
          --address-scope public provider
        Created a new subnetpool:
        +-------------------+--------------------------------------+
        | Field             | Value                                |
        +-------------------+--------------------------------------+
        | address_scope_id  | 238aaf8f-f91a-4538-b6b2-c0140111cf69 |
        | created_at        | 2016-06-30T07:03:52                  |
        | default_prefixlen | 8                                    |
        | default_quota     |                                      |
        | description       |                                      |
        | id                | 8439bfee-e09c-40a9-a3ea-8cf7212b7ba9 |
        | ip_version        | 4                                    |
        | is_default        | False                                |
        | max_prefixlen     | 32                                   |
        | min_prefixlen     | 8                                    |
        | name              | provider                             |
        | prefixes          | 172.24.4.0/24                        |
        | shared            | False                                |
        | tenant_id         | 21734c4383284cf9906b7fe8246bffb1     |
        | updated_at        | 2016-06-30T07:03:52                  |
        +-------------------+--------------------------------------+

    * Create tenant network pool.

    .. code-block:: console

        $ neutron subnetpool-create --pool-prefix 10.0.0.0/16 \
          --address-scope public --shared selfservice
        Created a new subnetpool:
        +-------------------+--------------------------------------+
        | Field             | Value                                |
        +-------------------+--------------------------------------+
        | address_scope_id  | c02c358a-9d35-43ea-8313-986b3e4a91c0 |
        | created_at        | 2016-06-30T07:08:30                  |
        | default_prefixlen | 8                                    |
        | default_quota     |                                      |
        | description       |                                      |
        | id                | c7e9737a-cfd3-45b5-a861-d1cee1135a92 |
        | ip_version        | 4                                    |
        | is_default        | False                                |
        | max_prefixlen     | 32                                   |
        | min_prefixlen     | 8                                    |
        | name              | selfservice                          |
        | prefixes          | 10.0.0.0/16                          |
        | shared            | True                                 |
        | tenant_id         | b3ac05ef10bf441fbf4aa17f16ae1e6d     |
        | updated_at        | 2016-06-30T07:08:30                  |
        +-------------------+--------------------------------------+

5. Create the provider and tenant networks.

    * Create the provider network.

    .. code-block:: console

        $ neutron net-create --router:external True --provider:physical_network provider \
          --provider:network_type flat provider
        Created a new network:
        +---------------------------+--------------------------------------+
        | Field                     | Value                                |
        +---------------------------+--------------------------------------+
        | admin_state_up            | True                                 |
        | id                        | 68ec148c-181f-4656-8334-8f4eb148689d |
        | name                      | provider                             |
        | provider:network_type     | flat                                 |
        | provider:physical_network | provider                             |
        | provider:segmentation_id  |                                      |
        | router:external           | True                                 |
        | shared                    | False                                |
        | status                    | ACTIVE                               |
        | subnets                   |                                      |
        | tenant_id                 | b3ac05ef10bf441fbf4aa17f16ae1e6d     |
        +---------------------------+--------------------------------------+

    * Create a subnet on the provider network using an IP address allocation from the provider subnet pool.

    .. code-block:: console

        $ neutron subnet-create --name provider --subnetpool provider \
          --prefixlen 24 provider
        Created a new subnet:
        +-------------------+------------------------------------------------+
        | Field             | Value                                          |
        +-------------------+------------------------------------------------+
        | allocation_pools  | {"start": "172.24.4.2", "end": "172.24.4.254"} |
        | cidr              | 172.24.4.0/24                                  |
        | created_at        | 2016-03-17T23:17:16                            |
        | description       |                                                |
        | dns_nameservers   |                                                |
        | enable_dhcp       | True                                           |
        | gateway_ip        | 172.24.4.1                                     |
        | host_routes       |                                                |
        | id                | 8ed65d41-2b2a-4f3a-9f92-45adb266e01a           |
        | ip_version        | 4                                              |
        | ipv6_address_mode |                                                |
        | ipv6_ra_mode      |                                                |
        | name              | provider                                       |
        | network_id        | 68ec148c-181f-4656-8334-8f4eb148689d           |
        | subnetpool_id     | 3771c0e7-7096-46d3-a3bd-699c58e70259           |
        | tenant_id         | b3ac05ef10bf441fbf4aa17f16ae1e6d               |
        | updated_at        | 2016-03-17T23:17:16                            |
        +-------------------+------------------------------------------------+

    * Create the tenant network.

    .. code-block:: console

        $ neutron net-create private
        Created a new network:
        +---------------------------+--------------------------------------+
        | Field                     | Value                                |
        +---------------------------+--------------------------------------+
        | admin_state_up            | True                                 |
        | id                        | 01da3e19-129f-4d26-b065-255ade0e5e2c |
        | name                      | private                              |
        | shared                    | False                                |
        | status                    | ACTIVE                               |
        | subnets                   |                                      |
        | tenant_id                 | b3ac05ef10bf441fbf4aa17f16ae1e6d     |
        +---------------------------+--------------------------------------+

    * Create a subnet on the tenant network using an IP address allocation from the private subnet pool.

    .. code-block:: console

        $ neutron subnet-create --name selfservice --subnetpool private \
          --prefixlen 24 private
        Created a new subnet:
        +-------------------+--------------------------------------------+
        | Field             | Value                                      |
        +-------------------+--------------------------------------------+
        | allocation_pools  | {"start": "10.0.0.2", "end": "10.0.0.254"} |
        | cidr              | 10.0.0.0/24                                |
        | created_at        | 2016-03-17T23:20:20                        |
        | description       |                                            |
        | dns_nameservers   |                                            |
        | enable_dhcp       | True                                       |
        | gateway_ip        | 10.0.0.1                                   |
        | host_routes       |                                            |
        | id                | 8edd3dc2-df40-4d71-816e-a4586d61c809       |
        | ip_version        | 4                                          |
        | ipv6_address_mode |                                            |
        | ipv6_ra_mode      |                                            |
        | name              | private                                    |
        | network_id        | 01da3e19-129f-4d26-b065-255ade0e5e2c       |
        | subnetpool_id     | c7e9737a-cfd3-45b5-a861-d1cee1135a92       |
        | tenant_id         | b3ac05ef10bf441fbf4aa17f16ae1e6d           |
        | updated_at        | 2016-03-17T23:20:20                        |
        +-------------------+--------------------------------------------+

6. Create and configure router

    * Create a router.

    .. code-block:: console

        $ neutron router-create router
        +-----------------------+--------------------------------------+
        | Field                 | Value                                |
        +-----------------------+--------------------------------------+
        | admin_state_up        | True                                 |
        | external_gateway_info |                                      |
        | id                    | 49439b14-f6ee-420d-8c48-d3767fadcb3a |
        | name                  | router                               |
        | status                | ACTIVE                               |
        | tenant_id             | b3ac05ef10bf441fbf4aa17f16ae1e6d     |
        +-----------------------+--------------------------------------+

    * Add the private subnet as an interface on the router.

    .. code-block:: console

        $ neutron router-interface-add router selfservice
        Added interface 969a1d4b-7fa1-4346-9963-de06becab87a to router router.

    * Add the provide network as a gateway on the router

    .. code-block:: console

        $ neutron router-gateway-set router provider
        Set gateway for router router

    * Verify router ports. Note: from this result, you can see what the advertised routes are.

    .. code-block:: console

        $ neutron router-port-list router
        +--------------------------------------+------+-------------------+----------------------------------------------------+
        | id                                   | name | mac_address       | fixed_ips                                          |
        +--------------------------------------+------+-------------------+----------------------------------------------------+
        | dc675aab-5a8b-462c-872e-2f791b6c1730 |      | fa:16:3e:e5:a2:d2 | {"subnet_id": "1c6b725e-                           |
        |                                      |      |                   | 890e-4454-8842-7ff22ffa704b", "ip_address":        |
        |                                      |      |                   | "10.0.0.1"}                                        |
        | e15c701d-868f-4171-a282-e6a4567a8d83 |      | fa:16:3e:28:86:4c | {"subnet_id":                                      |
        |                                      |      |                   | "b442c453-7e4a-4568-9d70-1dde91a65fbb",            |
        |                                      |      |                   | "ip_address": "172.24.4.2"}                        |
        +--------------------------------------+------+-------------------+----------------------------------------------------+

7. Create and configure the BGP speaker

   The BGP speaker advertised the next-hop IP address for the tenant network prefix.

    * Create the BGP speaker.

    Replace LOCAL_AS with an appropriate local autonomous system number. The example configuration uses AS 12345.

    .. code-block:: console

        $ neutron bgp-speaker-create --ip-version 4 \
          --local-as LOCAL_AS bgp-speaker
        Created a new bgp_speaker:
        +-----------------------------------+--------------------------------------+
        | Field                             | Value                                |
        +-----------------------------------+--------------------------------------+
        | advertise_floating_ip_host_routes | True                                 |
        | advertise_tenant_networks         | True                                 |
        | id                                | 5f227f14-4f46-4eca-9524-fc5a1eabc358 |
        | ip_version                        | 4                                    |
        | local_as                          | 12345                                |
        | name                              | bgp-speaker                          |
        | networks                          |                                      |
        | peers                             |                                      |
        | tenant_id                         | b3ac05ef10bf441fbf4aa17f16ae1e6d     |
        +-----------------------------------+--------------------------------------+

    * Associate the BGP speaker with the provider network.

    A BGP speaker requires association with a provider network to determine eligible
    prefixes. After the association, the BGP speaker can advertise the tenant network
    prefixes with the corresponding router as the next-hop IP address.

    .. code-block:: console

        $ neutron bgp-speaker-network-add bgp-speaker provider
        Added network provider to BGP speaker bgpspeaker.

    * Verify the association of the provider network with the BGP speaker.

    Checking the ``networks`` attribute.

    .. code-block:: console

        $ neutron bgp-speaker-show bgpspeaker
        +-----------------------------------+--------------------------------------+
        | Field                             | Value                                |
        +-----------------------------------+--------------------------------------+
        | advertise_floating_ip_host_routes | True                                 |
        | advertise_tenant_networks         | True                                 |
        | id                                | 5f227f14-4f46-4eca-9524-fc5a1eabc358 |
        | ip_version                        | 4                                    |
        | local_as                          | 12345                                |
        | name                              | bgp-speaker                          |
        | networks                          | 68ec148c-181f-4656-8334-8f4eb148689d |
        | peers                             |                                      |
        | tenant_id                         | b3ac05ef10bf441fbf4aa17f16ae1e6d     |
        +-----------------------------------+--------------------------------------+

    * Verify the prefixes and next-hop ip addresses that the BGP speaker advertises.

    .. code-block:: console

        $ neutron bgp-speaker-advertiseroute-list bgpspeaker
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

        $ neutron bgp-peer-create --peer-ip 10.156.18.20 \
          --remote-as REMOTE_AS bgp-peer
        Created a new bgp_peer:
        +-----------+--------------------------------------+
        | Field     | Value                                |
        +-----------+--------------------------------------+
        | auth_type | none                                 |
        | id        | 35c89ca0-ac5a-4298-a815-0b073c2362e9 |
        | name      | bgp-peer                             |
        | peer_ip   | 10.156.18.20                         |
        | remote_as | 12345                                |
        | tenant_id | b3ac05ef10bf441fbf4aa17f16ae1e6d     |
        +-----------+--------------------------------------+

    * Add a BGP peer to the BGP speaker.

    .. code-block:: console

        $ neutron bgp-speaker-peer-add bgp-speaker bgp-peer
        Added BGP peer bgppeer to BGP speaker bgpspeaker.

    * Verify the association of the BGP peer with the BGP speaker.

    Checking the ``peers`` attribute.

    .. code-block:: console

        $ neutron bgp-speaker-show bgp-speaker
        +-----------------------------------+--------------------------------------+
        | Field                             | Value                                |
        +-----------------------------------+--------------------------------------+
        | advertise_floating_ip_host_routes | True                                 |
        | advertise_tenant_networks         | True                                 |
        | id                                | 5f227f14-4f46-4eca-9524-fc5a1eabc358 |
        | ip_version                        | 4                                    |
        | local_as                          | 12345                                |
        | name                              | bgp-speaker                          |
        | networks                          | 68ec148c-181f-4656-8334-8f4eb148689d |
        | peers                             | 35c89ca0-ac5a-4298-a815-0b073c2362e9 |
        | tenant_id                         | b3ac05ef10bf441fbf4aa17f16ae1e6d     |
        +-----------------------------------+--------------------------------------+

8. Schedule the BGP speaker to an agent.

    * Schedule the BGP speaker to ``BGP dynamic routing agent``

    BGP speakers require manual scheduling to an agent. BGP speakers only form peering sessions.

    .. code-block:: console

        $ neutron bgp-speaker-network-add bgp-speaker provider
        Added network provider to BGP speaker bgpspeaker.

    * Verify scheduling of the BGP speaker to the agent.

    .. code-block:: console

        neutron bgp-dragent-list-hosting-speaker bgp-speaker
        +--------------------------------------+---------------------------+----------------+-------+
        | id                                   | host                      | admin_state_up | alive |
        +--------------------------------------+---------------------------+----------------+-------+
        | 69ad386f-e055-4284-8c8e-ef9bd540705c | yang-devstack-ubuntu-1604 | True           | :-)   |
        +--------------------------------------+---------------------------+----------------+-------+
