"""Send synthetic sensor measurements to Kafka-compatible Redpanda."""
import json
import os
import time
from confluent_kafka import Producer
from maintenance.data import generate


def main():
    p=Producer({"bootstrap.servers":os.getenv("KAFKA_BOOTSTRAP","localhost:9092"),"acks":"all"})
    for row in generate(50).drop(columns=["failure"]).to_dict("records"):
        p.produce(os.getenv("KAFKA_TOPIC","iot.sensors"),value=json.dumps(row,default=str).encode())
        p.poll(0)
        time.sleep(.1)
    if p.flush(15): raise RuntimeError("Undelivered sensor events")
    print("Published 50 synthetic readings")


if __name__=="__main__": main()
