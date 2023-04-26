import network, ujson
import time
from machine import Pin, I2C
import urequests
import usocket as socket
from umqtt.simple import MQTTClient
from umqtt.simple import MQTTException
from tmg39931 import TMG39931
from ledbar.my9221 import MY9221
from sdcard import SDCard
import uos


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
i2c1 = I2C(id=0, scl=Pin(1), sda=Pin(0), freq=400000)
print(i2c1.scan())
tmg39931 = TMG39931.TMG39931(i2c1)

# inint led bar
ledbar = MY9221(di=Pin(27), dcki=Pin(26))

#init button + interrupt

def button_pressed(change):
    lum = tmg39931.readluminance()
    luminance = lum['r'] + lum['g'] + lum['b']
    json_string={"ir-luminance":lum['i'],
                     'red-luminance':lum['r'],
                     'green-luminance':lum['g'],
                     'blue-luminance':lum['b'],
                     'combined-luminance':luminance}
    print(f"Sending json message from interrupt: {json_string}")
    json = ujson.dumps(json_string)
    luminance = 0
    client.publish(b"v1/devices/me/telemetry",json)
    spi = machine.SPI(1,
                  baudrate=1000000,
                  polarity=0,
                  phase=0,
                  bits=8,
                  firstbit=machine.SPI.MSB,
                  sck=machine.Pin(10),
                  mosi=machine.Pin(11),
                  miso=machine.Pin(12))
    cs = Pin(15)
    sd = SDCard(spi, cs)
    vfs = uos.VfsFat(sd)
    uos.mount(vfs, '/sd')
    with open('/sd/light_intensity_output.txt', 'a') as file:
        file.write(json_string + '\n')
        
button = Pin(20, Pin.IN)
button.irq(handler = button_pressed, trigger = Pin.IRQ_FALLING)

sent_flag = 0
# main program loop
while True:
    lum = tmg39931.readluminance()
    luminance = lum['r'] + lum['g'] + lum['b']
    ledbar.level(int(luminance/500 + 1))
    time.sleep_ms(10)
    sent_flag += 10
    if sent_flag == 10000:
        json_string={"ir-luminance":lum['i'],
                     'red-luminance':lum['r'],
                     'green-luminance':lum['g'],
                     'blue-luminance':lum['b'],
                     'combined-luminance':luminance}
        print(f"Sending json message: {json_string}")
        json = ujson.dumps(json_string)
        client.publish(b"v1/devices/me/telemetry",json)
        sent_flag = 0
   
client.disconnect()
