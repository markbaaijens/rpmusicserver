from flask import Flask, jsonify, abort, make_response, request
import logging
from logging import FileHandler
import traceback
from flask_cors import CORS
from werkzeug.wrappers import response

import logic 
from config import Config
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
    return BuildResponse(HTTP_OK, jsonify({"ApiName": "rpms-api"},
                                          {"Documentation": "api/GetApiList"}), request.url)

@app.route('/api/GetApiList', methods=['GET'])
def GetApiList():
    try:
        info = logic.GetApiList()
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

@app.route('/api/GetTranscoderLog/<int:nrOfLines>', methods=['GET'])
def GetTranscoderLog(nrOfLines):
    try:
        info = logic.GetLog('/media/usbdata/rpms/logs/transcoder.log', nrOfLines)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)    

@app.route('/api/SetTranscoderSettingSourceFolder', methods=['POST'])
def SetTranscoderSettingSourceFolder():
    if not request.json:
        abort(HTTP_BAD_REQUEST)
    requestData = request.get_json()

    settingName = 'sourcefolder'
    if not settingName in requestData:
        abort(HTTP_BAD_REQUEST)

    try:
        info = logic.SetTranscoderSetting(requestData, settingName)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)    

@app.route('/api/SetTranscoderSettingOggFolder', methods=['POST'])
def SetTranscoderSettingOggFolder():
    if not request.json:
        abort(HTTP_BAD_REQUEST)
    requestData = request.get_json()

    settingName = 'oggfolder'
    if not settingName in requestData:
        abort(HTTP_BAD_REQUEST)

    try:
        info = logic.SetTranscoderSetting(requestData, settingName)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)    

@app.route('/api/SetTranscoderSettingMp3Folder', methods=['POST'])
def SetTranscoderSettingMp3Folder():
    if not request.json:
        abort(HTTP_BAD_REQUEST)
    requestData = request.get_json()

    settingName = 'mp3folder'
    if not settingName in requestData:
        abort(HTTP_BAD_REQUEST)

    try:
        info = logic.SetTranscoderSetting(requestData, settingName)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)    

@app.route('/api/SetTranscoderSettingOggQuality', methods=['POST'])
def SetTranscoderSettingOggQuality():
    if not request.json:
        abort(HTTP_BAD_REQUEST)
    requestData = request.get_json()

    settingName = 'oggquality'
    if not settingName in requestData:
        abort(HTTP_BAD_REQUEST)

    if not (1 <= requestData[settingName] <= 5):
        abort(HTTP_BAD_REQUEST) 

    try:
        info = logic.SetTranscoderSetting(requestData, settingName)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)

@app.route('/api/SetTranscoderSettingMp3BitRate', methods=['POST'])
def SetTranscoderSettingMp3BitRate():
    if not request.json:
        abort(HTTP_BAD_REQUEST)
    requestData = request.get_json()

    settingName = 'mp3bitrate'
    if not settingName in requestData:
        abort(HTTP_BAD_REQUEST)

    if not (requestData[settingName] in [128, 256, 384]):
        abort(HTTP_BAD_REQUEST) 

    try:
        info = logic.SetTranscoderSetting(requestData, settingName)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)    

@app.route('/api/GetResourceInfo', methods=['GET'])
def GetResourceInfo():
    try:
        info = logic.GetResourceInfo()
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

@app.route('/api/DoRebootServer', methods=['POST'])
def DoRebootServer():
    try:
        info = logic.DoRebootServer()
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)

@app.route('/api/DoHaltServer', methods=['POST'])
def DoHaltServer():
    try:
        info = logic.DoHaltServer()
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)

@app.route('/api/DoUpdateServer', methods=['POST'])
def DoUpdateServer():
    try:
        info = logic.DoUpdateServer()
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
