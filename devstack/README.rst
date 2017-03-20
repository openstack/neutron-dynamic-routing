======================
 Enabling in Devstack
======================

1. Download devstack::

     git clone https://git.openstack.org/openstack-dev/devstack.git

2. Add neutron-dynamic-routing to devstack.  The minimal set of critical local.conf
   additions are following::

     cd devstack
     cat << EOF >> local.conf
     > enable_plugin neutron-dynamic-routing https://git.openstack.org/openstack/neutron-dynamic-routing
     > EOF

3. run devstack::

     ./stack.sh

Notes:

1. In default case, neutron-dynamic-routing is installed in allinone mode.
   In multiple nodes environment, for controller node::
     cd devstack
     cat << EOF >> local.conf
     > enable_plugin neutron-dynamic-routing https://git.openstack.org/openstack/neutron-dynamic-routing
     > DR_MODE=dr_plugin
     > EOF

   For the nodes where you want to run dr-agent::
     cd devstack
     cat << EOF >> local.conf
     > enable_plugin neutron-dynamic-routing https://git.openstack.org/openstack/neutron-dynamic-routing
     > DR_MODE=dr_agent
     > EOF

2. In default case, protocol BGP is enabled for neutron-dynamic-routing.
   You can change "DR_SUPPORTED_PROTOCOLS" in "devstack/settings" to protocols wanted.

