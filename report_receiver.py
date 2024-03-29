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
import json

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

DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)


def pprint(json_data):
    """
    Pretty print JSON formatted data
    :param json_data: data to pretty print
    :return None
    """
    print(json.dumps(json_data, indent=4, separators=(' , ', ' : ')))


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


def get_report_file(report_id, execution_id, dnac_auth):
    """
    This function will return the report content specified by the {report_id} and {execution_id}
    :param report_id: report id
    :param execution_id: execution id
    :param dnac_auth: Cisco DNA Center Auth
    :return: report data
    """
    url = DNAC_URL + '/dna/intent/api/v1/data/reports' + report_id + '/executions/' + execution_id
    header = {'Content-Type': 'application/json', 'X-Auth-Token': dnac_auth}
    response = requests.get(url, headers=header, verify=False)
    report = response.json()
    return report


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

            report_url = webhook_json['Cisco DNA Center Event Context link. **This link is active only in the context of Cisco DNA Center. You must have necessary permissions to login']

            # parse the "data-set-id" and "execution-id" from the provided URL
            report_list = report_url.split('&')

            for item in report_list:
                if 'data-set-id' in item:
                    report_id = item.replace('data-set-id=', '')
                elif 'execution-id' in item:
                    execution_id = item.replace('execution-id=', '')

            dnac_auth = get_dnac_jwt_token(DNAC_AUTH)

            print('\nReport Id: ', report_id, '\nExecution Id: ', execution_id)

            # call the API to download the report file
            report_content = get_report_file(report_id, execution_id, dnac_auth)
            print('\nReport content:\n', report_content)

            # save the report to a file
            try:
                report = json.dumps(report_content)

                # verify if report file exists, if the "error" key exists
                if 'error' in report_content:
                    raise ValueError('Report error received')
                with open('report.json', 'w') as file:
                    file.write(report)
                    print('Client report file saved')
                    file.close()
            except:
                report_error = report_content['error']
                print('Client report not saved, error received: ', report_error)

        return 'Client Detail Report Data Received', 202
    else:
        return 'Method not supported', 405


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, ssl_context='adhoc')
