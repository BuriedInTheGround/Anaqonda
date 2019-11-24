#!/bin/sh

##### Functions

usage() {
    echo "Usage: ./run.sh [options]"
    echo "  -e --evil       run Charile in evil mode"
    echo "  -h --help       shows this help"
}


##### Main

run_in_evil_mode=false

while [ "$1" != "" ] ; do
    case $1 in
        -e | --evil )   shift
                        run_in_evil_mode=true
                        ;;
        -h | --help )   usage
                        exit
                        ;;
    esac
done

echo "Settings up simulaqron..."
simulaqron start -f
simulaqron reset -f
simulaqron stop
simulaqron set max-qubits 65536
simulaqron start -f
echo "Done. Ready"

if $run_in_evil_mode ; then
    python3 node_evil_charlie.py &
else
    python3 node_charlie.py &
fi

python3 node_alice.py &
python3 node_bob.py &