LIBDIR=$NEUTRON_DYNAMIC_ROUTING_DIR/devstack/lib

source $LIBDIR/dr

if [[ "$1" == "stack" ]]; then
    case "$2" in
        install)
            echo_summary "Installing neutron-dynamic-routing"
            dr_install
            ;;
        post-config)
            echo_summary "Configuring neutron-dynamic-routing"
            dr_post_configure
            ;;
        extra)
            echo_summary "Launching neutron-dynamic-routing agent"
            start_dr_agent
            ;;
    esac
elif [[ "$1" == "unstack" ]]; then
    echo_summary "Uninstalling neutron-dynamic-routing"
    stop_dr_agent
fi
