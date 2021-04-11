# mqtt-display-control

Lets you turn the HDMI output on and off via MQTT. This is useful when using a typical PC monitor/display that doesn't support CEC commands.


`docker run -d --device=/dev/vchiq -v /opt/vc:/opt/vc:ro --restart unless-stopped mqtt-display-control`
