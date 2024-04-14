import adafruit_mcp3xxx.mcp3008 as MCP
import adafruit_mcp3xxx.analog_in as AnalogIn
import busio
import board
import digitalio
import time

from lib.config import config
from lib.utils import Logger
from lib.controller import MQTT


class MoistureSensor:
    def __init__(
        self,
        digital_in_out,
        mcp_channel,
        logger: Logger,
        mqtt_client: MQTT,
        print_to_console: bool = False,
    ):
        self.__spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
        self.__cs = digitalio.DigitalInOut(digital_in_out)
        self.__mcp3008 = MCP.MCP3008(self.__spi, self.__cs)
        self.__sensor= AnalogIn(mcp=self.__mcp3008, positive=mcp_channel)

        self.__mqtt_client = mqtt_client
        self.__logger = logger
        self.__print_to_console = print_to_console

    def __voltage_to_moisture(voltage) -> float:
        # Dry condition
        # Based on testing, 2.5V seems to be the highest achieved in the testing environment
        MAX_OPERATING_VOLTAGE = 2.5
        # Moist condition
        # Based on testing, 1.0V seems to be the lowest achieved in the testing environment
        MIN_OPERATING_VOLTAGE = 1.0

        MAX_MOISTURE = 100
        MIN_MOISTURE = 0

        # Logarithmetic curve on the moisture content vs capacitance
        hypothetical_moisture_content = MAX_MOISTURE - (
            (voltage - MIN_OPERATING_VOLTAGE)
            / (MAX_OPERATING_VOLTAGE - MIN_OPERATING_VOLTAGE)
        ) * (MAX_MOISTURE - MIN_MOISTURE)
        return max(MIN_MOISTURE, min(MAX_MOISTURE, hypothetical_moisture_content))

    def read_sensor(self):
        while True:
            try:
                voltage = self.__sensor.voltage

                moisture_content = self.__voltage_to_moisture(voltage)

                if not self.__print_to_console:
                    print(
                        "Moisture Content: {0:3f}; Voltage: {1:3f}V".format(
                            moisture_content, voltage
                        )
                    )
                    
                self.__mqtt_client.publish_mqtt(
                    config.MQTT_TOPIC_MOISTURE, moisture_content
                )

                time.sleep(1)

            except RuntimeError as error:
                self.__logger.error(error.args[0])
                continue

            except Exception as error:
                self.__logger.critical(error.args[0])
                raise error
