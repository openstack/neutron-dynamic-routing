To generate the sample neutron-dynamic-routing configuration files and the
sample policy file, run the following commands respectively from the top level
of the neutron-dynamic-routing directory:

  tox -e genconfig
  tox -e genpolicy

If a 'tox' environment is unavailable, then you can run the following commands
instead to generate the configuration files and the policy file:

  ./tools/generate_config_file_samples.sh
  oslopolicy-sample-generator --config-file=etc/oslo-policy-generator/policy.conf
