"""
MQTT sensor:  publish the Pico Pi Lights device on HASS
Just Simple button at present 
"""
from time import sleep
from umqtt.simple import MQTTClient
from machine import Pin
import json
from secrets import mqtt
from neopixel import Neopixel

class PL2MQTT_Light:
    def __init__(self, device_name, uid):
        self.dev_name = device_name + '_' + uid
        print("Creating FP2MQTT device class for device_name and uid: ", self.dev_name)
        self.device_cfg = {
                    "identifiers": self.dev_name,
                    "name": "Pi Lights",
                    "model": "RPi Pico-W",
                    "sw": "0.1",
                    "manufacturer": "Robby Saunders" 
                    }
        base_topic = "light/" + self.dev_name
        self.discovery_topic = "homeassistant/" + base_topic + "/config"
        self.availability_topic = base_topic + "/available"
        self.state_topic = base_topic + "/state"
        self.command_topic = base_topic + "/set"
        self.rgb_state_topic = base_topic + "/state/rgb"
        self.rgb_command_topic = base_topic + "/set/rgb"
        self.np = Neopixel(50,0,0)
        self.last_rgb = (255,48,0)
                
        self.client = MQTTClient(self.dev_name, mqtt['server'])
        
        def sub_cb(topic, msg):
            print("***Topic/Message received:  ",topic, msg)
            tpc_str = topic.decode("utf-8")            
            if tpc_str == self.command_topic:
                if(msg==b'ON'):
                    print("Turn ON")   # Turn on
                    self.np.fill((self.last_rgb))
                    self.np.show()
                else:
                    print("Turn OFF")   # Turn off
                    self.np.clear()
                    self.np.show()
                self.publish_light_state()
            elif tpc_str == self.rgb_command_topic:
                print("Set RGB using:", msg)
                rgb = msg.decode('utf-8').split(',')
                self.last_rgb=(int(rgb[0]), int(rgb[1]), int(rgb[2]))
                self.np.fill(self.last_rgb)
                self.np.show()
            else:
                print("Command not actioned - don't know what to do")

        self.client.set_callback(sub_cb)
        self.client.set_last_will(self.availability_topic, 'offline')

        # Conenct to server
        print('MQTT connect to server result {}', self.client.connect())
        print("Subscribing for: ", self.command_topic)
        self.client.subscribe(self.command_topic+"/#")

    def disconnect(self):
        print("Disconnecting and publishing 'offline' to availablity topic...")
        self.client.publish(self.availability_topic, 'offline')
        self.client.disconnect()

    def reconnect_client(self):
        try:
            self.client.connect()
        except OSError as e:
            raise RuntimeError('MQTT failed to re-connect to server')
        print('MQTT re-connected to server')

        print("Re-subscribing for: ", self.command_topic)
        self.client.subscribe(self.command_topic)
 
    def create_light(self, name):
        payload = { "name": name,
            "state_topic": self.state_topic,
            "command_topic": self.command_topic,
            "rgb_state_topic": self.rgb_state_topic,
            "rgb_command_topic": self.rgb_command_topic,
            "availability_topic": self.availability_topic,
            #"rgb_value_template": "{{ value_json.rgb | join(',') }}",
            "icon": "mdi:string-lights",
            "unique_id": self.dev_name,
            "device": self.device_cfg,
            }
        print(json.dumps(payload))
        self.client.publish(self.discovery_topic, bytes(json.dumps(payload), 'utf-8'))
        self.client.publish(self.availability_topic, 'online')
        self.publish_light_state()

    def publish_light_state(self):
        onoff_state = 'OFF' if self.np.get_pixel(0)==(0,0,0) else 'ON'
        print("{}  {}".format(self.state_topic, onoff_state))
        self.client.publish(self.state_topic, onoff_state )
        self.client.publish(self.availability_topic, 'online')
