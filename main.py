import paho.mqtt.client as mqtt
from typing import Any, Dict
from pathlib import Path
from typing import Dict
import yaml
import sched
import time
from threading import Thread

def get_config(filename: str) -> Dict:
    with open(Path(__file__).parent / filename, 'r') as file:
        try:
            cfg = yaml.safe_load(file)
            return cfg
        except yaml.YAMLError as e:
            print(e)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
scheduler = sched.scheduler()
start_time = time.time()
config = get_config('config.yaml')
plug_on_topic = config['plug_on_topic']
plug_on_payload = config['plug_on_payload']
plug_off_topic = config['plug_off_topic']
plug_off_payload = config['plug_off_payload']
odin2_soc_topic = config['odin2_soc_topic']
on_time_topic = config['on_time_topic']
activation_soc = config['activation_soc']
deactivation_soc = config['deactivation_soc']

def turn_on_plug():
    print("Turned plug ON")
    client.publish(topic=plug_on_topic, payload=plug_on_payload)
    
def turn_off_plug():
    print("Turned plug OFF")
    client.publish(topic=plug_off_topic, payload=plug_off_payload)

def mqtt_on_connect(client: mqtt.Client, userdata, flags, reason_code, properties):
    print("Subscribed to " + odin2_soc_topic)
    client.subscribe(odin2_soc_topic)

def mqtt_on_message(client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage):
    payload = msg.payload.decode()
    print("Got message: " + msg.topic + ": " + payload)
    soc = int(payload)
    if soc >= deactivation_soc:
        turn_off_plug()
    elif soc <= activation_soc:
        turn_on_plug()
    
run_mqtt = True     
def mqtt_loop():
    while run_mqtt:
        client.loop() 

def heartbeat_task():
    on_time = int(time.time() - start_time)
    client.publish(topic=on_time_topic, payload=on_time)
    scheduler.enter(delay=3, priority=1, action=heartbeat_task)

if __name__ == '__main__':
    client.on_connect = mqtt_on_connect
    client.on_message = mqtt_on_message

    #mqtt_client.username_pw_set(credentials['username'], credentials['password'])
    client.connect(host=config['mqtt_server'], port=config['mqtt_port'], keepalive=60)
    
    
    mqtt_thread = Thread(target=mqtt_loop)
    mqtt_thread.start()

    scheduler.enter(delay=0, priority=1, action=heartbeat_task)
    
    try:
        scheduler.run()
    except KeyboardInterrupt:
        print('exiting by keyboard interrupt.')
        run_mqtt = False