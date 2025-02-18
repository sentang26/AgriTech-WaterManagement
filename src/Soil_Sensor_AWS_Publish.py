import time

import boto3
from boto3.dynamodb.conditions import Key, Attr
import datetime
import os
import json
import random
import sched
import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT

# Define ENDPOINT, TOPIC, RELATOVE DIRECTORY for CERTIFICATE AND KEYS
ENDPOINT = "account_endpoint_for_things.amazonaws.com"
PATH_TO_CERT = "..\\config"
TOPIC = "iot/agritech"

# AWS class to create number of objects (devices)
class AWS():
    # Constructor that accepts client id that works as device id and file names for different devices
    # This method will obviosuly be called while creating the instance
    # It will create the MQTT client for AWS using the credentials
    # Connect operation will make sure that connection is established between the device and AWS MQTT
    def __init__(self, client, certificate, private_key):
        self.client_id = client
        self.device_id = client
        self.cert_path = PATH_TO_CERT + "\\" + certificate
        self.pvt_key_path = PATH_TO_CERT + "\\" + private_key
        self.root_path = PATH_TO_CERT + "\\" + "AmazonRootCA1.pem"
        self.myAWSIoTMQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient(self.client_id)
        self.myAWSIoTMQTTClient.configureEndpoint(ENDPOINT, 8883)
        self.myAWSIoTMQTTClient.configureCredentials(self.root_path, self.pvt_key_path, self.cert_path)
        self._connect()

    # Connect method to establish connection with AWS IoT core MQTT
    def _connect(self):
        self.myAWSIoTMQTTClient.connect()

    # This method will publish the data on MQTT 
    # Before publishing we are confiuguring message to be published on MQTT
    def publish(self):
        print('Begin Publish')
        for i in range (10):
            message = {}    
            value = float(random.normalvariate(99, 1.5))
            value = round(value, 1)
            timestamp = str(datetime.datetime.now())
            message['device_id'] = self.device_id
            message['timestamp'] = timestamp
            message['device_type'] = 'Temperature'
            message['value'] = value
            messageJson = json.dumps(message)
            self.myAWSIoTMQTTClient.publish(TOPIC, messageJson, 1) 
            print("Published: '" + json.dumps(message) + "' to the topic: " + TOPIC)
            time.sleep(0.1)
        print('Publish End')

    # Disconect operation for each devices
    def disconnect(self):
        self.myAWSIoTMQTTClient.disconnect()

# Main method with actual objects and method calling to publish the data in MQTT
# Again this is a minimal example that can be extended to incopporate more devices
# Also there can be different method calls as well based on the devices and their working.
if __name__ == '__main__':

    # Here we assign our aws clients/resources to use
    iot_client = boto3.client('iot',region_name ='us-east-1')
    s3 = boto3.resource(service_name = 's3')
    dynamodb_resource = boto3.resource('dynamodb',region_name='us-east-1')
    table = dynamodb_resource.Table('farmraw')
    
    # retrive unique device ids from the IOT Core 
    response = iot_client.list_things(maxResults=100, thingTypeName='Farm')
    devices = response["things"]

    device_ids = []
    sensors = []
    for y in devices:
            device_id = y["thingName"]
            device_ids.append(device_id)

    for device_id in device_ids:
        # SOil sensor device Objects
        soil_sensor = AWS(device_id, "thing_1_certificate_filename", "thing_1_private_key_filename")
        sensors.append(soil_sensor)

    for sensor in (sensors):
        sensor.publish()

