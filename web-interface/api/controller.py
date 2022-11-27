from flask import Flask, jsonify, abort, make_response, request
import logging
import traceback
from flask_cors import CORS
import asyncio

import logic 
from globals import configObject

HTTP_OK = 200
HTTP_CREATED = 201
HTTP_BAD_REQUEST = 400
HTTP_NOT_FOUND = 404
HTTP_METHOD_NOT_ALLOWED = 405

app = Flask(__name__)
CORS(app)  # To enable http over different domains
logger = logging.getLogger()

def SetupLogger():
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        fileHandler = logging.FileHandler(configObject.LogFileName, 'a')
        fileHandler.setLevel(logging.DEBUG)
        fileHandler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        logger.addHandler(fileHandler)

        # By default, console logging is disabled once logger is activated; to still see console messages, 
        # a consoleHandler must be created
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(logging.DEBUG)
        consoleHandler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(consoleHandler)
    pass

@app.errorhandler(HTTP_NOT_FOUND)
def notFoundError(error):
    return make_response(jsonify({'message': 'Not Found: ' + request.url}), HTTP_NOT_FOUND)

@app.errorhandler(HTTP_BAD_REQUEST)
def invalidBodyError(error):
    return make_response(jsonify({'message': 'Bad request'}), HTTP_BAD_REQUEST)

@app.errorhandler(HTTP_METHOD_NOT_ALLOWED)
def methodNotAllowedError(error):
    return make_response(jsonify({'message': 'Method ' + request.method + ' is not allowed on ' + request.url}), HTTP_METHOD_NOT_ALLOWED)

def BuildResponse(statusCode, body, location):
    response = make_response( body, statusCode)
    response.headers['Location'] = location
    return response

@app.route('/', methods=['GET'])
def root():
    return BuildResponse(HTTP_OK, jsonify({"ApiName": "rpms-api",
                                           "Documentation": "api/GetApiList"}), request.url)

@app.route('/api/GetApiList', methods=['GET'])
def GetApiList():
    try:
        info = logic.GetApiList()
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)

@app.route('/api/GetVersionList', methods=['GET'])
def GetVersionList():
    try:
        info = logic.GetVersionList()
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)    

@app.route('/api/GetTranscoderSettings', methods=['GET'])
def GetTranscoderSettings():
    try:
        info = logic.GetTranscoderSettings()
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)    

@app.route('/api/GetDockerContainerList', methods=['GET'])
def GetDockerContainerList():
    try:
        info = logic.GetDockerContainerList()
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)

@app.route('/api/GetMachineInfo', methods=['GET'])
def GetMachineInfo():
    try:
        info = logic.GetMachineInfo()
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)

@app.route('/api/GetVersionInfo', methods=['GET'])
def GetVersionInfo():
    try:
        info = logic.GetVersionInfo()
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)

@app.route('/api/GetBackupInfo', methods=['GET'])
def GetBackupInfo():
    try:
        info = logic.GetBackupInfo()
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)

@app.route('/api/GetUpdateLog/<int:nrOfLines>', methods=['GET'])
def GetUpdateLog(nrOfLines):
    try:
        info = logic.GetLog('/media/usbdata/rpms/logs/update.log', nrOfLines)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)

@app.route('/api/GetApiLog/<int:nrOfLines>', methods=['GET'])
def GetApiLog(nrOfLines):
    try:
        info = logic.GetLog('/media/usbdata/rpms/logs/api.log', nrOfLines)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)

@app.route('/api/GetWebLog/<int:nrOfLines>', methods=['GET'])
def GetWebLog(nrOfLines):
    try:
        info = logic.GetLog('/media/usbdata/rpms/logs/web.log', nrOfLines)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)

@app.route('/api/GetTranscoderLog/<int:nrOfLines>', methods=['GET'])
def GetTranscoderLog(nrOfLines):
    try:
        info = logic.GetLog('/media/usbdata/rpms/logs/transcoder.log', nrOfLines)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)    

@app.route('/api/GetBackupLog/<int:nrOfLines>', methods=['GET'])
def GetBackupLog(nrOfLines):
    try:
        info = logic.GetLog('/media/usbdata/rpms/logs/backup.log', nrOfLines)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)    

@app.route('/api/GetBackupDetailsLog/<int:nrOfLines>', methods=['GET'])
def GetBackupDetailsLog(nrOfLines):
    try:
        info = logic.GetLog('/media/usbdata/rpms/logs/backup-details.log', nrOfLines)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)        

@app.route('/api/SetTranscoderSourceFolder', methods=['POST'])
def SetTranscoderSourceFolder():
    if not request.json:
        abort(HTTP_BAD_REQUEST)
    requestData = request.get_json()

    if not 'Value' in requestData:
        abort(HTTP_BAD_REQUEST)

    try:
        info = logic.SetTranscoderSetting('sourcefolder', requestData['Value'])
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)    

@app.route('/api/SetTranscoderOggFolder', methods=['POST'])
def SetTranscoderOggFolder():
    if not request.json:
        abort(HTTP_BAD_REQUEST)
    requestData = request.get_json()

    if not 'Value' in requestData:
        abort(HTTP_BAD_REQUEST)

    try:
        info = logic.SetTranscoderSetting('oggfolder', requestData['Value'])
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)    

@app.route('/api/SetTranscoderMp3Folder', methods=['POST'])
def SetTranscoderMp3Folder():
    if not request.json:
        abort(HTTP_BAD_REQUEST)
    requestData = request.get_json()

    if not 'Value' in requestData:
        abort(HTTP_BAD_REQUEST)

    try:
        info = logic.SetTranscoderSetting('mp3folder', requestData['Value'])
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)    

@app.route('/api/SetTranscoderOggQuality', methods=['POST'])
def SetTranscoderOggQuality():
    if not request.json:
        abort(HTTP_BAD_REQUEST)
    requestData = request.get_json()

    if not 'Value' in requestData:
        abort(HTTP_BAD_REQUEST)

    if not (0 <= requestData['Value'] <= 5):
        abort(HTTP_BAD_REQUEST) 

    try:
        info = logic.SetTranscoderSetting('oggquality', requestData['Value'])
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)

@app.route('/api/SetTranscoderMp3Bitrate', methods=['POST'])
def SetTranscoderMp3Bitrate():
    if not request.json:
        abort(HTTP_BAD_REQUEST)
    requestData = request.get_json()

    if not 'Value' in requestData:
        abort(HTTP_BAD_REQUEST)

    if not (requestData['Value'] in [0, 128, 256, 384]):
        abort(HTTP_BAD_REQUEST) 

    try:
        info = logic.SetTranscoderSetting('mp3bitrate', requestData['Value'])
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)    

@app.route('/api/GetMemoryResourceInfo', methods=['GET'])
def GetMemoryResourceInfo():
    try:
        info = logic.GetMemoryResourceInfo()
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)    

@app.route('/api/GetCpuResourceInfo', methods=['GET'])
def GetCpuResourceInfo():
    try:
        info = logic.GetCpuResourceInfo()
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)

@app.route('/api/GetDiskList', methods=['GET'])
def GetDiskList():
    try:
        info = logic.GetDiskList()
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)

@app.route('/api/GetServiceStatusList', methods=['GET'])
def GetServiceStatusList():
    try:
        info = logic.GetServiceStatusList()
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)    

@app.route('/api/DoRebootServer', methods=['POST'])
def DoRebootServer():
    try:
        asyncio.run(logic.DoRebootServer())
        info = { "Message": "Server is rebooting" }
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)

@app.route('/api/DoBackupServer', methods=['POST'])
def DoBackupServer():
    try:
        asyncio.run(logic.DoBackupServer())
        info = { "Message": "Backup has been started" }        
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)

@app.route('/api/DoHaltServer', methods=['POST'])
def DoHaltServer():
    try:
        asyncio.run(logic.DoHaltServer())
        info = { "Message": "Server is halting" }
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)

@app.route('/api/DoKillDocker', methods=['POST'])
def DoKillDocker():
    try:
        asyncio.run(logic.DoKillDocker())
        info = { "Message": "Docker-container will be killed" }
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)    

@app.route('/api/DoStartDocker', methods=['POST'])
def DoStartDocker():
    try:
        asyncio.run(logic.DoStartDocker())
        info = { "Message": "Docker-container(s) will be started" }
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)    

@app.route('/api/DoUpdateDocker', methods=['POST'])
def DoUpdateDocker():
    try:
        asyncio.run(logic.DoUpdateDocker())
        info = { "Message": "Docker-container(s) will be updated" }
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)        

@app.route('/api/DoUpdateServer', methods=['POST'])
def DoUpdateServer():
    try:
        asyncio.run(logic.DoUpdateServer())
        info = { "Message": "Server is updating" }        
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)

@app.route('/api/GetLmsServerInfo', methods=['GET'])
def GetLmsServerInfo():
    try:
        info = logic.GetLmsServerInfo()
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    return BuildResponse(HTTP_OK, jsonify(info), request.url)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Controller for RP Music Server API')
    parser.add_argument('--logfile', type=str,  help="file where log is stored", nargs=1) 
    parser.add_argument('-p', '--production', help="start a production server", action="store_true")        

    args = parser.parse_args()

    configObject.Debug = not args.production

    if (args.logfile != None) and (args.logfile[0] != ''):
        configObject.LogFileName = args.logfile[0]

    SetupLogger()       
    logger.info('Log to: ' + configObject.LogFileName)

    if configObject.Debug:
        logger.info('API started - debug')
        app.run(port=5000, debug=True)  # auto-reload on file change, only localhost
    else:
        logger.info('API started - production')
        app.run(host='0.0.0.0', port=5000)  # public server, reachable from remote
    logger.info('API stopped')
