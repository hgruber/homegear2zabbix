#!/usr/bin/env python
import re
import paho.mqtt.client as mqtt
import xmlrpclib
import json
from zabbix.sender import ZabbixMetric, ZabbixSender

homegear_host = "balmung"
zabbix_host = "balmung"
application = "homegear"
types   = {
    "climate":  re.compile('^HM-WDS.*-TH-'), 
    "thermostat": re.compile('^HM-CC-RT-DN'),
    "actor": re.compile('^HM-LC-Sw1-Pl-DN-R1')
}
sensors = {}
devicetypes = {}

def get_devices():
    devices = {}
    data = {}
    message = []
    homegear = xmlrpclib.ServerProxy('http://'+homegear_host+':2001')
    for device in homegear.listDevices(False, ('FAMILY', 'ID', 'ADDRESS', 'TYPE', 'FIRMWARE')):
        info = homegear.getDeviceInfo(device['ID'], ('NAME', 'RSSI', 'INTERFACE'))
        name = info['NAME']
        if name == '': continue # don't discover unnamed devices
        devicetype = application+'.discovery.'+get_device_type(device['TYPE'])
        if devicetype not in devices: devices[devicetype] = []
        devices[devicetype].append({ '{#SENSOR}': name })
        sensors[int(device['ID'])] = name
        devicetypes[int(device['ID'])] = get_device_type(device['TYPE'])
    for devicetype in devices:
        data['data'] = devices[devicetype]
        message.append(ZabbixMetric(zabbix_host, devicetype, json.dumps(data)))
    ZabbixSender(zabbix_host, 10051).send(message)

def get_device_type(name):
    for devicetype in types:
        if types[devicetype].match(name): return devicetype
    return name

def on_connect(client, userdata, flags, rc):
    client.subscribe("/#")

def on_message(client, userdata, msg):
    device = int(re.sub( r'.*/event/([0-9]*)/.*', '\\1', msg.topic))
    if device not in sensors:
        get_devices()
        if device not in sensors: return
    name = sensors[device]
    typ = devicetypes[device]
    parameter = re.sub( r'.*/event/.*/', '', msg.topic).lower()
    value = re.sub( r'\[(.*)\]', '\\1', msg.payload)
    message = []
    message.append(ZabbixMetric(zabbix_host, application+'.'+typ+'.'+parameter+'['+name+']', value))
    ZabbixSender(zabbix_host, 10051).send(message)

get_devices()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(homegear_host, 1883, 60)
client.loop_forever()
