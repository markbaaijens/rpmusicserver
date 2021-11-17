import subprocess
import requests
import json

def ExecuteBashCommand(bashCommand):
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    return output.decode("utf-8").strip('\n')

def GetMachineInfo():
    hostName = ExecuteBashCommand("hostname")
    ipAddress = ExecuteBashCommand("hostname -I").split()[0]
    return {'HostName': hostName, 'IpAddress': ipAddress}


'''
LMS API-reference: http://msi:9000/html/docs/cli-api.html

Examples:

# [player] Play
curl --location --request POST 'http://msi:9000/jsonrpc.js' \
--header 'Content-Type: application/json' \
--data-raw '{"method": "slim.request", "params": ["b8:27:eb:79:f5:47", ["play"]]}'

# [player] Pause/unpause
curl --location --request POST 'http://msi:9000/jsonrpc.js' \
--header 'Content-Type: application/json' \
--data-raw '{"method": "slim.request", "params": ["b8:27:eb:79:f5:47", ["pause"]]}'

# [player] Player status
curl --location --request POST 'http://msi:9000/jsonrpc.js' \
--header 'Content-Type: application/json' \
--data-raw '{"method": "slim.request", "params": ["b8:27:eb:79:f5:47", ["status","-"]]}'

# [player] Get title now playing
curl --location --request POST 'http://msi:9000/jsonrpc.js' \
--header 'Content-Type: application/json' \
--data-raw '{"method": "slim.request", "params": ["b8:27:eb:79:f5:47", ["playlist","title","?"]]}

# [server] Get song details (song-id from status, first in playlist); bitrate/samplesize
curl --location --request POST 'http://msi:9000/jsonrpc.js' \
--header 'Content-Type: application/json' \
--data-raw '{"method": "slim.request", "params": ["-", ["songinfo","0","100", "track_id:3903170"]]}'

# [server] Get server status; playerlist, library-statistics
curl --location --request POST 'http://msi:9000/jsonrpc.js' \
--header 'Content-Type: application/json' \
--data-raw '{"method": "slim.request", "params": ["-", ["serverstatus","0","100"]]}
'''

def GetServerInfo():  # Sample function from generated code in Postman; may not function
    # Todo 'msi' => 'localhost'
    # Todo '9000' => '9002'    
    url = "http://msi:9000/jsonrpc.js"
    payload = "{\"method\": \"slim.request\", \"params\": [\"-\", [\"serverstatus\",\"0\",\"100\"]]}\n"
    headers = {'Content-Type': 'application/json'}

    # TODO This call does npt seem to return the result (body)
    response = requests.request("POST", url, headers=headers, data=payload)

    # TODO This call should return the resukt
#    response = json.loads(requests.get(app.config['API_ROOT_URL'] + '/books').content)

    print(response)

    return(response)