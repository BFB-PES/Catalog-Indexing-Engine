fashion_mappings = {
        "properties":{
            "id":{
                "type":"integer"
            },
            "name":{
                "type":"text"
            },
            "img":{
                "type":"keyword"
            },
            "asin":{
                "type":"text",
                "index": "false"
            },
            "price":{
                "type":"scaled_float",
                "scaling_factor": 100
            },
            "mrp":{
                "type":"scaled_float",
                "scaling_factor": 100
            },
            "rating":{
                "type":"scaled_float",
                "scaling_factor": 10
            },
            "ratingTotal":{
                "type":"integer"
            },
            "discount":{
                "type":"integer"
            },
            "seller":{
                "type":"text"
            },
            "purl":{
                "type":"keyword"
            },
            "DescriptionVector":{
                "type":"dense_vector",
                "dims": 768,
                "index":True,
                "similarity": "l2_norm"
            },
        }
    }