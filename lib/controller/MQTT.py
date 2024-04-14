import paho.mqtt.client as mqtt
from lib.utils.Logger import setup_logger


class MQTT:
    def __init__(
        self,
        host: str,
        port: int = 1883,
    ):
        self.logger = setup_logger("mqtt_log", "./logs", "mqtt.log")
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.mqtt_client.on_pre_connect = self.__on_preconnect
        self.mqtt_client.on_connect = self.__on_connect
        self.mqtt_client.connect(host, port)

    def __on_preconnect(self, client, userdata):
        self.logger.info("Initializing connection to MQTT broker")

    def __on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            self.logger.info("Connected to MQTT broker")
        else:
            self.logger.error(
                f"Failed to connect to MQTT broker with result code {reason_code}"
            )

    def publish_mqtt(self, topic, payload):
        self.mqtt_client.publish(topic, payload)


    def start(self):
        self.mqtt_client.loop_start()
