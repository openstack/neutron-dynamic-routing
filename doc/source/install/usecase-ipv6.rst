..
      Copyright 2023 OSISM GmbH

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

======================================================
Use-case: Global IPv6 connectivity for tenant networks
======================================================

Motivation
----------

With IPv6 the use of NAT is strongly deprecated with the intention of allowing
direct end-to-end connectivity between hosts. Thus the Neutron implementation
does not provide a mechanism to create floating IPv6 addresses.

As a consequence, projects will want globally routed IPv6 adresses directly connected
to their instances. As this will be difficult to achieve if you continue to allow
your projects to choose their own favorite range of addresses, there are two
possible solutions:

1. Set up a shared network to which your instances will be directly connected and
   configure this network with a public IPv6 prefix (*provider network*). This
   way instances will get a public IPv6 address that they can use without any
   restriction.
2. Configure a *subnet pool* containing a range of public IPv6 prefixes, so that
   projects may configure their own networks by requesting a slice from that
   subnet pool instead of choosing their own.

Option 1 has some drawbacks, though:

- It places all projects into a single shared network, complicating things like
  per-project firewall rules or rDNS management.
- If you want to dual-stack your instances (i.e. provide them with IPv4 and IPv6
  connectivity at the same time), you either need to use two different networks
  and attach your instances to both of them, or you will need to also assign a
  public IPv4 address to every instance, which may be considered a rather wasteful
  approach to dealing with this scarce resource.

So this document will describe how to set up option 2 by deploying *dynamic routing*.

Preparation
-----------

Address scope
~~~~~~~~~~~~~

Start by setting up an address scope that will be used by the BGP agent in order
to select the set of prefixes to be announced over the BGP sessions. All commands shown
in this section will require you to use admin credentials::

    $ openstack address scope create --share --ip-version 6 ipv6-global
    +------------+--------------------------------------+
    | Field      | Value                                |
    +------------+--------------------------------------+
    | id         | ee2ee196-156c-424e-81e5-4d029c66190a |
    | ip_version | 6                                    |
    | name       | ipv6-global                          |
    | project_id | 6de6f29dcf904ab8a12e8ca558f532e9     |
    | shared     | True                                 |
    +------------+--------------------------------------+

Subnet pool
~~~~~~~~~~~

Next create the subnet pool that your projects will use to configure their subnets
with. For a real deployment, use a globally routable network prefix instead
of the documentation prefix that is used in this example::

    $ openstack subnet pool create --address-scope ipv6-global --share --default \
    >   --pool-prefix 2001:db8:1234::/48 --default-prefix-length 64 \
    >   --min-prefix-length 64 --max-prefix-length 124 default-pool-ipv6
    +-------------------+--------------------------------------+
    | Field             | Value                                |
    +-------------------+--------------------------------------+
    | address_scope_id  | ee2ee196-156c-424e-81e5-4d029c66190a |
    | created_at        | 2017-02-24T15:28:27Z                 |
    | default_prefixlen | 64                                   |
    | default_quota     | None                                 |
    | description       |                                      |
    | id                | 4c1661ba-b24c-4fda-8815-3f1fd29281af |
    | ip_version        | 6                                    |
    | is_default        | True                                 |
    | max_prefixlen     | 124                                  |
    | min_prefixlen     | 64                                   |
    | name              | default-pool-ipv6                    |
    | prefixes          | 2001:db8:1234::/48                   |
    | project_id        | 6de6f29dcf904ab8a12e8ca558f532e9     |
    | revision_number   | 1                                    |
    | shared            | True                                 |
    | updated_at        | 2017-02-24T15:28:27Z                 |
    +-------------------+--------------------------------------+

Public network
~~~~~~~~~~~~~~

Your public network, the network that the gateway ports of the project routers
will be connected to, needs to be configured with the

For an existing deployment, you will usually already have a network defined
using public IPv4 addresses for floating IPs and router gateway ports. This
is the network that an IPv6 subnet needs to be added to, using same address
scope that was used for the subnet pool above.

If you do not yet have such a network, you can create it with::

    $ openstack network create --provider-network-type flat --provider-physical-network public --external public
    <output skipped>

The exact parameters that you need to specify depend on your deployment and
are out of scope for this document, see the Neutron documentation for
more details.

There are now three different options in order to make sure that you have
an IPv6 subnet on this public network which is associated with the required
address scope:

Using the shared subnet pool
++++++++++++++++++++++++++++

Create the IPv6 subnet on the public network from the shared subnet pool
above::

    $ openstack subnet create --ip-version 6 --use-default-subnet-pool --network public public-ip6
    +-------------------+----------------------------------------------------------+
    | Field             | Value                                                    |
    +-------------------+----------------------------------------------------------+
    | allocation_pools  | 2001:db8:1234::2-2001:db8:1234:0:ffff:ffff:ffff:ffff     |
    | cidr              | 2001:db8:1234::/64                                       |
    | created_at        | 2017-02-27T10:23:00Z                                     |
    | description       |                                                          |
    | dns_nameservers   |                                                          |
    | enable_dhcp       | True                                                     |
    | gateway_ip        | 2001:db8:1234::1                                         |
    | host_routes       |                                                          |
    | id                | 77551166-fb97-4ea5-912a-c17c75a05eda                     |
    | ip_version        | 6                                                        |
    | ipv6_address_mode | None                                                     |
    | ipv6_ra_mode      | None                                                     |
    | name              | public-ip6                                               |
    | network_id        | 28c08355-cb8f-4b1b-b5fd-f5442e531b28                     |
    | project_id        | 6de6f29dcf904ab8a12e8ca558f532e9                         |
    | revision_number   | 2                                                        |
    | segment_id        | None                                                     |
    | service_types     |                                                          |
    | subnetpool_id     | 56a1b34b-7e0a-4a76-aac9-8893314ee2a4                     |
    | updated_at        | 2017-02-27T10:23:00Z                                     |
    +-------------------+----------------------------------------------------------+

Using a dedicated subnet pool
+++++++++++++++++++++++++++++

Create a second subnet pool containing just the specific prefix that you
want to use for your public network::

    $ openstack subnet pool create --address-scope ipv6-global --pool-prefix 2001:db8:4321:42::/64 --default-prefix-length 64 public-pool
    +-------------------+--------------------------------------+
    | Field             | Value                                |
    +-------------------+--------------------------------------+
    | address_scope_id  | ee2ee196-156c-424e-81e5-4d029c66190a |
    | created_at        | 2017-02-27T10:13:38Z                 |
    | default_prefixlen | 64                                   |
    | default_quota     | None                                 |
    | description       |                                      |
    | id                | 56a1b34b-7e0a-4a76-aac9-8893314ee2a4 |
    | ip_version        | 6                                    |
    | is_default        | False                                |
    | max_prefixlen     | 128                                  |
    | min_prefixlen     | 64                                   |
    | name              | public-pool                          |
    | prefixes          | 2001:db8:4321:42::/64                |
    | project_id        | 6de6f29dcf904ab8a12e8ca558f532e9     |
    | revision_number   | 1                                    |
    | shared            | False                                |
    | updated_at        | 2017-02-27T10:13:38Z                 |
    +-------------------+--------------------------------------+

Create the IPv6 subnet on your public network::

    $ openstack subnet create --ip-version 6 --subnet-pool public-pool --network public public-ip6
    +-------------------+----------------------------------------------------------+
    | Field             | Value                                                    |
    +-------------------+----------------------------------------------------------+
    | allocation_pools  | 2001:db8:4321:42::2-2001:db8:4321:42:ffff:ffff:ffff:ffff |
    | cidr              | 2001:db8:4321:42::/64                                    |
    | created_at        | 2017-02-27T10:23:00Z                                     |
    | description       |                                                          |
    | dns_nameservers   |                                                          |
    | enable_dhcp       | True                                                     |
    | gateway_ip        | 2001:db8:4321:42::1                                      |
    | host_routes       |                                                          |
    | id                | 77551166-fb97-4ea5-912a-c17c75a05eda                     |
    | ip_version        | 6                                                        |
    | ipv6_address_mode | None                                                     |
    | ipv6_ra_mode      | None                                                     |
    | name              | public-ip6                                               |
    | network_id        | 28c08355-cb8f-4b1b-b5fd-f5442e531b28                     |
    | project_id        | 6de6f29dcf904ab8a12e8ca558f532e9                         |
    | revision_number   | 2                                                        |
    | segment_id        | None                                                     |
    | service_types     |                                                          |
    | subnetpool_id     | 56a1b34b-7e0a-4a76-aac9-8893314ee2a4                     |
    | updated_at        | 2017-02-27T10:23:00Z                                     |
    +-------------------+----------------------------------------------------------+

Using subnet onboarding
+++++++++++++++++++++++

If you have enabled the ``subnet_onboard`` extension in your Neutron deployment, there is
the simpler option of simply onboarding an existing IPv6 subnet on your public network onto
the default IPv6 subnet pool created above::

    $ openstack network onboard subnets public default-pool-ipv6
    $ # This command does not generate any output

Verifying the address scope
+++++++++++++++++++++++++++

After you have create the public IPv6 subnet using one of the options shown above, verify
that the address scope for IPv6 indeed got set for the public network::

    $ openstack network show public
    +---------------------------+--------------------------------------+
    | Field                     | Value                                |
    +---------------------------+--------------------------------------+
    | admin_state_up            | UP                                   |
    | availability_zone_hints   |                                      |
    | availability_zones        |                                      |
    | created_at                | 2017-02-27T10:21:04Z                 |
    | description               |                                      |
    | dns_domain                | None                                 |
    | id                        | 28c08355-cb8f-4b1b-b5fd-f5442e531b28 |
    | ipv4_address_scope        | None                                 |
    | ipv6_address_scope        | ee2ee196-156c-424e-81e5-4d029c66190a |
    | is_default                | False                                |
    | mtu                       | 1500                                 |
    | name                      | public                               |
    | port_security_enabled     | True                                 |
    | project_id                | 6de6f29dcf904ab8a12e8ca558f532e9     |
    | provider:network_type     | flat                                 |
    | provider:physical_network | external                             |
    | provider:segmentation_id  | None                                 |
    | qos_policy_id             | None                                 |
    | revision_number           | 6                                    |
    | router:external           | External                             |
    | segments                  | None                                 |
    | shared                    | False                                |
    | status                    | ACTIVE                               |
    | subnets                   | 77551166-fb97-4ea5-912a-c17c75a05eda |
    | updated_at                | 2017-02-27T10:23:00Z                 |
    +---------------------------+--------------------------------------+

.. note::
   It is essential that the same address scope is being used both for the
   public subnet and the tenant subnets. If there is a mismatch, the
   BGP announcement will not happen and connectivity will be broken.

Dynamic routing setup
---------------------

Now that you have prepared the network configuration, the next step is to
configure the dynamic routing part. First add the service plugin to your
``neutron.conf`` file. Note that depending on your deployment, there may
be other plugins already configured, keep those unchanged, just add the
BGP plugin::

    [DEFAULT]
    # You may have other plugins enabled here depending on your environment
    # Important thing is you add the BgpPlugin to the list
    service_plugins = neutron_dynamic_routing.services.bgp.bgp_plugin.BgpPlugin,neutron.services.l3_router.l3_router_plugin.L3RouterPlugin
    # In case you run into issues, this will also be helpful
    debug = true

You need to restart the Neutron service in order activate the plugin.

Now you can create your first BGP speaker. Set the IP version to 6, select some
private ASN that can be used for this POC and disable advertising floating IPs::

    $ openstack bgp speaker create --ip-version 6 --local-as 65000 --no-advertise-floating-ip-host-routes bgp1
    +-----------------------------------+--------------------------------------+
    | Field                             | Value                                |
    +-----------------------------------+--------------------------------------+
    | advertise_floating_ip_host_routes | False                                |
    | advertise_tenant_networks         | True                                 |
    | id                                | b9547458-7bdd-4738-bd57-a985055fc59c |
    | ip_version                        | 6                                    |
    | local_as                          | 65000                                |
    | name                              | bgp1                                 |
    | networks                          | []                                   |
    | peers                             | []                                   |
    | project_id                        | c67d6ba16ea2484597061245e5258c1e     |
    +-----------------------------------+--------------------------------------+

Add your public network to this speaker, indicating that you want to advertise all those
tenant networks here, which have a router with the public network as gateway::

    $ openstack bgp speaker add network bgp1 public
    $ # This command does not generate any output

Assuming your external router has the address 2001:db8:4321:e0::1, configure it as
BGP peer and add it to the BGP speaker::

    $ openstack bgp peer create --peer-ip 2001:db8:4321:e0::1 --remote-as 65001 bgp-peer1
    +------------+--------------------------------------+
    | Field      | Value                                |
    +------------+--------------------------------------+
    | auth_type  | none                                 |
    | id         | 0183260e-b1d0-40ae-994f-075668b99676 |
    | name       | bgp-peer1                            |
    | peer_ip    | 2001:db8:4321:e0::1                  |
    | project_id | c67d6ba16ea2484597061245e5258c1e     |
    | remote_as  | 65001                                |
    | tenant_id  | c67d6ba16ea2484597061245e5258c1e     |
    +------------+--------------------------------------+
    $ openstack bgp speaker add peer bgp1 bgp-peer1
    $ # This command does not generate any output

Now configure the Neutron BGP agent, add the following data into your ``bgp_dragent.ini``
configuration file::

    [BGP]
    bgp_speaker_driver = neutron_dynamic_routing.services.bgp.agent.driver.os_ken.driver.OsKenBgpDriver

    # 32-bit BGP identifier, typically an IPv4 address owned by the system running
    # the BGP DrAgent.
    bgp_router_id = 192.0.2.42

Again you will have to restart the agent in order for it to pick up the new
configuration. If all goes well, the agent should register itself in your setup::

    $ openstack network agent list --agent-type bgp
    +--------------------------------------+---------------------------+--------------+-------------------+-------+-------+---------------------+
    | ID                                   | Agent Type                | Host         | Availability Zone | Alive | State | Binary              |
    +--------------------------------------+---------------------------+--------------+-------------------+-------+-------+---------------------+
    | 68d6e83c-db04-4711-b031-44cf3fb51bb7 | BGP dynamic routing agent | network-node | None              | :-)   | UP    | neutron-bgp-dragent |
    +--------------------------------------+---------------------------+--------------+-------------------+-------+-------+---------------------+

As the final step, use the agent ID from above and tell the agent that it
should host our BGP speaker::

    $ openstack bgp dragent add speaker 68d6e83c-db04-4711-b031-44cf3fb51bb7 bgp1
    $ # This command does not generate any output

The view from the outside
-------------------------

The final step is to configure your outside router to accept the BGP session
from the Neutron dynamic routing agent, so it can receive the prefix
announcements and forward traffic accordingly.

In this example we assume a system running [BIRD](http://bird.network.cz/), which
we configure to be the remote end of the BGP session like this::

    protocol bgp bgp1 {
      description "Neutron agent";
      passive on;
      local 2001:db8:4321:e0::1 as 65001;
      neighbor 2001:db8:4321:e0::42 as 65000;
    }

Verify that the session gets established as expected::

    bird> show proto bgp1
    name     proto    table    state  since       info
    bgp1     BGP      master   up     00:01:50    Established

Tenant networks
---------------

You have now prepared everything on the admin side of things, so let's have
a look at how your users should configure their networking.
The commands in this section are meant to be executed with user credentials::

    $ openstack network create mynet
    +---------------------------+--------------------------------------+
    | Field                     | Value                                |
    +---------------------------+--------------------------------------+
    | admin_state_up            | UP                                   |
    | availability_zone_hints   |                                      |
    | availability_zones        |                                      |
    | created_at                | 2017-02-27T10:26:22Z                 |
    | description               |                                      |
    | dns_domain                | None                                 |
    | id                        | 1f20da97-ddd4-40f8-b8d3-6321de8671a0 |
    | ipv4_address_scope        | None                                 |
    | ipv6_address_scope        | None                                 |
    | is_default                | None                                 |
    | mtu                       | 1500                                 |
    | name                      | mynet                                |
    | port_security_enabled     | True                                 |
    | project_id                | 6de6f29dcf904ab8a12e8ca558f532e9     |
    | provider:network_type     | None                                 |
    | provider:physical_network | None                                 |
    | provider:segmentation_id  | None                                 |
    | qos_policy_id             | None                                 |
    | revision_number           | 3                                    |
    | router:external           | Internal                             |
    | segments                  | None                                 |
    | shared                    | False                                |
    | status                    | ACTIVE                               |
    | subnets                   |                                      |
    | updated_at                | 2017-02-27T10:26:22Z                 |
    +---------------------------+--------------------------------------+

In order to add an IPv6 prefix, simply request one from the default pool::

    $ openstack subnet create --ip-version 6 --use-default-subnet-pool \
    > --ipv6-address-mode slaac --ipv6-ra-mode slaac --network mynet mysubnet
    +------------------------+--------------------------------------------------------+
    | Field                  | Value                                                  |
    +------------------------+--------------------------------------------------------+
    | allocation_pools       | 2001:db8:1234:1::2-2001:db8:1234:1:ffff:ffff:ffff:ffff |
    | cidr                   | 2001:db8:1234:1::/64                                   |
    | created_at             | 2017-02-27T11:14:23Z                                   |
    | description            |                                                        |
    | dns_nameservers        |                                                        |
    | enable_dhcp            | True                                                   |
    | gateway_ip             | 2001:db8:1234:1::1                                     |
    | host_routes            |                                                        |
    | id                     | 193f7620-6c4c-4adc-9bb5-ff73c9b08d59                   |
    | ip_version             | 6                                                      |
    | ipv6_address_mode      | slaac                                                  |
    | ipv6_ra_mode           | slaac                                                  |
    | name                   | mysubnet                                               |
    | network_id             | 1f20da97-ddd4-40f8-b8d3-6321de8671a0                   |
    | project_id             | 6de6f29dcf904ab8a12e8ca558f532e9                       |
    | revision_number        | 2                                                      |
    | segment_id             | None                                                   |
    | service_types          |                                                        |
    | subnetpool_id          | 4c1661ba-b24c-4fda-8815-3f1fd29281af                   |
    | updated_at             | 2017-02-27T11:14:23Z                                   |
    | use_default_subnetpool | true                                                   |
    +------------------------+--------------------------------------------------------+

For outside connectivity create a router, add an interface into your project net and set the gateway to be
the public network::

    $ openstack router create router1
    +-------------------------+--------------------------------------+
    | Field                   | Value                                |
    +-------------------------+--------------------------------------+
    | admin_state_up          | UP                                   |
    | availability_zone_hints |                                      |
    | availability_zones      |                                      |
    | created_at              | 2017-02-27T12:59:06Z                 |
    | description             |                                      |
    | distributed             | False                                |
    | external_gateway_info   | None                                 |
    | flavor_id               | None                                 |
    | ha                      | False                                |
    | id                      | d2db0603-fda2-4305-a1de-e793a36c0770 |
    | name                    | router1                              |
    | project_id              | 6de6f29dcf904ab8a12e8ca558f532e9     |
    | revision_number         | None                                 |
    | routes                  |                                      |
    | status                  | ACTIVE                               |
    | updated_at              | 2017-02-27T12:59:06Z                 |
    +-------------------------+--------------------------------------+
    $ openstack router add subnet router1 mysubnet
    $ openstack router set --external-gateway public router1

Finally boot an instance and verify that it gets an IPv6 address assigned::

    $ openstack server create --flavor c1 --image cirros vm1
    $ openstack server list
    +--------------------------------------+------+--------+-------------+--------------------------------------------+------------+
    | ID                                   | Name | Status | Power State | Networks                                   | Image Name |
    +--------------------------------------+------+--------+-------------+--------------------------------------------+------------+
    | 17b2ac04-9a17-45ff-be30-401aa8331a66 | vm1  | ACTIVE | Running     | mynet=2001:db8:1234:1:f816:3eff:fe53:f89e  | cirros     |
    +--------------------------------------+------+--------+-------------+--------------------------------------------+------------+
    $ openstack console log show vm1 | grep -A1 -B1 2001
    eth0      Link encap:Ethernet  HWaddr FA:16:3E:53:F8:9E
              inet6 addr: 2001:db8:1234:1:f816:3eff:fe53:f89e/64 Scope:Global
              inet6 addr: fe80::f816:3eff:fe53:f89e/64 Scope:Link

.. note::

   Most cloud images are built to insist on receiving an IPv4 address via DHCP,
   so there will be a considerable delay durging booting while waiting for this
   to run into a timeout. In order to avoid the resulting delay, you could add
   an IPv4 subnet to your project net.

.. note::

   There is a similar concern regarding access to the metadata provided by the
   compute service. While Neutron does provide the option to access metadata via
   IPv6, this is not available in all deployments and not supported by all cloud
   images. You can work around this either by adding and IPv4 subnet like mentioned
   above or by using the config drive option to provide metadata to your instance.

Verification
------------

As an admin you can now verify that the tenant network gets listed for advertisement::

    $ openstack bgp speaker list advertised routes bgp1
    +----+--------------------+---------------------+
    | ID | Destination        | Nexthop             |
    +----+--------------------+---------------------+
    |    | 2001:db8:1234::/64 | 2001:db8:4321:42::c |
    +----+--------------------+---------------------+

And verify it is being seen on your outside router::

    bird> show route 2001:db8:1234:1::/64
    2001:db8:1234:1::/64 via 2001:db8:4321:2::5 on ens3 [bgp1 12:06:50 from 2001:db8:4321:e0::42] * (100/0) [i]

As extra bonus, verify that the instance is reachable from the router::

    router01:~$ ping6 -c3  2001:db8:1234:1:f816:3eff:fecd:6bf4
    PING 2001:db8:1234:1:f816:3eff:fecd:6bf4(2001:db8:1234:1:f816:3eff:fecd:6bf4) 56 data bytes
    64 bytes from 2001:db8:1234:1:f816:3eff:fecd:6bf4: icmp_seq=1 ttl=63 time=1.80 ms
    64 bytes from 2001:db8:1234:1:f816:3eff:fecd:6bf4: icmp_seq=2 ttl=63 time=0.724 ms
    64 bytes from 2001:db8:1234:1:f816:3eff:fecd:6bf4: icmp_seq=3 ttl=63 time=1.04 ms

    --- 2001:db8:1234:1:f816:3eff:fecd:6bf4 ping statistics ---
    3 packets transmitted, 3 received, 0% packet loss, time 2000ms
    rtt min/avg/max/mdev = 0.724/1.190/1.803/0.454 ms
    router01:~$ ssh -6 2001:db8:1234:1:f816:3eff:fe58:f80a -l cirros
    cirros@2001:db8:1234:1:f816:3eff:fe58:f80a's password:
    $
