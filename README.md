# han_mqtt_gw
Smart Meter HAN to MQTT Gateway

## Purpose
This Python Script reads in data from a smart meter with HAN interface and sends it for further processing via MQTT to smart home systems (e.g. Home Assistant). 
Additionally there are some helper files to setup a NGINX Reverse Proxy and Home Assistant Configuration

## Starting Point
In my case the smart meter is from the company PPC and has a HAN port. The HAN port in this case is nothing more than a Ethernet Port.
In german: Intelligentes Messsystem
The term "intelligent" is a little exagerated... I would say it reached at least what was state-of-the-art in 2005.

Unfortunately the IP address is fixed to ** 192.168.1.200 ** and cannot be changed - almost nothing can be changed, except the password for the user.
As we have two smart meters (one for heat pump, one for regular energy) a simple integration in our network was not possible. 

## Concept
I used two old Raspberry Pi 3B to act as a bridge to my network and also as a MQTT client to upload the latest readings to Home Assistant.
The Raspberries connect via WiFi to the regular network and connect directly via a static IPv4 address to the smart meter.
The Raspberries have also NGINX with a reverse proxy installed, that I can easily connect the (super slow) Web Interface of the smart meter.
If you want to use the Python script with an easier setup - also no problem: The script directly parses the webpage and extracts the latest data, no matter how you connect the smart meter.

## Prerequisites
A fresh installation of Raspbian is the starting point.
after logging in, you should perform a full upgrade to have the latest packages installed:
```
sudo apt update && sudo apt full-upgrade
```
As Git is not part of the standard installation, please install the git package to get a clone of this repository
```
sudo apt install git
```
You then can clone this repository:
```
git clone https://github.com/Rincewind76/han_mqtt_gw
```

Then install the necessary packages for python
```
sudo apt install python3-requests python3-bs4 python3-paho-mqtt
```

## Configuration
After changing the directory
```
cd han_mqtt_gw
```
please open an editor to change the user/password
```
nano smartmeter.py
```
Search for the lines 
```
# General config
user= 'my_super_username_from_Netzbetreiber'
password = 'my_super_password_from_Netzbetreiber'
smartmeter_id= '1EFR123456789'
```
The username and password is usually provided by the provider of the grid (Netzbetreiber). The smartmeter ID is only used to cluster the MQTT messages, so no check is done if it is the real ID.

The MQTT host has to be edited as well just below.

## Execution
The script is a single run, reading out the data and providing it via MQTT - including a feedback on the screen:
```
python smartmeter.py
```
