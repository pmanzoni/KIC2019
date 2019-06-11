import binascii
import machine
import micropython
import pycom
import socket
import struct
import sys
import time
import config

from network import LoRa
from pysense import Pysense
from SI7006A20 import SI7006A20 		# Humidity and Temperature Sensor
from LTR329ALS01 import LTR329ALS01 	# Digital Ambient Light Sensor
from raw2lux import raw2Lux             # ... additional library for the light sensor

RED = 0xFF0000
YELLOW = 0xFFFF33
GREEN = 0x007F00
OFF = 0x000000
def flash_led_to(color=GREEN, t1=1):
    pycom.rgbled(color)
    time.sleep(t1)
    pycom.rgbled(OFF)



def join_lora(force_join = False):
    '''Joining The Things Network '''
    print('Joining TTN')

    # restore previous state
    if not force_join:
        lora.nvram_restore()

    if not lora.has_joined() or force_join == True:

        # create an OTA authentication params
        dev_eui = binascii.unhexlify('70B3D54996F5FB12')
        app_eui = binascii.unhexlify('70B3D57ED001D95F')
        app_key = binascii.unhexlify('B074C5875EB3D8E92FA650576035D53F')


        #remove all channels
        for channel in range(0, 10):
            lora.remove_channel(channel)

        # set the 3 default channels to the same frequency (must be before sending the OTAA join request)
        lora.add_channel(0, frequency=config.LORA_FREQUENCY, dr_min=0, dr_max=5)
        lora.add_channel(1, frequency=config.LORA_FREQUENCY, dr_min=0, dr_max=5)
        lora.add_channel(2, frequency=config.LORA_FREQUENCY, dr_min=0, dr_max=5)
        #lora.remove_channel(3)
        #lora.remove_channel(4)
        #lora.remove_channel(5)
        #lora.remove_channel(6)

        # join a network using OTAA if not previously done
        lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)

        # wait until the module has joined the network
        while not lora.has_joined():
            time.sleep(2.5)

        # saving the state
        #lora.nvram_save()

        # returning whether the join was successful
        if lora.has_joined():
            flash_led_to(GREEN)
            print('LoRa Joined')
            return True
        else:
            flash_led_to(RED)
            print('LoRa Not Joined')
            return False

    else:
        return True

pycom.heartbeat(False) # Disable the heartbeat LED

# Getting the LoRa MAC
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.AS923)
print("Device LoRa MAC:", binascii.hexlify(lora.mac()))

flash_led_to(YELLOW)
# joining TTN
join_lora(True)

py = Pysense()
tempHum = SI7006A20(py)
ambientLight = LTR329ALS01(py)

# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

#    s.setsockopt(socket.SOL_LORA, socket.SO_DR, 0)
s.setsockopt(socket.SOL_LORA, socket.SO_DR, config.LORA_NODE_DR)

s.setblocking(False)

while True:


    temperature = tempHum.temp()
    humidity = tempHum.humidity()
    luxval = raw2Lux(ambientLight.lux())

    print("Read sensors: temp. {} hum. {} lux: {}".format(temperature, humidity, luxval))
    # Packing sensor data as byte sequence using 'struct'
    # Data is represented as 3 float values, each of 4 bytes, byte orde 'big-endian'
    # for more infos: https://docs.python.org/3.6/library/struct.html
#    payload = struct.pack(">fff", temperature, humidity, luxval)

#    payload = struct.pack(">ff", temperature,luxval)
    payload = struct.pack(">ff", temperature,luxval)
    print(payload)
    try:
        s.send(payload)
    except:
        pass
    flash_led_to(GREEN)

    time.sleep(5)
