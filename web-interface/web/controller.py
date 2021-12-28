# TODO logging: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-vii-error-handling
# TODO - create logs folders runtime (delete info.txt files)
#        if not os.path.exists('logs'):
#           os.mkdir('logs')
# TODO - choose console-logging OR file-logging based on debug-modus
#        if not app.debug:
# TODO Exception handling API-calls (based on return codes op calls) 
# TODO see: https://flask.palletsprojects.com/en/1.1.x/patterns/apierrors/
# TODO Error when page (or id) not found
# TODO Error when service not found when doing a request

from flask import Flask, render_template, jsonify, request, redirect, flash
import requests
import json
import logging
from logging.handlers import RotatingFileHandler
import traceback

from config import Config
from globals import configObject

from converters import ConvertToTwoDecimals, ConvertBooleanToText

app = Flask(__name__)
logger = logging.getLogger()

'''
if not logger.handlers:
    logger.setLevel(logging.DEBUG)

    fileHandler = logging.handlers.RotatingFileHandler(
        app.config['LOG_FILE_NAME'], 'a', app.config['LOG_MAX_SIZE'], app.config['LOG_BACKUP_COUNT'])
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    logger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.DEBUG)
    consoleHandler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(consoleHandler)
'''

@app.route('/', methods=['GET'])
def index():
    try:
        apiInfo = json.loads(requests.get(configObject.ApiRootUrl).content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        apiInfo = []

    try:
        versionInfo = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetVersionInfo').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        versionInfo = []

    try:
        machineInfo = json.loads(requests.get(configObject.ApiRootUrl + '/api/GetMachineInfo').content)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        machineInfo = []

    return render_template(
        'details.html', 
        appTitle = configObject.AppTitle, 
        apiInfo = apiInfo,
        apiRootUrl = configObject.ApiRootUrl,
        versionInfo = versionInfo,
        machineInfo = machineInfo
    )

if __name__ == '__main__':
    logger.debug('App Started')
    app.run(port=5001, debug=True)  # auto-reload, only localhoast
#    app.run(host='0.0.0.0', port=5001)  # public server, reachable from remote
    logger.debug('App Stopped')

