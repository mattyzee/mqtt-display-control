mqtt-display-control
====================

Lets you turn the Raspberry Pi HDMI output on and off via MQTT. This is useful when using a typical PC monitor/display that doesn't support CEC commands.

# Configuration
The settings to configure the MQTT broker and topic prefix are in the `config.ini` file. `config.default.ini` is provided as a starting point.

# Docker
This runs in docker and needs the following device and volume passed through.
```
docker run -d --device=/dev/vchiq -v /opt/vc:/opt/vc:ro --restart unless-stopped mqtt-display-control
```

# MQTT Topics

The bridge subscribes to the following topics:

| topic                   | body                                    | remark                                           |
|:------------------------|-----------------------------------------|--------------------------------------------------|
| `prefix`/display/cmd    | `on` / `off`                            | Turn on/off the display        .                 |

The bridge publishes to the following topics:

| topic                   | body                                    | remark                                           |
|:------------------------|-----------------------------------------|--------------------------------------------------|
| `prefix`/bridge/status  | `online` / `offline`                    | Report availability status of the bridge.        |
| `prefix`/display/status | `on` / `off`                            | Report power status of the dsiplay               |
| `prefix/pi/temp         | `number`                                | The internal temp of the pi (GPU?)               |

# Home Assistant
You can easily control the display using an MQTT switch in Home Assistant. The following example uses a topic `prefix` of `kitchen/tv`
```
switch:
  - platform: mqtt
    name: "Kitchen TV"
    command_topic: "kitchen/tv/display/cmd"
    payload_on: "on"
    payload_off: "off"
    state_topic: "kitchen/tv/display/status"
    availability_topic: "kitchen/tv/bridge/status"
```

# Acknowlegment
This is my first project using Paho and Docker on a pi. It is heavily based on `cec-mqtt-bridge` (https://github.com/michaelarnauts/cec-mqtt-bridge). I first tried using `cec-mqtt-bridge` to control the display but my display didn't support any CEC commands.  
