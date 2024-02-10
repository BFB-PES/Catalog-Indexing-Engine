#elastic search with last index data
import pickle
import psycopg2
from elasticsearch import Elasticsearch
import time
import helpers
import indexMappings

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Connect to PostgreSQL
postgres_config = {
    'host': 'localhost',
    'database': 'fashion',
    'user': 'postgres',
    'password': 'postgres',
    'port': '5432'  # Default PostgreSQL port
}

pg_conn = psycopg2.connect(**postgres_config)
pg_cursor = pg_conn.cursor()

# Connect to Elasticsearch
es = Elasticsearch(['http://localhost:9200'])

def get_last_indexed_id(index_name):
    # Query Elasticsearch to get the last record
    body = {
        "size": 1,
        "sort": [
            {
                "id": {
                    "order": "desc"
                }
            }
        ]
    }
    res = es.search(index=index_name, body=body)

    # Extract the ID of the last record
    last_indexed_id = res['hits']['hits'][0]['_source']['id']

    return last_indexed_id


def index_postgresql_to_elasticsearch(table_name, index_name):
    # Check if the index exists
    if not es.indices.exists(index=index_name):
        # If the index doesn't exist, create it
        es.indices.create(index=index_name, mappings=indexMappings.fashion_mappings)
        print("Index created.")
        last_indexed_id = 0
        #index all the records
        pg_cursor.execute(f"SELECT * FROM fashion1")
        columns = [desc[0] for desc in pg_cursor.description]
        rows = pg_cursor.fetchall()

        # Index data in Elasticsearch
        limit = 10000
        i = 0
        for row in rows:
            if i<limit:
                doc = dict(zip(columns, row))
                es.index(index=index_name, body=doc)
                i = i + 1

    else:
        # If the index exists, retrieve the ID of the last indexed record
        last_indexed_id = get_last_indexed_id(index_name)

        # Retrieve new records from PostgreSQL
        pg_cursor.execute(f"SELECT * FROM {table_name} WHERE id > {last_indexed_id}")
        columns = [desc[0] for desc in pg_cursor.description]
        rows = pg_cursor.fetchall()
        
        # Index new records in Elasticsearch
        #limit = 10000
        #i = 0 #counter
        for row in rows:
            #if i<limit:
            doc = dict(zip(columns, row))
            doc["DescriptionVector"] = helpers.get_description_vector(doc["name"])
            with open('seller_list.pkl', 'rb') as f:
                seller_list = pickle.load(f)
                if doc["seller"] not in seller_list:
                    seller_list.add(doc["seller"])
            try:
                es.index(index = index_name, document=doc, id=doc["id"])
            except Exception as e:
                print(e)
            #i = i+1
            
        
    print("Index count: ", es.count(index = index_name))





if __name__ == '__main__':
    print("Started")
    # Specify the PostgreSQL table name and Elasticsearch index name
    postgresql_table = 'fashion0'
    elasticsearch_index = 'fashion_v2'

    start_time = time.time()
    #if es.indices.exists(index=elasticsearch_index):
    print(f"printing index name: {elasticsearch_index}")
    index_postgresql_to_elasticsearch(postgresql_table, elasticsearch_index)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"indexing took {elapsed_time} seconds to run.")

    # Close connections
    pg_cursor.close()
    pg_conn.close()
    print("Done")