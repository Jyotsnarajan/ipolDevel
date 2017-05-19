#!/usr/bin/env bash

host=$(hostname)
today=$(date)

# Git pull
git pull


function send_email () {
    msg="$*"
    sendTo=$(cat /home/ipol/ipolDevel/ci_tests/send_to.txt)
    echo -e "This is the ${host} machine. The tests failed on ${today}:\n${msg}" | mutt -s "[${host}] Test failed" -- ${sendTo}
}

# Executes all the tests for integration and production
if [ $host == "integration.ipol.im" ] || [ $host == "ipol_core" ];then
    out=$(python /home/ipol/ipolDevel/ci_tests/all.py)
    if [ $? -ne 0 ];then
        send_email "$out"
    fi
fi

