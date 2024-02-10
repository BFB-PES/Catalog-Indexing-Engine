import csv
from confluent_kafka import Producer
import sys
import json

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
#produce_csv_to_kafka('Datasets/Fashion_dataset.csv', 'BFB4', 'localhost:9092')
produce_terminal_to_kafka('BFB4', 'localhost:9092')