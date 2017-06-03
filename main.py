import ble
import mqtt
from config import *

try:
    ble.start()
    mqtt.start()

finally:
    #notify MQTT subscribers that gateway is offline
    mqtt.publish(TOPIC_PREFIX, "offline")
    
    ble.stop()
