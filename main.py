import paho.mqtt.client as mqtt
from typing import Any, Dict
from pathlib import Path
from typing import Dict
import yaml
import sched

def mqtt_on_connect(client: mqtt.Client, userdata: Any, flags: Dict, rc: int):
    pass

def mqtt_on_message(client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage):
    pass

def heartbeat_task():
    pass

def get_config(filename: str) -> Dict:
    with open(Path(__file__).parent / filename, 'r') as file:
        try:
            cfg = yaml.safe_load(file)
            return cfg
        except yaml.YAMLError as e:
            print(e)

if __name__ == '__main__':
    config = get_config('config.yaml')
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqtt_client.on_connect = mqtt_on_connect
    mqtt_client.on_message = mqtt_on_message

    #mqtt_client.username_pw_set(credentials['username'], credentials['password'])
    mqtt_client.connect(host=config['mqtt_server'], port=config['mqtt_port'], keepalive=60)

    scheduler = sched.scheduler()
    scheduler.enter(delay=0, priority=1, action=heartbeat_task)
    
    try:
        scheduler.run()
    except KeyboardInterrupt:
        print('exiting by keyboard interrupt.')

    mqtt_client.loop_forever()