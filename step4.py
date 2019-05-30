import random
import time
import json


import paho.mqtt.client as mqtt

THE_BROKER = "things.ubidots.com"
CLIENT_ID = ""
UBI_USERNAME = "VOID"
UBI_PASSWD = ""
TOPIC = "/v1.6/devices/"
DEVICE_LABEL = "VOID"
VARIABLE_LABEL = "VOID"

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected to ", client._host, "port: ", client._port)
    print("Flags: ", flags, "returned code: ", rc)

# The callback for when a message is published.
def on_publish(client, userdata, mid):
    print("sipub: msg published (mid={})".format(mid))


client = mqtt.Client(client_id=CLIENT_ID, 
                     clean_session=True, 
                     userdata=None, 
                     protocol=mqtt.MQTTv311, 
                     transport="tcp")

client.on_connect = on_connect
client.on_publish = on_publish

client.username_pw_set(UBI_USERNAME, password=UBI_PASSWD)
client.connect(THE_BROKER, port=1883, keepalive=60)

client.loop_start()

while True:

    # Simulates sensor values
    sensor_value = random.random() * 100

    # Builds Payload and topíc
    payload = json.dumps({VARIABLE_LABEL: sensor_value})
    topic = "{}{}".format(TOPIC, DEVICE_LABEL)

    client.publish(topic, payload, qos=1, retain=False)

    time.sleep(5)

client.loop_stop()
