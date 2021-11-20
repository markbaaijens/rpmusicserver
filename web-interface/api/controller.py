from flask import Flask, jsonify, abort, make_response, request
import logging
from logging.handlers import RotatingFileHandler
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

        fileHandler = logging.handlers.RotatingFileHandler(
            configObject.LogFileName, 
            'a', 
            configObject.LogMaxSize, 
            configObject.LogBackupCount)
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

# GET /
# curl -i http://localhost:5000
@app.route('/', methods=['GET'])
def root():
    return BuildResponse(HTTP_OK, jsonify({'ApiName': 'rpms-api'}), request.url)

# GET /api/GetMachineInfo
# curl -i http://localhost:5000/GetMachineInfo
@app.route('/api/GetMachineInfo', methods=['GET'])
def GetMachineInfo():
    try:
        info = logic.GetMachineInfo()
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)

# GET /api/GetVersionInfo
# curl -i http://localhost:5000/GetVersionInfo
@app.route('/api/GetVersionInfo', methods=['GET'])
def GetVersionInfo():
    try:
        info = logic.GetVersionInfo()
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)

# GET /api/GetUpdateLog
# curl -i http://localhost:5000/GetUpdateLog
@app.route('/api/GetUpdateLog', methods=['GET'])
def GetUpdateLog():
    try:
        info = logic.GetUpdateLog()
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(info), request.url)


'''
# TODO Method logic.GetServerInfo() is not working 
# GET /api/ServerInfo
# curl -i http://localhost:5000/ServerInfo
@app.route('/api/ServerInfo', methods=['GET'])
def GetServerInfo():
    try:
        info = logic.GetServerInfo()
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    return BuildResponse(HTTP_OK, jsonify(info), request.url)
'''

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
