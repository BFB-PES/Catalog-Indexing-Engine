import csv
from confluent_kafka import Producer
import sys
import json

def produce_csv_to_kafka(csv_file, topic, bootstrap_servers):
    # Kafka producer configuration
    producer_config = {
        'bootstrap.servers': bootstrap_servers,
        'client.id': 'csv-producer',
        'queue.buffering.max.messages': 10000000,  # Adjust the buffer size as needed
        'batch.num.messages': 1000, # Adjust the batch size
         'linger.ms': 10  # Adjust the linger time in milliseconds
    }

    # Create Kafka producer
    producer = Producer(producer_config)

    # Read CSV file and produce each row to Kafka topic
    with open(csv_file, newline='') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            # Convert row to JSON string
            row_json = str(row)
            # Produce to Kafka topic without specifying a key
            producer.produce(topic, value=row_json)

    # Wait for any outstanding messages to be delivered and delivery reports received
    producer.flush()

def produce_terminal_to_kafka(topic, bootstrap_servers):
    # Kafka producer configuration
    producer_config = {
        'bootstrap.servers': bootstrap_servers,
        'client.id': 'terminal-producer',
        'queue.buffering.max.messages': 10000000,  # Adjust the buffer size as needed
        'batch.num.messages': 1000, # Adjust the batch size
        'linger.ms': 10  # Adjust the linger time in milliseconds
    }

    # Create Kafka producer
    producer = Producer(producer_config)

    # Read JSON strings from stdin and produce each one to Kafka topic
    for line in sys.stdin:
        # Parse JSON string
        try:
            row = json.loads(line)
            row_json = json.dumps(row)
            # Produce to Kafka topic without specifying a key
            producer.produce(topic, value=row_json)
        except json.JSONDecodeError:
            print(f"Invalid JSON: {line}", file=sys.stderr)
            continue

    # Wait for any outstanding messages to be delivered and delivery reports received
    producer.flush()   

# Example usage
# produce_csv_to_kafka('Fashion_dataset.csv', 'test', 'kafka-0.kafka-svc.kafka-kraft.svc.cluster.local:9092')
produce_terminal_to_kafka('test', 'kafka-0.kafka-svc.kafka-kraft.svc.cluster.local:9092')
