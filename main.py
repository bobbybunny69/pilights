from secrets import wifi
import network
import machine
from umqtt.simple import MQTTClient
from pl2mqtt import PL2MQTT_Light
import time
from random import randint as rand

# Fill in your WiFi network name (ssid) and password here:
wifi_ssid = wifi['ssid']
wifi_password = wifi['pw']

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(wifi_ssid, wifi_password)
while wlan.isconnected() == False:
    print('Waiting for connection...')
    time.sleep(1)
print("Connected to Wi-Fi. My IP Address:", wlan.ifconfig()[0])

# Initialize our MQTTClient and connect to the MQTT server
uid = machine.unique_id()
uid = '{:02x}{:02x}'.format(uid[2],uid[3])
pi_lights_mqtt = PL2MQTT_Light("pi_lights", uid)
pi_lights_mqtt.create_light("Pi Lights")

# Loop checking for messages
try:
    while True:
        pi_lights_mqtt.client.wait_msg()
finally:
    print("Finished.")
    pi_lights_mqtt.np.clear()
    pi_lights_mqtt.np.show()
    pi_lights_mqtt.disconnect()
