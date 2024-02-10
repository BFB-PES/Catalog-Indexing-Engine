from flask import Flask, request, jsonify
from confluent_kafka import Producer
from elasticsearch import Elasticsearch
import indexMappings
import psycopg2
import helpers
import producer

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
KAFKA_TOPIC = 'test'

postgresql_table = 'fashion'
elasticsearch_index = 'fashion_index'

# Connect to PostgreSQL
postgres_config = {
    'host': 'localhost',
    'database': 'fashion',
    'user': 'postgres',
    'password': 'postgres',
    'port': '5432'  # Default PostgreSQL port
}

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
        #TODO: Check message format
        message = data['message']

        producer.produce_api_to_kafka(KAFKA_TOPIC, KAFKA_BOOTSTRAP_SERVERS, message)

        helpers.index_postgresql_to_elasticsearch(postgresql_table, elasticsearch_index)

        return jsonify({'status': 'success', 'message': 'Message sent to Kafka topic'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/unstructured_search', methods=['GET'])
def unstructured_search():
    try:
        data = request.json
        query = data['query']
        result = helpers.run_unstructured_elasticsearch_query(elasticsearch_index, query)
        return jsonify({'status': 'success', 'message': result}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/structured_search', methods=['GET'])
# Query input format = {
#             "bool": {
#                 "must": [
#                     {
#                         "range": {
#                             "price": {
#                                 "gte": filter_map["min_price"],
#                                 "lte": filter_map["max_price"]
#                             }
#                         },
#                         "range": {
#                             "rating": {
#                                 "gte": filter_map["min_rating"]
#                             }
#                         }
#                     }
#                 ],
#                 "should": [
#                     {
#                         "match": {
#                             "seller": filter_map["seller"]
#                         }
#                     }
#                 ]
#             }
#         }
def structured_search():
    try:
        data = request.json
        query = data['query']
        result = helpers.run_structured_elasticsearch_query(elasticsearch_index, query)
        return jsonify({'status': 'success', 'message': result}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
