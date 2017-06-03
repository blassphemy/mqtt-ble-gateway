import paho.mqtt.client as mqtt
import functools
import ble
import error
import re
from config import *

client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
        #subscribe to all relevant topics
        client.subscribe(TOPIC_COMMAND + "/#")
    
        #notify MQTT subscribers that gateway is online
        client.publish(TOPIC_PREFIX, "online")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    
    #check if topic is valid
    if len(msg.topic.split("/")) >= 6:
        mac = msg.topic.split("/")[3]
        cmd = msg.topic.split("/")[4]
        target = msg.topic.split("/")[5]

        #check for valid MAC address
        mac_valid = re.match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac.lower())
        #check for valid command
        cmd_valid = ((cmd == "connect") or (cmd == "read") or (cmd == "write") or (cmd == "subscribe") or (cmd == "unsubscribe"))
        #check for valid UUIDs and handles
        target_valid = (len(target) == 36)

        if mac_valid and cmd_valid and target_valid:
            #execute the received BLE command
            ble.execute_command(mac, cmd, target, msg.payload)
        else:
            if not mac_valid: error.error("MQTT: invalid MAC address!")
            if not cmd_valid: error.error("MQTT: invalid command!")
            if not target_valid: error.error("MQTT: not a valid UUID!")

    #check if scan was requested
    elif len(msg.topic.split("/")) == 4 and msg.topic.split("/")[3] == "scan":
        print("starting full BLE scan!")
        ble.scan_devices()
                
    else:
        error.error("MQTT: received topic is not valid!")

def start():
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE)
        
    client.loop_forever()
        
            
def publish(topic, msg):
    client.publish(topic, msg)
