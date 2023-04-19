import network, ujson
import time
from machine import Pin, I2C
import urequests
import usocket as socket
from umqtt.simple import MQTTClient
from umqtt.simple import MQTTException
from tmg39931 import TMG39931

# begin of establishing connection
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("LPWAN-IoT-03", "LPWAN-IoT-03-WiFi") 
while not wlan.isconnected():
    print("WIFI STATUS CONNECTED: " + str(wlan.isconnected()))        
    time.sleep_ms(500)
print(wlan.ifconfig())
SERVER_IP = "86.49.182.194"
CLIENT_ID = "IoT_03" 
ACCESS_TOKEN = "LPWAN_IoT_03"
keepalive_seconds = 60 #seconds
REMOTE_PORT = 36102
client = MQTTClient(CLIENT_ID,SERVER_IP, user=ACCESS_TOKEN, password="",keepalive=keepalive_seconds, port=REMOTE_PORT)
try:
    client.connect()
    client.subscribe(b"v1/devices/me/attributes") # check shared attributes changes
    client.subscribe(b"v1/devices/me/rpc/request/+") # check RPC requests from user
except MQTTException as mqtte:
    print("MQTTException : " + str(mqtte)  + " - " + mqtterrortable[int(str(mqtte))])
except:
    print("Other Error")
mqtt_ctr = 0
seconds_counter = 0
# end of establishing connection

# init light sensor
i2c1 = I2C(id=1, scl=Pin(3), sda=Pin(2), freq=400000)
tmg39931 = TMG39931.TMG39931(i2c1)

# inint led bar

# init sd card writing, button

# main program loop
while True:
    lum = tmg39931.readluminance()
    json_string={"ir-luminance":lum['i'],
                 'red-luminance':lum['r'],
                 'green-luminance':lum['g'],
                 'blue-luminance':lum['b']}
    print(f"Sending json message: {json_string}")
    json = ujson.dumps(json_string)
    print(json)
    client.publish(b"v1/devices/me/telemetry",json)
    time.sleep_ms(1000)
client.disconnect()
