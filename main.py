from lib.sensors import SensorManager
from lib.config import config
from lib.controller import Controller
from lib.utils import setup_logger

def main():
    logger = setup_logger("sensor_log", "./logs", "sensor.log")

    sensor_manager = SensorManager(logger=logger, print_to_console=True, use_legacy_dht=True)
    controller = Controller(mqtt_host=config.MQTT_BROKER_ADDRESS, mqtt_port=int(config.MQTT_BROKER_PORT))

    sensor_manager.run()
    controller.listen((config.MQTT_TOPIC_MOISTURE, config.MQTT_TOPIC_TEMPERATURE, config.MQTT_TOPIC_HUMIDITY))
    

if __name__ == "__main__":
    main()
