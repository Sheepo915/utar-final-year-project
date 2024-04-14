import adafruit_dht
import Adafruit_DHT as DHT  # Legacy library
import board

from lib.config import config
from lib.controller import MQTT
from lib.utils import Logger


class TempHumiditySensor:
    def __init__(
        self,
        mqtt_client: MQTT,
        logger: Logger,
        print_to_console: bool = False,
        use_legacy: bool = False,
    ):
        self.dht11 = (
            adafruit_dht.DHT11(board.D4) if use_legacy is not True else DHT.DHT11
        )
        self.__use_legacy = use_legacy
        self.__mqtt_client = mqtt_client
        self.__logger = logger
        self.__print_to_console = print_to_console

    def read_sensor(self):
        while True:
            try:
                # humidity, temperature

                if self.__use_legacy is not True:
                    temperature = self.dht11.temperature
                    humidity = self.dht11.humidity
                else:
                    humidity, temperature = DHT.read_retry(
                        self.dht11, 4, delay_seconds=1
                    )

                self.__mqtt_client.publish_mqtt(
                    config.MQTT_TOPIC_TEMPERATURE, temperature
                )
                self.__mqtt_client.publish_mqtt(config.MQTT_TOPIC_HUMIDITY, humidity)

                if not self.__print_to_console:
                    print(
                        "Temperature: {0:1f}; Humidity: {1:1f}".format(
                            temperature, humidity
                        )
                    )

            except RuntimeError as error:
                self.__logger.error(error.args[0])
                continue
            except Exception as error:
                self.__logger.critical(error.args[0])
                raise error
