import paho.mqtt.subscribe as subscribe
import paho.mqtt.client as mqtt
import os
import time
import influxdb_client

class Controller:
    def __init__(self, mqtt_host: str, mqtt_port: int):
        self.host = mqtt_host
        self.port = mqtt_port

        self.__token = os.environ.get("INFLUXDB_TOKEN")
        self.__org = os.environ.get("INFLUXDB_ORG")
        self.__url = os.environ.get("INFLUXDB_URL")

        self.influxdb_client = influxdb_client.InfluxDBClient(url=self.__url, token=self.__token, org=self.__org)
    
    
    def __on_message(self, client, userdata, message: mqtt.MQTTMessage):
        payload = message.payload
        print("%s" % (payload))


    def listen(self, topic: str):
        subscribe.callback(self.__on_message, topic, hostname=self.host, port=self.port)