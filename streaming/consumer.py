"""Simple at-least-once sensor scoring consumer."""
import json
import os
import pandas as pd
from confluent_kafka import Consumer,KafkaException
from api.main import load_model
from maintenance.data import FEATURES


def main():
    c=Consumer({"bootstrap.servers":os.getenv("KAFKA_BOOTSTRAP","localhost:9092"),
        "group.id":"iot-risk-score","auto.offset.reset":"earliest","enable.auto.commit":False})
    c.subscribe([os.getenv("KAFKA_TOPIC","iot.sensors")])
    model=load_model()
    print("Streaming sensor scores; Ctrl+C to exit")
    try:
        while True:
            msg=c.poll(1)
            if msg is None:continue
            if msg.error():raise KafkaException(msg.error())
            try:
                row=json.loads(msg.value())
                probability=float(model.predict_proba(pd.DataFrame([row])[FEATURES])[0,1])
                print(json.dumps({"partition":msg.partition(),"offset":msg.offset(),"risk":round(probability,4)}))
            except (ValueError,TypeError,KeyError) as exc:
                print("Rejected invalid event:",type(exc).__name__)
            c.commit(msg,asynchronous=False)
    except KeyboardInterrupt:pass
    finally:c.close()


if __name__=="__main__":main()
