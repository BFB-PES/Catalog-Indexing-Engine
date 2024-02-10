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

seller_list = {'Kanvin', 'SHEETAL Associates', 'Nimble', 'HERE&NOW', 'HRX by Hrithik Roshan', 'HELLCAT', 'urSense', 'SASSAFRAS', 'Urban Revivo', 'Vero Moda', 'DILLINGER', 'Okane', 'Difference of Opinion', 'U.S. Polo Assn.', 'ELLIS', 'Sztori', 'Sweet Dreams', 'Juniper', 'Mast & Harbour', 'ADIDAS', 'SUMAVI-FASHION', 'H&M', 'Moda Rapido', 'WEAVETECH IMPEX', 'GUTI', 'RAASSIO', 'Puma', 'NEUDIS', 'Wool Trees', 'VEIRDO', 'TAG 7', 'T-SHIRT TRUCK', 'Urbano Fashion', 'BRINNS', 'LYRA', 'BoStreet', 'MODWEE', 'Huetrap', 'Louis Philippe Sport', 'Disrupt', 'Styli', 'Frempy', 'Kook N Keech', 'DressBerry', 'Roadster', 'Bonkers Corner', 'Nautica', 'Jinfo'}