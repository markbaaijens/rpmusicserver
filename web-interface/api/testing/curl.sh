#!/bin/bash
#
# Usage:
#  chown +x curl.sh
#  ./curl.sh
#  (or)
#  ./curl.sh | grep -i "error"
#

debug=0  # Set to 1 to show curl-statements

result=""

run_test() {
    result=$($2 -s | grep "$3") 
    if [ "$result" != "" ]
    then
        echo "[$1] returns [$3] => OK"
    else
        echo "[$1] returns [$3] => Error"
    fi
    if [ "$debug" == 1 ]
    then
        echo "$2"
        echo
    fi
}

# GET /
title="GET /api"
test_cmd="curl http://localhost:5000/api"
test_value="rpmusicserver-api"
run_test "$title" "$test_cmd" "$test_value"

test_cmd="curl -i http://localhost:5000/api"
test_value="HTTP/1.0 200 OK"
run_test "$title" "$test_cmd" "$test_value"

