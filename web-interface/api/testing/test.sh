#!/bin/bash
# Note: all tests are idempotent

given_a_api_when_called_root_then_correct_output_returned () {
    output=$(curl --no-progress-meter localhost:5000)
    if echo $output | grep "rpms" ; then echo "OK"; else echo "Fail"; fi
}

given_a_api_when_called_root_then_correct_output_returned

