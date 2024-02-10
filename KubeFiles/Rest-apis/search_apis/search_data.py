import psycopg2
from elasticsearch import Elasticsearch
import replicate
import json
import helpers
import pickle

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

query_source = ['id', 'name', 'asin', 'price', 'mrp', 'rating', 'ratingTotal', 'discount', 'seller']


def connect_to_postgresql():
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
    return pg_conn, pg_cursor

def connect_to_elasticsearch():
    # Connect to Elasticsearch
    es = Elasticsearch(['http://localhost:9200'],
    #basic_auth=('elastic', 'NSFO6Y0TTCi7PhlaIQu2'),
    verify_certs=False)
    return es

def run_elasticsearch_query(es, index_name, input_keyword):
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

users query : {input_keyword}
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
                "query_vector": helpers.get_description_vector(input_keyword),
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

def main():
    try:
        # Connect to PostgreSQL
        pg_conn, pg_cursor = connect_to_postgresql()

        # Connect to Elasticsearch
        es = connect_to_elasticsearch()

        # Define Elasticsearch query
        index_name = 'fashion_index_1'
#         query_body = {
#             "query": {
#                 "bool": {
#                     "must": [
#                         {"match": {"seller": "Apraa & Parma"}},
#                         {"match": {"color": "Rose"}}
#                     ]
#                 }
#             },
#             "size": 100
# }
        input_keyword = "Roadster Cotton Tshirt under 900 rated above 3.6"



        # Run Elasticsearch query
        result = run_elasticsearch_query(es, index_name, input_keyword)

        # Process and print the result
        print("Elasticsearch Query Result:")
        print(result)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close connections
        if pg_cursor:
            pg_cursor.close()
        if pg_conn:
            pg_conn.close()

if __name__ == '__main__':
    main()