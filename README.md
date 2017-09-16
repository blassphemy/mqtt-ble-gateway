# mqtt-ble-gateway

The mqtt-ble-gateway is designed to provide a generic bidirectional gateway between a MQTT broker and BLE devices. It allows to scan for BLE devices and read or write specific characteristics by their UUID. Furthermore, subscriptions and notifications are supported.

## Installation
```
sudo pip install pygatt paho-mqtt pexpect
setcap 'cap_net_raw,cap_net_admin+eip' `which hcitool`
```

## Start
```
python main.py
```

## MQTT commands
- home/MQTTtoBLE/command/scan
- home/MQTTtoBLE/command/**MAC**/connect
- home/MQTTtoBLE/command/**MAC**/read/**UUID**
- home/MQTTtoBLE/command/**MAC**/write/**UUID** **value**
- home/MQTTtoBLE/command/**MAC**/subscribe/**UUID**
- home/MQTTtoBLE/command/**MAC**/unsubscribe/**UUID**

## MQTT responses
- /home/MQTTtoBLE **online**
- /home/MQTTtoBLE **offline**
- home/MQTTtoBLE/device/scan **results**
- home/MQTTtoBLE/device/**MAC**/read/**handle** **value**
- home/MQTTtoBLE/device/**MAC**/notify/**handle** **value**

## Examples
```
# read the current color of a BLE lamp
mosquitto_pub -h localhost -t home/MQTTtoBLE/command/F4:B8:5E:XX:XX:XX/read/0000ffb2-0000-1000-8000-00805f9b34fb -m ""
# --> d0ffffff (current color = white)

# set the color of a BLE lamp to red
mosquitto_pub -h localhost -t home/MQTTtoBLE/command/F4:B8:5E:XX:XX:XX/write/0000ffb2-0000-1000-8000-00805f9b34fb -m "d0ff0000"

# vibrate Xiaomi Mi Band 1
mosquitto_pub -h localhost -t home/MQTTtoBLE/command/C8:0F:10:XX:XX:XX/write/00002a06-0000-1000-8000-00805f9b34fb -m "01"
```
