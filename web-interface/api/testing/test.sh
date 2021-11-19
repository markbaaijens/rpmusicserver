#!/bin/bash
# Note: all tests are idempotent

curl_output_file="/tmp/curl-output.txt"

given_an_api_when_called_root_then_correct_output_returned () {
    echo "* ${FUNCNAME[0]}"
    $(curl -s localhost:5000 > $curl_output_file 2>&1)
    if [ "$(cat $curl_output_file | grep 'rpms')" ]; then echo "OK"; else echo "Fail"; fi
}

given_an_api_when_called_root_then_correct_output_returned

