#!/usr/bin/env bash

set -xe

PROJECT_NAME=neutron-dynamic-routing
GATE_DEST=$BASE/new
NEUTRON_PATH=$GATE_DEST/neutron
DR_PATH=$GATE_DEST/$PROJECT_NAME
SCRIPTS_PATH="/usr/os-testr-env/bin/"

VENV=${1:-"dsvm-functional"}

function generate_testr_results {
    # Give job user rights to access tox logs
    sudo -H -u $OWNER chmod o+rw .
    sudo -H -u $OWNER chmod o+rw -R .stestr
    if [ -f ".stestr/0" ] ; then
        .tox/$VENV/bin/subunit-1to2 < .stestr/0 > ./stestr.subunit
        $SCRIPTS_PATH/subunit2html ./stestr.subunit testr_results.html
        gzip -9 ./stestr.subunit
        gzip -9 ./testr_results.html
        sudo mv ./*.gz /opt/stack/logs/
    fi
}

if [[ "$VENV" == dsvm-functional* ]]
then
    OWNER=stack
    SUDO_ENV=

    # Set owner permissions according to job's requirements.
    sudo chown -R $OWNER:stack $NEUTRON_PATH
    sudo chown -R $OWNER:stack $DR_PATH
    cd $DR_PATH

    # Run tests
    echo "Running $PROJECT_NAME $VENV test suite"
    set +e
    sudo -H -u $OWNER $SUDO_ENV tox -e $VENV
    testr_exit_code=$?
    set -e

    # Collect and parse results
    generate_testr_results
    exit $testr_exit_code
fi
