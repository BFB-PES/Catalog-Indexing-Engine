import os
import locale
import pickle
import replicate
from sentence_transformers import SentenceTransformer
import json
import psycopg2
import indexMappings
import Elasticsearch

query_source = ['id', 'name', 'asin', 'price', 'mrp', 'rating', 'ratingTotal', 'discount', 'seller']

with open('seller_list.pkl', 'wb') as f:
    pickle.dump(indexMappings.seller_list, f)

locale.getpreferredencoding = lambda: "UTF-8"
os.environ["REPLICATE_API_TOKEN"] = "r8_1Cqldwtqw5MyUh8fI22HNJfNp2VGBkm2lImnb"

model = SentenceTransformer('all-mpnet-base-v2')

# Connect to Elasticsearch
es = Elasticsearch(['http://localhost:9200'])
    #basic_auth=('elastic', 'NSFO6Y0TTCi7PhlaIQu2'),
    #verify_certs=False,
    #request_timeout=300) #might need to inc timeout acc

def get_description_vector(value):
    return model.encode(value)

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

    # Connect to PostgreSQL
    postgres_config = {
        'host': 'localhost',
        'database': 'fashion',
        'user': 'postgres',
        'password': 'postgres',
        'port': '5432'  # Default PostgreSQL port
    }
    # Connect to postgres
    pg_conn = psycopg2.connect(**postgres_config)
    pg_cursor = pg_conn.cursor()

    if not es.indices.exists(index=index_name):

        es.indices.create(index=index_name, mappings=indexMappings.fashion_mappings)
        last_indexed_id = 0
        #index all the records
        pg_cursor.execute(f"SELECT * FROM fashion1")
        columns = [desc[0] for desc in pg_cursor.description]
        rows = pg_cursor.fetchall()

        # Index data in Elasticsearch
        for row in rows:
            doc = dict(zip(columns, row))
            doc["DescriptionVector"] = get_description_vector(doc["name"])
            # es.index(index=index_name, body=doc)
            es.index(index=index_name, document=doc, id=doc["id"])

    else :
        last_indexed_id = get_last_indexed_id(index_name)
        # If the index exists, retrieve the ID of the last indexed record
        pg_cursor.execute(f"SELECT * FROM {table_name} WHERE id > {last_indexed_id}")
        columns = [desc[0] for desc in pg_cursor.description]
        rows = pg_cursor.fetchall()

        # Index new records in Elasticsearch
        for row in rows:
            doc = dict(zip(columns, row))
            doc["DescriptionVector"] = get_description_vector(doc["name"])
            with open('seller_list.pkl', 'rb') as f:
                seller_list = pickle.load(f)
                if doc["seller"] not in seller_list:
                    seller_list.add(doc["seller"])
            try:
                es.index(index=index_name, document=doc, id=doc["id"])
            except Exception as e:
                print(e)

    print("Index count: ", es.count(index=index_name))

def run_unstructured_elasticsearch_query(index_name, query):
    # Run Elasticsearch query

    with open('seller_list.pkl', 'rb') as f:
        seller_list = pickle.load(f)

        my_prompt = f"""I have data in elastic search of all clothing products with their description, seller, price and the rating they have.
sellers are {seller_list}
price can be anything from 0 to 7000
rating can be anything from 0 to 5
based on user's search query. give me json output as follows
{{
"seller": "it should be what users want. give Not-Mentioned if user did not explicitly mentioned the seller brand in query. If the seller mentioned by user is not present in above color list, give Not-Found",
"max_price":
"min_price":
"min_rating":
}}

users query : {query}
"""

        # result = es.search(index=index_name, body=query_body)
        event = replicate.run(
            "meta/llama-2-70b-chat",
            input={
                "debug": False,
                "top_k": 50,
                "top_p": 1,
                "prompt": my_prompt,
                "temperature": 0.5,
                "system_prompt": "You are a helpful assistant designed to output only in JSON format. No other text or explanation.",
                "max_new_tokens": 500,
                "min_new_tokens": -1
            },
        )
        response = ""
        for text in event:
            response+=text
        print(response)
        filter_map = json.loads(response)

        # Apply filter on semantic search results
        q1 = {
            "knn": {
                "field": "DescriptionVector",
                "query_vector": get_description_vector(query),
                "k": 10,
                "num_candidates": 10000
            },
            "_source": query_source
        }

        filter_query = {
            "bool": {
                "must": [
                    {
                        "range": {
                            "price": {
                                "gte": filter_map["min_price"],
                                "lte": filter_map["max_price"]
                            }
                        },
                        "range": {
                            "rating": {
                                "gte": filter_map["min_rating"]
                            }
                        }
                    }
                ],
                "should": [
                    {
                        "match": {
                            "seller": filter_map["seller"]
                        }
                    }
                ]
            }
        }

        res = es.knn_search(index=index_name,  # change index name here.
                        body=q1,
                        request_timeout=5000,
                        filter=filter_query)

        return res["hits"]["hits"]

def run_structured_elasticsearch_query(index_name, query):
    # Run Elasticsearch query

    res = es.search(index=index_name, body=query)
    return res["hits"]["hits"]