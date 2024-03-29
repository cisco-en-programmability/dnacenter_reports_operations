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

import datetime
import logging
import os
import time
import urllib3
import json
import requests

from datetime import datetime
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth  # for Basic Auth
from urllib3.exceptions import InsecureRequestWarning  # for insecure https warnings

load_dotenv('environment.env')

DNAC_URL = os.getenv('DNAC_URL')
DNAC_USER = os.getenv('DNAC_USER')
DNAC_PASS = os.getenv('DNAC_PASS')

os.environ['TZ'] = 'America/Los_Angeles'  # define the timezone for PST
time.tzset()  # adjust the timezone, more info https://help.pythonanywhere.com/pages/SettingTheTimezone/

urllib3.disable_warnings(InsecureRequestWarning)  # disable insecure https warnings


DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)

REPORT_CATEGORY = 'Client'
VIEW_NAME = 'Client Detail'
WEBHOOK_NAME = 'LinuxMint_Report'
REPORT_NAME = 'Client Report Detail 24 h'
WEBHOOK_DELIVERY = True


def pprint(json_data):
    """
    Pretty print JSON formatted data
   :param json_data: data to pretty print
   :return None
    """
    print(json.dumps(json_data, indent=4, separators=(', ', ': ')))


def get_dnac_jwt_token(dnac_auth):
    """
    Create the authorization token required to access DNA C
   :param dnac_auth - Cisco DNA Center Basic Auth string
   :return: Cisco DNA Center JWT token
    """
    url = DNAC_URL + '/dna/system/api/v1/auth/token'
    header = {'content-type': 'application/json'}
    response = requests.post(url, auth=dnac_auth, headers=header, verify=False)
    dnac_jwt_token = response.json()['Token']
    return dnac_jwt_token


def get_report_view_groups(dnac_auth):
    """
    This function will return the report view groups
   :param dnac_auth: Cisco DNA Center Auth
   :return: report view groups
    """
    url = DNAC_URL + '/dna/intent/api/v1/data/view-groups'
    header = {'Content-Type': 'application/json', 'X-Auth-Token': dnac_auth}
    response = requests.get(url, headers=header, verify=False)
    report_view_groups = response.json()
    return report_view_groups


def get_report_view_ids(view_group_id, dnac_auth):
    """
    This function will get return the views for the groups id {view_group_id}
   :param view_group_id: report view group id
   :param dnac_auth: Cisco DNA Center Auth
   :return: the report view ids
    """
    url = DNAC_URL + '/dna/intent/api/v1/data/view-groups/' + view_group_id
    header = {'Content-Type': 'application/json', 'X-Auth-Token': dnac_auth}
    response = requests.get(url, headers=header, verify=False)
    report_view_ids = response.json()
    return report_view_ids


def get_detailed_report_views(view_id, group_id, dnac_auth):
    """
    This function will retrieve the view details for the view group id {group_id} and the view id {view_id}
   :param view_id: report view id
   :param group_id: report group id
   :param dnac_auth: Cisco DNA Center Auth
   :return: the report report view details
    """
    url = DNAC_URL + '/dna/intent/api/v1/data/view-groups/' + group_id + '/views/' + view_id
    header = {'Content-Type': 'application/json', 'X-Auth-Token': dnac_auth}
    response = requests.get(url, headers=header, verify=False)
    report_detailed_views = response.json()
    return report_detailed_views


def create_report(payload, dnac_auth):
    """
    This function will create a new Client Detail report
   :param payload: request payload
   :param dnac_auth: Cisco DNA Center Auth
   :return: return the API response
    """
    url = DNAC_URL + '/dna/intent/api/v1/data/reports'
    header = {'Content-Type': 'application/json', 'X-Auth-Token': dnac_auth}
    response = requests.post(url, headers=header, data=json.dumps(payload), verify=False)
    return response


def get_report_executions(report_id, dnac_auth):
    """
    This function will get the report executions info for the {report_id}
    :param report_id: the report id
    :param dnac_auth: Cisco DNA Center Auth
    :return: return the response payload
    """
    url = DNAC_URL + '/dna/intent/api/v1/data/reports/' + report_id + '/executions'
    header = {'Content-Type': 'application/json', 'X-Auth-Token': dnac_auth}
    response = requests.get(url, headers=header, verify=False)
    response_json = response.json()
    return response_json


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


def main():
    """
    This application will create a new Client Detail Report:
     - for the Global site
     - all client details
     - run now schedule
     - all client details
     - wired and wireless clients
     - will check when report execution is completed and save the report to a file
    """

    # logging, debug level, to file {application_run.log}
    logging.basicConfig(
        filename='application_run.log',
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    current_time = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print('\nCreate Report App Run Start, ', current_time)

    # get the Cisco DNA Center Auth token
    dnac_auth = get_dnac_jwt_token(DNAC_AUTH)

    # find out the report view group id
    report_view_groups = get_report_view_groups(dnac_auth)
    for view in report_view_groups:
        if view['category'] == REPORT_CATEGORY:
            view_group_id = view['viewGroupId']
    print('\nReport Category:', REPORT_CATEGORY)
    print('Report View Group Id is:', view_group_id)

    # find out the report view id's
    report_view_ids = get_report_view_ids(view_group_id, dnac_auth)
    report_views = report_view_ids['views']
    for view in report_views:
        if view['viewName'] == VIEW_NAME:
            report_view_id = view['viewId']
    print('Report View Name:', VIEW_NAME)
    print('Report View Id is:', report_view_id)

    # get the detailed report views
    report_detail_view = get_detailed_report_views(report_view_id, view_group_id, dnac_auth)
    print('\nClient Report Detail \n')
    pprint(report_detail_view)

    # create the report request payload
    
    report_request = {
        'name': REPORT_NAME,
        'description': '',
        'dataCategory': REPORT_CATEGORY,
        'viewGroupId': view_group_id,
        'viewGroupVersion': '2.0.0',
        'schedule': {
            'type': 'SCHEDULE_NOW'
        },
        'deliveries': [
            {
                'type': 'DOWNLOAD',
                "default": True
            }
        ],
        'view': {
            'name': VIEW_NAME,
            'viewId': report_view_id,
            'description': 'Client Report',
            'fieldGroups': [
                {
                    'fieldGroupName': 'client_details',
                    'fieldGroupDisplayName': 'Client Data',
                    'fields': [
                        {
                            'name': 'hostName',
                            'displayName': 'Host Name'
                        },
                        {
                            'name': 'username',
                            'displayName': 'User ID'
                        },
                        {
                            'name': 'macAddress',
                            'displayName': 'MAC Address'
                        },
                        {
                            'name': 'ipv4',
                            'displayName': 'IPv4 Address'
                        },
                        {
                            'name': 'ipv6',
                            'displayName': 'IPv6 Address'
                        },
                        {
                            'name': 'deviceType',
                            'displayName': 'Device Type'
                        },
                        {
                            'name': 'connectionStatus',
                            'displayName': 'Current Status'
                        },
                        {
                            'name': 'averageHealthScore_min',
                            'displayName': 'Min Health Score'
                        },
                        {
                            'name': 'averageHealthScore_max',
                            'displayName': 'Max Health Score'
                        },
                        {
                            'name': 'averageHealthScore_median',
                            'displayName': 'Median Health Score'
                        },
                        {
                            'name': 'usage_sum',
                            'displayName': 'Usage (MB)'
                        },
                        {
                            'name': 'connectedDeviceName',
                            'displayName': 'Connected Device Name'
                        },
                        {
                            'name': 'frequency',
                            'displayName': 'Band'
                        },
                        {
                            'name': 'rssi_median',
                            'displayName': 'RSSI (dBm)'
                        },
                        {
                            'name': 'snr_median',
                            'displayName': 'SNR (dB)'
                        },
                        {
                            'name': 'site',
                            'displayName': 'Last Location'
                        },
                        {
                            'name': 'lastUpdated',
                            'displayName': 'Last Seen'
                        },
                        {
                            'name': 'apGroup',
                            'displayName': 'AP Group'
                        },
                        {
                            'name': 'ssid',
                            'displayName': 'SSID'
                        },
                        {
                            'name': 'vlan',
                            'displayName': 'VLAN ID'
                        },
                        {
                            'name': 'vnid',
                            'displayName': 'VNID'
                        },
                        {
                            'name': 'onboardingEventTime',
                            'displayName': 'Onboarding Time'
                        },
                        {
                            'name': 'assocDoneTimestamp',
                            'displayName': 'Association Time'
                        },
                        {
                            'name': 'authDoneTimestamp',
                            'displayName': 'Authentication Time'
                        },
                        {
                            'name': 'aaaServerIp',
                            'displayName': 'Authentication Server'
                        },
                        {
                            'name': 'dhcpDoneTimestamp',
                            'displayName': 'Last DHCP Request'
                        },
                        {
                            'name': 'maxDhcpDuration_max',
                            'displayName': 'DHCP Response Time (ms)'
                        },
                        {
                            'name': 'dhcpServerIp',
                            'displayName': 'DHCP Server'
                        },
                        {
                            'name': 'linkSpeed',
                            'displayName': 'Link Speed (Mbps)'
                        },
                        {
                            'name': 'txRate_min',
                            'displayName': 'Min Tx Rate (bps)'
                        },
                        {
                            'name': 'txRate_max',
                            'displayName': 'Max Tx Rate (bps)'
                        },
                        {
                            'name': 'txRate_avg',
                            'displayName': 'Average Tx Rate (bps)'
                        },
                        {
                            'name': 'rxRate_min',
                            'displayName': 'Min Rx Rate (bps)'
                        },
                        {
                            'name': 'rxRate_max',
                            'displayName': 'Max Rx Rate (bps)'
                        },
                        {
                            'name': 'rxRate_avg',
                            'displayName': 'Average Rx Rate (bps)'
                        },
                        {
                            'name': 'txBytes_sum',
                            'displayName': 'Tx (MB)'
                        },
                        {
                            'name': 'rxBytes_sum',
                            'displayName': 'Rx (MB)'
                        },
                        {
                            'name': 'dataRate_median',
                            'displayName': 'Data Rate (Mbps)'
                        },
                        {
                            'name': 'dot11Protocol',
                            'displayName': 'Client Protocol'
                        }
                    ]
                }
            ],
            'filters': [
                {
                    'name': 'Location',
                    'displayName': 'Location',
                    'type': 'MULTI_SELECT_TREE',
                    'value': []
                },
                {
                    'name': 'DeviceType',
                    'displayName': 'Device Type',
                    'type': 'SINGLE_SELECT_ARRAY',
                    'value': []
                },
                {
                    'name': 'SSID',
                    'displayName': 'SSID',
                    'type': 'MULTI_SELECT',
                    'value': []
                },
                {
                    'name': 'Band',
                    'displayName': 'Band',
                    'type': 'MULTI_SELECT',
                    'value': []
                },
                {
                    'name': 'TimeRange',
                    'type': 'TIME_RANGE',
                    'displayName': 'Time Range',
                    'value': {
                        'timeRangeOption': 'LAST_24_HOURS',
                        'startDateTime': 0,
                        'endDateTime': 0
                    }
                }
            ],
            'format': {
                'name': 'JSON',
                'formatType': 'JSON',
                'default': False
            }
        }
    }

    create_report_status = create_report(report_request, dnac_auth)

    if create_report_status.status_code == 200:
        print('\nReport submitted')

        # parsing the response from create new report API
        create_report_json = create_report_status.json()
        report_id = create_report_json['reportId']
        print('Report id: ', report_id)

        # verify when the report execution starts
        # this app will create a new report, not execute an existing report again
        # due to this there will be always execution count "0" when the report is triggered
        # for a new report, not executed yet

        print('\nWait for report execution to start')
        execution_count = 0
        while execution_count == 0:
            time.sleep(1)
            print('!', end="")
            report_details = get_report_executions(report_id, dnac_auth)
            execution_count = report_details['executionCount']

        # report execution started
        print('\n\nReport execution started, wait for process to complete')

        # check when the report is completed
        process_status = None
        while process_status != 'SUCCESS':
            time.sleep(1)
            print('!', end="")
            report_details = get_report_executions(report_id, dnac_auth)
            execution_info = report_details['executions'][0]
            process_status = execution_info['processStatus']

        # execution completed successfully

        print('\n\nReport execution completed')
        execution_id = report_details['executions'][0]['executionId']
        print('Report execution id: ', execution_id)

        # download the report
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

    else:
        print('\nReport not submitted, ', report_status.text)
    current_time = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print('\nCreate Report App Run End, ', current_time)


if __name__ == '__main__':
    main()
