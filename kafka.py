from confluent_kafka import Producer
import socket
import json



def json_serializer(data):
    return json.dumps(data).encode('utf-8')

def send_message(values):
    conf = {'bootstrap.servers': "171.244.60.109:29092",
            'client.id': socket.gethostname()}
    producer = Producer(conf)
    producer.produce(topic = 'book-audio', key="SVC", value=json_serializer(values))
    producer.flush() 

if __name__ == "__main__":
    values = {"bookId": "34" }
    send_message(values)



