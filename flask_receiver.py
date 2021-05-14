#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2021 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

__author__ = "Gabriel Zapodeanu TME, ENB"
__email__ = "gzapodea@cisco.com"
__version__ = "0.1.0"
__copyright__ = "Copyright (c) 2021 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"


import os
import time
import requests
import urllib3

from flask import Flask, request
from flask_basicauth import BasicAuth
from requests.auth import HTTPBasicAuth  # for Basic Auth
from urllib3.exceptions import InsecureRequestWarning  # for insecure https warnings
from dotenv import load_dotenv


urllib3.disable_warnings(InsecureRequestWarning)  # disable insecure https warnings

load_dotenv('environment.env')

WEBHOOK_USERNAME = os.getenv('WEBHOOK_USERNAME')
WEBHOOK_PASSWORD = os.getenv('WEBHOOK_PASSWORD')

DNAC_URL = os.getenv('DNAC_URL')
DNAC_USER = os.getenv('DNAC_USER')
DNAC_PASS = os.getenv('DNAC_PASS')

os.environ['TZ'] = 'America/Los_Angeles'  # define the timezone for PST
time.tzset()  # adjust the timezone, more info https://help.pythonanywhere.com/pages/SettingTheTimezone/


app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = WEBHOOK_USERNAME
app.config['BASIC_AUTH_PASSWORD'] = WEBHOOK_PASSWORD
# app.config['BASIC_AUTH_FORCE'] = True  # enable if all API endpoints support HTTP basic auth

basic_auth = BasicAuth(app)


def get_dnac_jwt_token(dnac_auth):
    """
    Create the authorization token required to access DNA C
    Call to Cisco DNA Center - /api/system/v1/auth/login
    :param dnac_auth - Cisco DNA Center Basic Auth string
    :return: Cisco DNA Center JWT token
    """
    url = DNAC_URL + '/dna/system/api/v1/auth/token'
    header = {'content-type': 'application/json'}
    response = requests.post(url, auth=dnac_auth, headers=header, verify=False)
    dnac_jwt_token = response.json()['Token']
    return dnac_jwt_token


@app.route('/')  # create a decorator for testing the Flask framework
@basic_auth.required
def index():
    return '<h1>Flask Receiver App is Up!</h1>', 200


@app.route('/dnacenter_report', methods=['POST'])  # API endpoint to receive the client detail report
@basic_auth.required
def client_report():
    if request.method == 'POST':
        print('Webhook Received')
        webhook_json = request.json

        # print the received notification
        print('Payload: ')
        print(webhook_json, '\n')

        # parse the report status and event type
        event_type = webhook_json['Event Type']
        event_status = webhook_json['Event Details']['status']

        if event_type == 'APP' and event_status == 'Success':

            # get the Cisco DNA Center Auth token
            dnac_auth = get_dnac_jwt_token(DNAC_AUTH)

            report_url = webhook_json['Cisco DNA Center Event Context link. **This link is active only in the context of Cisco DNA Center. You must have necessary permissions to login']

            # parse the "data-set-id" and "execution-id" from the provided URL
            report_list = report_url.split('&')

            for item in report_list:
                if 'data-set-id' in item:
                    data_set_id = item.replace('data-set-id=', '')
                elif 'execution-id' in item:
                    execution_id = item.replace('execution-id=', '')

            # call the API to download the report file
            report_file_url = DNAC_URL + '/api/dnacaap/v1/daas/core/content/data-set/' + data_set_id + '/' + execution_id
            header = {'Content-Type': 'application/json', 'X-Auth-Token': dnac_auth}
            response = requests.get(report_file_url, headers=header, verify=False)

            # save the report to a file
            with open('client_report.json', 'wb') as file:
                file.write(response.content)
                print('Client report file saved')

        return 'Client Detail Report Data Received', 202
    else:
        return 'Method not supported', 405


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, ssl_context='adhoc')


