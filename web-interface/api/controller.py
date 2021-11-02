from flask import Flask, jsonify, abort, make_response, request
import logging
from logging.handlers import RotatingFileHandler
import traceback
from flask_cors import CORS

import logic 
from config import Config
import globals

HTTP_OK = 200
HTTP_CREATED = 201
HTTP_BAD_REQUEST = 400
HTTP_NOT_FOUND = 404
HTTP_METHOD_NOT_ALLOWED = 405

app = Flask(__name__)
CORS(app)  # To enable http over different domains
app.config.from_object(Config)

logger = logging.getLogger()
if not logger.handlers:
    logger.setLevel(logging.DEBUG)

    fileHandler = logging.handlers.RotatingFileHandler(
        app.config['LOG_FILE_NAME'], 'a', app.config['LOG_MAX_SIZE'], app.config['LOG_BACKUP_COUNT'])
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    logger.addHandler(fileHandler)

    # By default, console logging is disabled once logger is activated; to still see console messages, 
    # a consoleHandler must be created
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.DEBUG)
    consoleHandler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(consoleHandler)

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

# GET /api
# curl -i http://localhost:5000/api
@app.route('/api', methods=['GET'])
def root():
    return BuildResponse(HTTP_OK, jsonify({'name': globals.apiName}), request.url)

# GET /api/MachineInfo
# curl -i http://localhost:5000/MachineInfo
@app.route('/api/MachineInfo', methods=['GET'])
def GetMachineInfo():
    try:
        machineInfo = logic.GetMachineInfo()
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        return BuildResponse(HTTP_BAD_REQUEST, jsonify({'message': str(e)}), request.url)
    
    return BuildResponse(HTTP_OK, jsonify(machineInfo), request.url)

if __name__ == '__main__':
    import argparse
    global configDir
    parser = argparse.ArgumentParser(description='Controller for RP Music Server API')
    parser.add_argument('--config', type=str,  help="folder where settings = api-settings.json are stored",  nargs=1) 
    args = parser.parse_args()

    if (args.config != None) and (args.config[0] != ''):
        configDir = args.config[0]
    else:
        configDir = '../../files/config'

    logger.debug('API started')
    app.run(port=5000, debug=True)  # auto-reload, only localhoast
#    app.run(host='0.0.0.0', port=5000)  # public server, reachable from remote
    logger.debug('API stopped')


