import network, ujson
import time
from machine import Pin
import urequests
import usocket as socket
from umqtt.simple import MQTTClient
from umqtt.simple import MQTTException
import TMG39931

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
light_sensor = TMG39931.TMG39931()
while True:
    light_sensor.readLuminance()
    time.sleep(1)
# inint led bar

# init sd card writing, button

# main program loop
while True:
    json_string={"light-intensity":20}
    print(f"Sending json message: {json_string}")
    json = ujson.dumps(json_string)
    print(json)
    client.publish(b"v1/devices/me/telemetry",json)
    time.sleep_ms(1000)
client.disconnect()
