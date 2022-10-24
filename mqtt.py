import paho.mqtt.client as paho

def _on_publish(client,userdata,result):
    pass

def connect(broker):
    port=1883
    client = paho.Client("power")
    client.on_publish = _on_publish
    client.connect(broker, port)
    client.loop_start()
    return client

def publish(client, topic, data):
    return client.publish(topic, data)  