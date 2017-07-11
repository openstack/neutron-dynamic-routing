#!/usr/bin/env bash

set -xe

PROJECT_NAME=neutron-dynamic-routing
GATE_DEST=$BASE/new
NEUTRON_PATH=$GATE_DEST/neutron
DR_PATH=$GATE_DEST/$PROJECT_NAME
DEVSTACK_PATH=$GATE_DEST/devstack
APPARMOR_PROFILE_PATH=/etc/apparmor.d
QUAGGA_CONFIG_PATH=/tmp/ctn_docker

VENV=${1:-"dsvm-functional"}

# NOTE(kakuma)
# Check apparmor to avoid the following error for docker operation.
#   "oci runtime error: apparmor failed to apply profile: no such file or directory"
# This is a temporary solution. This needs to be fixed in a better way.
function check_apparmor_for_docker {
    if [[ -d $APPARMOR_PROFILE_PATH ]]
    then
        if [[ ! -f $APPARMOR_PROFILE_PATH/docker ]]
        then
cat << EOF > /tmp/docker
#include <tunables/global>


profile docker-default flags=(attach_disconnected,mediate_deleted) {

  #include <abstractions/base>


  network,
  capability,
  file,
  umount,

  deny @{PROC}/* w,   # deny write for all files directly in /proc (not in a subdir)
  # deny write to files not in /proc/<number>/** or /proc/sys/**
  deny @{PROC}/{[^1-9],[^1-9][^0-9],[^1-9s][^0-9y][^0-9s],[^1-9][^0-9][^0-9][^0-9]*}/** w,
  deny @{PROC}/sys/[^k]** w,  # deny /proc/sys except /proc/sys/k* (effectively /proc/sys/kernel)
  deny @{PROC}/sys/kernel/{?,??,[^s][^h][^m]**} w,  # deny everything except shm* in /proc/sys/kernel/
  deny @{PROC}/sysrq-trigger rwklx,
  deny @{PROC}/mem rwklx,
  deny @{PROC}/kmem rwklx,
  deny @{PROC}/kcore rwklx,

  deny mount,

  deny /sys/[^f]*/** wklx,
  deny /sys/f[^s]*/** wklx,
  deny /sys/fs/[^c]*/** wklx,
  deny /sys/fs/c[^g]*/** wklx,
  deny /sys/fs/cg[^r]*/** wklx,
  deny /sys/firmware/efi/efivars/** rwklx,
  deny /sys/kernel/security/** rwklx,


  # suppress ptrace denials when using 'docker ps' or using 'ps' inside a container
  ptrace (trace,read) peer=docker-default,

}
EOF
            chmod 0644 /tmp/docker
            sudo chown root:root /tmp/docker
            sudo mv /tmp/docker $APPARMOR_PROFILE_PATH/docker
            sudo service apparmor restart
            sudo service docker restart
        fi
    fi
}

function configure_docker_test_env {
    local docker_pkg

    sudo bash -c 'echo "tempest ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers'
    sudo apt-get update
    if apt-cache search docker-engine | grep docker-engine; then
        docker_pkg=docker-engine
    else
        docker_pkg=docker.io
    fi
    sudo apt-get install -y $docker_pkg
}

function do_devstack_gate {
    local gate_retval
    set +e
    $GATE_DEST/devstack-gate/devstack-vm-gate.sh
    gate_retval=$?
    if [[ -d $QUAGGA_CONFIG_PATH ]]
    then
        sudo cp -r $QUAGGA_CONFIG_PATH /opt/stack/logs/bgp_dr_docker
    fi
    set -e
    return $gate_retval
}

if [[ "$VENV" == dsvm-functional* ]]
then
    # The following need to be set before sourcing
    # configure_for_func_testing.
    GATE_STACK_USER=stack
    IS_GATE=True

    source $DEVSTACK_PATH/functions
    source $NEUTRON_PATH/devstack/lib/ovs
    source $NEUTRON_PATH/tools/configure_for_func_testing.sh

    enable_plugin $PROJECT_NAME https://git.openstack.org/openstack/$PROJECT_NAME

    # Make the workspace owned by the stack user
    sudo chown -R $STACK_USER:$STACK_USER $BASE

elif [[ "$VENV" == dsvm-api* ]]
then
    export DEVSTACK_LOCAL_CONFIG+=$'\n'"NETWORK_API_EXTENSIONS=all"
    $GATE_DEST/devstack-gate/devstack-vm-gate.sh

elif [[ "$VENV" == dsvm-scenario* ]]
then
    sudo apt-get update
    sudo apt-get install -y --reinstall apparmor
    configure_docker_test_env
    check_apparmor_for_docker
    DEVSTACK_LOCAL_CONFIG+=$'\n'"NETWORK_API_EXTENSIONS=all"
    export DEVSTACK_LOCAL_CONFIG+=$'\n'"BGP_SCHEDULER_DRIVER=neutron_dynamic_routing.services.bgp.scheduler.bgp_dragent_scheduler.ChanceScheduler"

    do_devstack_gate

else
    echo "Unrecognized environment $VENV".
    exit 1
fi
