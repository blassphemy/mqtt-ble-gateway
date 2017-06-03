import pygatt
import binascii
import functools
import mqtt
import error
import time
import json
from config import *
from retrying import retry

adapter = pygatt.GATTToolBackend()
#dictionary to store connections to BLE devices by their MAC-addresses
devices = {}
    

def start():
    adapter.start()
    
def stop():
    adapter.stop()

def connect(mac):
    adapter.connect(mac)
    

def execute_command(mac, cmd, target, msg="", tries=0):
    # return if maximum number of connection tries is reached
    if tries >= BLE_CONNECTION_TRIES:
        return
    
    try:
        print(mac + " " + cmd + " " + target + " " + str(msg))
        
        if devices.get(mac) == None or cmd == 'connect':
            #establish connection to devices using the mac address
            devices[mac] = adapter.connect(mac)

        if cmd == 'read':
            #read value by UUID
            read_value_handler(mac, target, devices[mac].char_read(target))
        
        elif cmd == 'write':
            #write value with UUID
            devices[mac].char_write(target, binascii.unhexlify(msg))
            
        elif cmd == 'subscribe':
            # subscribe by mac and handle
            #notify_callback = functools.partial(notification_handler, mac=mac)
            devices[mac].subscribe(target, functools.partial(notification_handler, mac))
    
        elif cmd == 'unsubscribe':
            # unsubscribe by UUID
            devices[mac].unsubscribe(target)
        
        else:
            error.error("BLE: received unsupported command!")
            
    except pygatt.exceptions.NotificationTimeout:
        reset_connection(mac, cmd, target, msg, tries, "BLE: notification timeout!")
    except pygatt.exceptions.NotConnectedError:
        reset_connection(mac, cmd, target, msg, tries, "BLE: not connected!")
    except ValueError:
        reset_connection(mac, cmd, target, msg, tries, "BLE: value error!")
    except pygatt.exceptions.BLEError:
        reset_connection(mac, cmd, target, msg, tries, "BLE: general BLE error!")
    
    
def reset_connection(mac, cmd, target, msg, tries, err):
    #allow to modify global variable adapter
    global adapter
    
    tries +=1
    
    error.error(err)
        
    print("reset connection to BLE device!")
    adapter.stop()
    adapter.start()
    
    devices[mac] = None
    
    execute_command(mac, cmd, target, msg, tries)

def notification_handler(mac, handle, data):
    value = str(binascii.hexlify(data))
    
    print("received notification from " + mac + " and handle: " + hex(handle) + " with data: " + value)

    #send this via MQTT
    mqtt.publish(TOPIC_DEVICE + "/" + mac +"/notify/" + hex(handle), value)

        
def read_value_handler(mac, source, value):
    print("read value: " + str(binascii.hexlify(value)))
    
    #send this via MQTT
    mqtt.publish(TOPIC_DEVICE + "/" + mac +"/read/" + source, binascii.hexlify(value))
    
    
def scan_devices(results={}, tries=0):
    # return if maximum number of connection tries is reached
    if tries >= BLE_CONNECTION_TRIES:
        error.error("aborted BLE search because of multiple connection errors!")
        return results
    
    try:
        #start scanning for BLE devices
        ble_devices = adapter.scan()
        print("found devices" + str(ble_devices))
    
        for device in ble_devices:
            #check if this devices was already completely scanned
            if not device['address'] in results:
                dev = adapter.connect(device['address'])
                chars = dev.discover_characteristics()

                #create dictionary for results of this particular device                
                results[device['address']] = {}
                
                #store device name in results
                results[device['address']]['name'] = device['name']
                
                results[device['address']]['uuids'] = [str(uuid) for uuid in chars]
            else:
                print("skip device " + device['address'] + " because it was already scanned completely!")
            
        #send results via MQTT
        mqtt.publish(TOPIC_DEVICE + "/scan", json.dumps(results))
        print("finished BLE scan successfully!")
    
    except pygatt.exceptions.NotificationTimeout:
        reset_scan(results, tries, "BLE scan: received notification timeout!")
    except pygatt.exceptions.NotConnectedError:
        reset_scan(results, tries, "BLE scan: received not connected error!")
    except pygatt.exceptions.BLEError:
        reset_scan(results, tries, "BLE scan: received general BLE error!")
        
        
def reset_scan(results, tries, err):
    #allow to modify global variable adapter
    global adapter

    error.error(err)
    
    tries += 1
        
    print("reset connection to scan for new BLE devices!")
    adapter.stop()
    adapter.start()
    
    scan_devices(results, tries)