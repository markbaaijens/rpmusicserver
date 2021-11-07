import subprocess
import requests

def ExecuteBashCommand(bashCommand):
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    return output.decode("utf-8").strip('\n')

def GetMachineInfo():
    hostName = ExecuteBashCommand("hostname")
    ipAddress = ExecuteBashCommand("hostname -I").split()[0]
    return {'HostName': hostName, 'IpAddress': ipAddress}

def GetServerInfo():
    # Todo 'msi' => 'localhost'
    url = "http://msi:9000/jsonrpc.js"
    payload = "{\"method\": \"slim.request\", \"params\": [\"-\", [\"serverstatus\",\"0\",\"100\"]]}\n"
    headers = {'Content-Type': 'application/json'}

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response)

    return(response)
