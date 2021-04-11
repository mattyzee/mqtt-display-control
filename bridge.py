#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import subprocess
import time
import re
import configparser as ConfigParser
import threading
import os

# Default configuration
config = {
    'mqtt': {
        'broker': 'localhost',
        'devicename': 'display-power-mqtt',
        'port': 1883,
        'prefix': 'media',
        'user': os.environ.get('MQTT_USER'),
        'password': os.environ.get('MQTT_PASSWORD'),
        'tls': 0,
    }
}


def mqtt_on_connect(client, userdata, flags, rc):
    """@type client: paho.mqtt.client """

    print("Connection returned result: " + str(rc))

    # Subscribe to display command
    client.subscribe([
        (config['mqtt']['prefix'] + '/display/cmd', 0),
    ])
    
    # Publish birth message
    client.publish(config['mqtt']['prefix'] + '/bridge/status', 'online', qos=1, retain=True)


def mqtt_on_message(client, userdata, message):
    """@type client: paho.mqtt.client """

    try:

        # Decode topic
        cmd = message.topic.replace(config['mqtt']['prefix'], '').strip('/')
        print("Command received: %s (%s)" % (cmd, message.payload))

        split = cmd.split('/')

        if split[0] == 'display':

            if split[1] == 'cmd':

                action = message.payload.decode()

                if action == 'on':
                    os.system("/opt/vc/bin/vcgencmd display_power 1")
                    mqtt_send(config['mqtt']['prefix'] + '/display/status', 'on')
                    return

                if action == 'off':
                    os.system("/opt/vc/bin/vcgencmd display_power 0")
                    mqtt_send(config['mqtt']['prefix'] + '/display/status', 'off')
                    return

                raise Exception("Unknown command (%s)" % action)

    except Exception as e:
        print("Error during processing of message: ", message.topic, message.payload, str(e))


def mqtt_send(topic, value, retain=False):
    mqtt_client.publish(topic, value, retain=retain)

def cleanup():
    mqtt_client.loop_stop()
    mqtt_client.publish(config['mqtt']['prefix'] + '/bridge/status', 'offline', qos=1, retain=True)
    mqtt_client.disconnect()
    
def display_refresh():
    # check display status
    t = subprocess.run(["/opt/vc/bin/vcgencmd", "measure_temp"], capture_output=True, text=True).stdout
    m = re.search('temp=(\d+.?\d?)', t)
    if m:
        mqtt_send(config['mqtt']['prefix'] + '/pi/temp', m.group(1))


try:
    ### Parse config ###
    try:
        Config = ConfigParser.SafeConfigParser()
        if Config.read("config.ini"):

            # Load all sections and overwrite default configuration
            for section in Config.sections():
                config[section].update(dict(Config.items(section)))

        # Environment variables
        for section in config:
            for key, value in config[section].items():
                env = os.getenv(section.upper() + '_' + key.upper());
                if env:
                    config[section][key] = type(value)(env)
        
    except Exception as e:
        print("ERROR: Could not configure:", str(e))
        exit(1)

    ### Setup MQTT ###
    print("Initialising MQTT...")
    mqtt_client = mqtt.Client(config['mqtt']['devicename'])
    mqtt_client.on_connect = mqtt_on_connect
    mqtt_client.on_message = mqtt_on_message
    if config['mqtt']['user']:
        mqtt_client.username_pw_set(config['mqtt']['user'], password=config['mqtt']['password']);
    if int(config['mqtt']['tls']) == 1:
        mqtt_client.tls_set();
    mqtt_client.will_set(config['mqtt']['prefix'] + '/bridge/status', 'offline', qos=1, retain=True)
    mqtt_client.connect(config['mqtt']['broker'], int(config['mqtt']['port']), 60)
    mqtt_client.loop_start()

    print("Starting main loop...")
    while True:
        display_refresh()
        time.sleep(10)

except KeyboardInterrupt:
    cleanup()

except RuntimeError:
    cleanup()