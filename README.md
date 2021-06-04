
# Cisco DNA Center Report Operations


This repo is for an application that will create a new Cisco DNA Center Client Detail report, receive notifications when the report is in progress and completed. 
It will download the report file from Cisco DNA Center using APIs.
 
This app is to be used only for demos or lab environments, it is not written for production. 

Please follow these recommendations for production Flask deployments: https://flask.palletsprojects.com/en/1.1.x/deploying/.



**Cisco Products & Services:**

- Cisco DNA Center

**Tools & Frameworks:**

- Python environment to run the Flask App as a Webhook Receiver - "report_receiver.py"
- Python environment to execute the application that will create and run the report - "dnacenter_create_report.py"

**Usage**

The script "dnacenter_create_report.py" will identify:
 - report group id for the report category "Client"
 - report view id for the report "Client Detail"
 - the configured webhook id where to send the report status notifications
 - construct the payload required to create the new report
 - create a new report

Sample Output:
```
/Users/gzapodea/PythonCode/dnacenter_reports_operations/venv/bin/python /Users/gzapodea/PythonCode/dnacenter_reports_operations/dnacenter_create_report.py

Create Report App Run Start,  2021-06-03 17:58:25

Report Category: Client
Report View Group Id is: d7afe5c9-4941-4251-8bf5-0fb643e90847
Report View Name: Client Detail
Report View Id is: e8e66b17-4aeb-4857-af81-f472023bb05e
Webhook Name: LinuxMint_Report
Webhook Id: 8dcbeb87-420b-49f1-b813-a0c0046e3672 


Client Report Detail 

{
    "viewId": "e8e66b17-4aeb-4857-af81-f472023bb05e", 
    "viewName": "Client Detail", 
    "description": "This client report view provides detailed information about the list of clients that are seen in the network", 
    "viewInfo": null, 
    "schedules": [
        {
            "type": "SCHEDULE_NOW", 
            "default": true
        }, 
        {
            "type": "SCHEDULE_LATER", 
            "default": false
        }, 
        {
            "type": "SCHEDULE_RECURRENCE", 
            "default": false
        }
    ], 
    "deliveries": [
        {
            "type": "DOWNLOAD", 
            "default": true
        }, 
        {
            "type": "EMAIL", 
            "default": false
        }, 
        {
            "type": "WEBHOOK", 
            "default": false
        }
    ], 
    "formats": [
        {
            "name": "CSV", 
            "format": "CSV", 
            "template": {
                "jsTemplateId": "BJYghfA3z"
            }, 
            "default": true
        }, 
        {
            "name": "Tableau Data Extract", 
            "format": "TDE", 
            "template": null, 
            "default": false
        }, 
        {
            "name": "JSON", 
            "format": "JSON", 
            "template": null, 
            "default": false
        }
        ...
    ]
}

Report submitted

Create Report App Run End,  2021-06-03 17:58:28

```

The "report_receiver.py" will receive the Cisco DNA Center report notifications, download and save the report file when completed.

Sample Output:

```

Webhook Received
Payload: 
{'Event Id': '7332787b-d727-48a1-baba-288385bdf6df', 'Event Timestamp': 1622765873532, 'Event Name': 'Report [Client Report Detail 24h] - In Progress', 'Event Type': 'APP', 'Cisco DNA Center Event Context link. **This link is active only in the context of Cisco DNA Center. You must have necessary permissions to login': 'https://10.93.141.35/data-sets-reports?report-tab=list&list-tab=my-reports&data-set-id=f8a68f72-aeaf-42ab-b665-f142a9335816', 'Event Details': {'name': 'Report [Client Report Detail 24h]', 'status': 'In Progress', 'status update @': 'Fri Jun 04 00:17:53 UTC 2021'}} 

173.36.240.173 - - [03/Jun/2021 17:17:56] "POST /dnacenter_report HTTP/1.1" 202 -
Webhook Received
Payload: 
{'Event Id': 'd717cec1-0b12-4c37-95fb-efb4603dfe27', 'Event Timestamp': 1622765900832, 'Event Name': 'Report [Client Report Detail 24h] - Success', 'Event Type': 'APP', 'Cisco DNA Center Event Context link. **This link is active only in the context of Cisco DNA Center. You must have necessary permissions to login': 'https://10.93.141.35/data-sets-reports?report-tab=list&list-tab=my-reports&data-set-id=f8a68f72-aeaf-42ab-b665-f142a9335816&execution-id=f2ce8bed-1734-4652-9150-ab3aa013fae8', 'Event Details': {'name': 'Report [Client Report Detail 24h]', 'status': 'Success', 'status update @': 'Fri Jun 04 00:18:20 UTC 2021'}} 


Report Id:  f8a68f72-aeaf-42ab-b665-f142a9335816 
Execution Id:  f2ce8bed-1734-4652-9150-ab3aa013fae8

Report content:
 {'client_details': [], 'filters': [{'name': 'Location', 'displayName': 'Location', 'values': []}, {'name': 'DeviceType', 'displayName': 'Device Type', 'values': ['']}, {'name': 'SSID', 'displayName': 'SSID', 'values': []}, {'name': 'Band', 'displayName': 'Band', 'values': []}, {'name': 'startTime', 'displayName': 'Start Time', 'values': ['2021-06-03 00:17:54.022 AM UTC']}, {'name': 'endTime', 'displayName': 'End Time', 'values': ['2021-06-04 00:17:54.022 AM UTC']}]}
Client report file saved
```
 
This sample code is for proof of concepts and labs

**License**

This project is licensed to you under the terms of the [Cisco Sample Code License](./LICENSE).


