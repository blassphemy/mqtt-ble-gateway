TOPIC_PREFIX = "home/MQTTtoBLE"             #MQTT prefix to identify this device
TOPIC_COMMAND = TOPIC_PREFIX + "/command"   #MQTT -> BLE
TOPIC_DEVICE = TOPIC_PREFIX + "/device"     #MQTT <- MQTT

MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60

BLE_CONNECTION_TRIES = 3					#number of BLE error retries