#!/bin/bash
# Note: all tests are idempotent

curl_output_file="/tmp/curl-output.txt"

call_api () {
    $(curl -s $1 > $curl_output_file 2>&1)
}

given_an_api_when_called_root_then_correct_output_returned () {
    echo "* ${FUNCNAME[0]}"
    call_api "localhost:5000"
    if [ "$(cat /tmp/curl-output.txt | jq .name | grep 'rpms')" ]; then echo "OK"; else echo "Fail"; fi
}

given_an_api_when_called_root_then_correct_output_returned
