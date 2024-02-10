import json
import psycopg2
from confluent_kafka import Consumer, KafkaError
# import time

# time.sleep(10)

def consume_and_write_to_postgres(topic, bootstrap_servers, postgres_config):
    # Kafka consumer configuration
    consumer_config = {
        'bootstrap.servers': bootstrap_servers,
        'group.id': 'csv-consumer',
        'auto.offset.reset': 'earliest'
    }

    # Set up PostgreSQL connection
    conn = psycopg2.connect(**postgres_config)
    cursor = conn.cursor()

    # Create Kafka consumer
    consumer = Consumer(consumer_config)

    # Subscribe to Kafka topic
    consumer.subscribe([topic])

    # Consume and write data to PostgreSQL
    while True:
        msg = consumer.poll(timeout=1000)  # Adjust timeout as needed
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(msg.error())
                break
        
        # Process the received message and write to PostgreSQL
        value = msg.value().decode('utf8').replace("'", '"')
        
        
        try:
            row_dict = json.loads(value)
            # Example: Insert data into PostgreSQL
            insert_query = "INSERT INTO fashion (id, name, price, mrp, rating, ratingTotal, discount, seller, color, Sku, in_stock) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(insert_query, (int(row_dict['id']), row_dict['name'], float(row_dict['price']), float(row_dict['mrp']), float(row_dict['rating']), float(row_dict['ratingTotal']), int(row_dict['discount']), row_dict['seller'], row_dict['color'], int(row_dict['Sku']), int(row_dict['in_stock'])))
        except:
            continue
        conn.commit()
        
    

    # Clean up
    cursor.close()
    conn.close()


postgres_config = {
    'host': 'postgres',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'postgres',
    'port': '5432'  # Default PostgreSQL port
}
# Example usage
consume_and_write_to_postgres('test', 'kafka-0.kafka-svc.kafka-kraft.svc.cluster.local:9092', postgres_config)
