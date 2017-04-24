# sensor-data
Sensor Data Plugin for Dreambox (Enigma2)

This plugin shows a string of sensor data permanently on the dreambox screen, similar to the permanent clock plugin. In fact, this is based on the permanent clock plugin.

The data needs to be provided through a REST interface which needs to be edited into the plugin.py file in the following line:
http://REST_SERVER:PORT/DATA_ENDPOINT

You will also need to modify the following line to suit your json structure:

"T:" + '{:02d}'.format(int(textd[0]["last_Temperature"])) + ",H:" + '{:02d}'.format(int(textd[0]["last_Humidity"])) + ",C:" + '{:04d}'.format(int(textd[0]["last_CO2"]))

I'm displaying the current temperature, humidity, and CO2 content in the room via this plugin on the TV screen.

It is a typical python plugin for dreambox. You need to place the files in the following directory:
/usr/lib/enigma2/python/Plugins/Extensions/SensorData/
In addition, also create an empty \_\_init\_\_.py file in this folder and restart the dreambox to activate the plugin via remote control under system settings.
