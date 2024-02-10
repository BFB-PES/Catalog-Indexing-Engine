from flask import Flask, request, jsonify
from confluent_kafka import Producer
import psycopg2
from elasticsearch import Elasticsearch

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
KAFKA_TOPIC = 'test'

# Connect to PostgreSQL
postgres_config = {
    'host': 'localhost',
    'database': 'fashion',
    'user': 'postgres',
    'password': 'postgres',
    'port': '5432'  # Default PostgreSQL port
}



# Connect to Elasticsearch
es = Elasticsearch(['http://localhost:9200'])
    #basic_auth=('elastic', 'NSFO6Y0TTCi7PhlaIQu2'),
    #verify_certs=False, 
    #request_timeout=300) #might need to inc timeout acc 

producer_config = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    'client.id': 'terminal-producer',
    'queue.buffering.max.messages': 10000000,  # Adjust the buffer size as needed
    'batch.num.messages': 1000, # Adjust the batch size
    'linger.ms': 10  # Adjust the linger time in milliseconds
}

# Create Kafka producer
producer = Producer(producer_config)

@app.route('/produce', methods=['POST'])
def produce_message():
    try:
        data = request.json
        message = data['message']
        producer.produce(KAFKA_TOPIC, value=message)
        producer.flush()
        postgresql_table = 'fashion'
        elasticsearch_index = 'fashion_index'
        index_postgresql_to_elasticsearch(postgresql_table, elasticsearch_index)
        return jsonify({'status': 'success', 'message': 'Message sent to Kafka topic'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


def index_postgresql_to_elasticsearch(table_name, index_name):
    # Connect to postgres
    pg_conn = psycopg2.connect(**postgres_config)
    pg_cursor = pg_conn.cursor()
    # Retrieve data from PostgreSQL
    pg_cursor.execute(f"SELECT * FROM fashion1")    #1000 records
    columns = [desc[0] for desc in pg_cursor.description]
    rows = pg_cursor.fetchall()

    # Index data in Elasticsearch
    for row in rows:
        #print(row)
        doc = dict(zip(columns, row))
        es.index(index=index_name, body=doc)
    pg_cursor.close()
    pg_conn.close()
    print("Done")

@app.route('/search', methods=['GET'])
def produce_message():

    # please write the search data code

if __name__ == '__main__':
    app.run(debug=True)
