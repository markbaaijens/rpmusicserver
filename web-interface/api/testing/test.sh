#!/bin/bash
# Note: all tests are idempotent

curl_output_file="/tmp/curl-output.txt"

call_api () {
    $(curl -s $1 > $curl_output_file 2>&1)
}

given_an_api_when_called_root_then_correct_output_returned () {
    func_name="* ${FUNCNAME[0]}"
    call_api "localhost:5000"
    if [ "$(cat /tmp/curl-output.txt | jq .ApiName | grep 'rpms')" ]; then echo "$func_name => OK"; else echo "$func_name => Fail"; fi
}

given_an_api_when_called_machine_info_then_ipadress_returned () {
    func_name="* ${FUNCNAME[0]}"
    test_value=$(hostname -I | awk '{print $1}')
    call_api "localhost:5000/api/GetMachineInfo"
    if [ "$(cat /tmp/curl-output.txt | jq .IpAddress | grep $test_value)" ]; then echo "$func_name => OK"; else echo "$func_name => Fail"; fi
}

given_an_api_when_called_machine_info_then_hostname_returned () {
    func_name="* ${FUNCNAME[0]}"
    test_value=$(hostname)
    call_api "localhost:5000/api/GetMachineInfo"
    if [ "$(cat /tmp/curl-output.txt | jq .HostName | grep $test_value)" ]; then echo "$func_name => OK"; else echo "$func_name => Fail"; fi
}

given_an_api_when_called_machine_info_then_os_codename_returned () {
    func_name="* ${FUNCNAME[0]}"
    test_value=$(lsb_release -c | awk '{print $2}')
    call_api "localhost:5000/api/GetMachineInfo"
    if [ "$(cat /tmp/curl-output.txt | jq .OsCodeName | grep $test_value)" ]; then echo "$func_name => OK"; else echo "$func_name => Fail"; fi
}

given_an_api_when_called_version_info_then_current_version_returned () {
    func_name="* ${FUNCNAME[0]}"
    call_api "localhost:5000/api/GetVersionInfo"
    if [ "$(cat /tmp/curl-output.txt | jq .CurrentVersion)" ]; then echo "$func_name => OK"; else echo "$func_name => Fail"; fi
}

given_an_api_when_called_version_info_then_update_timestamp_returned () {
    func_name="* ${FUNCNAME[0]}"
    call_api "localhost:5000/api/GetVersionInfo"
    if [ "$(cat /tmp/curl-output.txt | jq .LastUpdateTimeStamp)" ]; then echo "$func_name => OK"; else echo "$func_name => Fail"; fi
}

given_an_api_when_called_update_log_then_update_log_returned () {
    func_name="* ${FUNCNAME[0]}"
    call_api "localhost:5000/api/GetUpdateLog/10"
    if [ "$(cat /tmp/curl-output.txt | jq .LogLines)" ]; then echo "$func_name => OK"; else echo "$func_name => Fail"; fi
}

given_an_api_when_called_api_log_then_api_log_returned () {
    func_name="* ${FUNCNAME[0]}"
    call_api "localhost:5000/api/GetApiLog/10"
    if [ "$(cat /tmp/curl-output.txt | jq .LogLines)" ]; then echo "$func_name => OK"; else echo "$func_name => Fail"; fi
}

given_an_api_when_called_root_then_correct_output_returned
echo 
given_an_api_when_called_machine_info_then_ipadress_returned
given_an_api_when_called_machine_info_then_hostname_returned
given_an_api_when_called_machine_info_then_os_codename_returned
echo 
given_an_api_when_called_version_info_then_current_version_returned
given_an_api_when_called_version_info_then_update_timestamp_returned
echo 
given_an_api_when_called_update_log_then_update_log_returned
given_an_api_when_called_api_log_then_api_log_returned

