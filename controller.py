# -*- coding: utf-8 -*-
"""
@author: sergii shapovalenko
"""
from flask import Flask, jsonify, request
from concurrent.futures import ThreadPoolExecutor
import kubbuilder_service
import requests
from coralogger import get_default_logger
import uuid
import traceback
import json


app = Flask(__name__)

log = get_default_logger()

executor = ThreadPoolExecutor(2)


@app.route("/", methods=["POST"])
def index():
    try:
        contents = request.get_json()
        contents['request_id'] = str(uuid.uuid4())
        log.debug("index request: %s" % contents)

        executor.submit(background, contents)

        response = {'success': True}
        log.debug("index response for: %s, status code: %s, response: %s", contents['request_id'], 200, response)
        return jsonify(response), 200
    except:
        error_json = {'error': traceback.format_exc()}
        log.error("index response for: %s, status code: %s, response: %s", contents['request_id'], 500, str(error_json))
        return jsonify(error_json), 500


def background(contents):
    try:
        log.debug("Start building! %s", contents['request_id'])
        response_data = json.dumps(kubbuilder_service.run(contents['executor_location'], contents['host_path']))
        log.debug("Sending: request %s, %s to: %s", contents['request_id'], response_data, contents['callback_url'])

        response = requests.post(
            url=contents['callback_url'],
            json=response_data)

        log.debug("request_id: %s, Status code: %s, response: %s", contents['request_id'], response.status_code, response.text)
        log.debug("request_id: %s completed successfully", contents['request_id'])
    except:
        log.error("background error for: %s, error_json: %s", contents['request_id'], str({'error': traceback.format_exc()}))


@app.route("/variables", methods=["POST"])
def variables():
    try:
        log.debug("Start building!")
        response = kubbuilder_service.run_secret(request.get_json())
        return jsonify(response), 200

    except:
        error_json = {'error': traceback.format_exc()}
        log.error("Status code: %s, response: %s", 500, error_json)
        return error_json, 500


@app.route("/healthcheck", methods=["GET"])
def healthcheck():
    return "ok"
