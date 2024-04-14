import paho.mqtt.subscribe as subscribe
import paho.mqtt.client as mqtt
import os
import time
import influxdb_client

from influxdb_client.client.write_api import SYNCHRONOUS
from multiprocessing import Pool


class Controller:
    def __init__(self, mqtt_host: str, mqtt_port: int):
        self.host = mqtt_host
        self.port = mqtt_port

        self.__token = os.environ.get("INFLUXDB_TOKEN")
        self.__org = os.environ.get("INFLUXDB_ORG")
        self.__url = os.environ.get("INFLUXDB_URL")
        self.__bucket = os.environ.get("INFLUXDB_BUCKET")

        self.influxdb_client = influxdb_client.InfluxDBClient(
            url=self.__url, token=self.__token, org=self.__org
        )
        self.__write_api = self.influxdb_client.write_api(write_options=SYNCHRONOUS)

    def __on_message(self, client, userdata, message: mqtt.MQTTMessage):
        topic = message.topic

        if topic.startswith("sensors/"):
            measurement = "pellet_production"
            tag = topic[8:]
            payload = message.payload.decode("utf-8")
            
            if tag == "temperature":
                unit = "C"
            elif tag == "humidity" or tag == "moisture":
                unit = "%"

            record = {
                "measurement": measurement,
                "tags": {"sensor": tag},
                "fields": {unit: float(payload)}
            }

            self.__write_api.write(bucket=self.__bucket, org=self.__org, record=record)

    def callback_wrapper(self, topic: str):
        subscribe.callback(self.__on_message, topic, hostname=self.host, port=self.port)

    def listen(self, topics: tuple[str]):
        topic_args = [(topic,) for topic in topics]

        with Pool(len(topics)) as pool:
            pool.starmap(self.callback_wrapper, topic_args)
