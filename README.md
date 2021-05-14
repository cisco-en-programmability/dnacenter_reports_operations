
# Cisco DNA Center Report Operations


This repo is for an application that will create a new Cisco DNA Center Client Detail report, receive notifications when the report is in progress and completed. 
It will download from Cisco DNA Center using APIs.
 
This app is to be used only in demo or lab environments, it is not written for production. Please follow these
 recommendations for production Flask deployments: https://flask.palletsprojects.com/en/1.1.x/deploying/.



**Cisco Products & Services:**

- Cisco DNA Center

**Tools & Frameworks:**

- Python environment to run the Flask App as a Webhook Receiver

**Usage**

The "flask_receiver.py" will receive the Cisco DNA Center report notifications.

It will save the report to a file.
 
 This sample code is for proof of concepts and labs

**License**

This project is licensed to you under the terms of the [Cisco Sample Code License](./LICENSE).


