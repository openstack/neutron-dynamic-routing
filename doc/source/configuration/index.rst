===================
Configuration Guide
===================

Configuration
-------------

This section provides a list of all possible options for each
configuration file.

neutron-dynamic-routing uses the following configuration files for its
various services.

.. toctree::
   :maxdepth: 1

   bgp_dragent

The following are sample configuration files for neutron-dynamic-routing.
These are generated from code and reflect the current state of code
in the neutron-dynamic-routing repository.

.. toctree::
   :glob:
   :maxdepth: 1

   samples/*

Policy
------

neutron-dynamic-routing, like most OpenStack projects, uses a policy language
to restrict permissions on REST API actions.

.. toctree::
   :maxdepth: 1

   Policy Reference <policy>
   Sample Policy File <policy-sample>
