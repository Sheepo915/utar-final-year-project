import adafruit_mcp3xxx.mcp3008 as MCP
import board
import threading

from lib.config import config
from lib.utils import Logger
from lib.sensors.MoistureSensor import MoistureSensor
from lib.sensors.TempHumiditySensor import TempHumiditySensor
from lib.controller.MQTT import MQTT


class SensorManager:
    def __init__(
        self,
        logger: Logger,
        print_to_console: bool = False,
        use_legacy_dht: bool = False,
    ):
        self.__mqtt_client = MQTT(config.MQTT_BROKER_ADDRESS, int(config.MQTT_BROKER_PORT))
        self.moisture_sensor = MoistureSensor(
            digital_in_out=board.D5,
            mcp_channel=MCP.P0,
            logger=logger,
            mqtt_client=self.__mqtt_client,
            print_to_console=print_to_console
        )
        self.temp_humidity_sensor = TempHumiditySensor(
            mqtt_client=self.__mqtt_client,
            logger=logger,
            print_to_console=print_to_console,
            use_legacy=use_legacy_dht,
        )

    def run(self):
        self.__mqtt_client.start()

        temp_humidity_sensor_thread = threading.Thread(target=self.temp_humidity_sensor.read_sensor)
        moisture_sensor_thread = threading.Thread(target=self.moisture_sensor.read_sensor)

        temp_humidity_sensor_thread.start()
        moisture_sensor_thread.start()
