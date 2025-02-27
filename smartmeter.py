#!/usr/bin/env python3

# Prerequisites
# sudo apt install python3-requests python3-bs4 python3-paho-mqtt

import requests, base64
from requests.auth import HTTPDigestAuth
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import paho.mqtt.publish as publish

# General config
user= 'my_super_username_from_Netzbetreiber'
password = 'my_super_password_from_Netzbetreiber'
smartmeter_id= '1EFR123456789'

# MQTT config
broker= 'homeassistant'
mqttport= 1883
mqttuser= 'mqttusername'
mqttpass= 'mqtt1234'


#static config, normally no need to change
url = 'https://192.168.1.200/cgi-bin/hanservice.cgi'

# Hier startet der Spass
s = requests.Session()
res=s.get(url,auth=HTTPDigestAuth(user, password),verify=False)
cookies = { 'Cookie' : res.cookies.get('session')}

soup = BeautifulSoup(res.content, 'html.parser')
tags = soup.find_all('input')
token = tags[0].get('value')
action = 'meterform'
post_data = "tkn=" + token + "&action=" + action 

res = s.post(url, data=post_data,cookies=cookies,verify=False)

soup = BeautifulSoup(res.content, 'html.parser')
sel = soup.find(id='meterform_select_meter')
meter_val = sel.findChild()
meter_id = meter_val.attrs.get('value')
post_data = "tkn=" + token + "&action=showMeterProfile&mid=" + meter_id

res= s.post(url, data=post_data,cookies=cookies,verify=False)

soup = BeautifulSoup(res.content, 'html.parser')
table_data = soup.find('table', id="metervalue")

# Listen, um die Daten zu speichern
results = []

# Alle Zeilen der Tabelle finden (außer der Kopfzeile)
rows = table_data.find_all('tr')[1:]  # Überspringe die erste Zeile, da es eine Kopfzeile gibt

for row in rows:
    result_data = {
                    'value': table_data.find(id="table_metervalues_col_wert").string,
                    'unit': table_data.find(id="table_metervalues_col_einheit").string,
                    'timestamp': table_data.find(id="table_metervalues_col_timestamp").string,
                    'isvalid': table_data.find(id="table_metervalues_col_istvalide").string,
                    'name': table_data.find(id="table_metervalues_col_name").string,
                    'obis': table_data.find(id="table_metervalues_col_obis").string
                }
    msgs = [ 
            {
            'topic': f"homeassistant/sensor/{smartmeter_id}/{result_data['obis']}_value",
            'payload': result_data['value'], 'qos':1, 'retain': False
            },
            {
            'topic': f"homeassistant/sensor/{smartmeter_id}/{result_data['obis']}_unit",
            'payload': result_data['unit'], 'qos':1, 'retain': False
            },
            {
            'topic': f"homeassistant/sensor/{smartmeter_id}/{result_data['obis']}_timestamp",
            'payload': result_data['timestamp'], 'qos':1, 'retain': False
            },
            {
            'topic': f"homeassistant/sensor/{smartmeter_id}/{result_data['obis']}_isvalid",
            'payload': result_data['isvalid'], 'qos':1, 'retain': False
            },
            {
            'topic': f"homeassistant/sensor/{smartmeter_id}/{result_data['obis']}_name",
            'payload': result_data['name'], 'qos':1, 'retain': False
            }
    ]
    results.append(result_data)
    publish.multiple(msgs, hostname= broker, port= mqttport, auth={'username': mqttuser, 'password':mqttpass})

# Ergebnisse ausgeben
for result in results:
    print(result['obis']+ ": " + result['timestamp']+ " " + result['value']+ " " + result['unit'] + " (" + result['name'] +")")


s.close()
