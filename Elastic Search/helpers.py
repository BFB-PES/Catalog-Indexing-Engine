from sentence_transformers import SentenceTransformer
import os
import locale
import pickle

seller_list = {'Kanvin', 'SHEETAL Associates', 'Nimble', 'HERE&NOW', 'HRX by Hrithik Roshan', 'HELLCAT', 'urSense', 'SASSAFRAS', 'Urban Revivo', 'Vero Moda', 'DILLINGER', 'Okane', 'Difference of Opinion', 'U.S. Polo Assn.', 'ELLIS', 'Sztori', 'Sweet Dreams', 'Juniper', 'Mast & Harbour', 'ADIDAS', 'SUMAVI-FASHION', 'H&M', 'Moda Rapido', 'WEAVETECH IMPEX', 'GUTI', 'RAASSIO', 'Puma', 'NEUDIS', 'Wool Trees', 'VEIRDO', 'TAG 7', 'T-SHIRT TRUCK', 'Urbano Fashion', 'BRINNS', 'LYRA', 'BoStreet', 'MODWEE', 'Huetrap', 'Louis Philippe Sport', 'Disrupt', 'Styli', 'Frempy', 'Kook N Keech', 'DressBerry', 'Roadster', 'Bonkers Corner', 'Nautica', 'Jinfo'}

with open('seller_list.pkl', 'wb') as f:
    pickle.dump(seller_list, f)

with open('seller_list.pkl', 'rb') as f:
    seller_list = pickle.load(f)

locale.getpreferredencoding = lambda: "UTF-8"
os.environ["REPLICATE_API_TOKEN"] = "r8_1Cqldwtqw5MyUh8fI22HNJfNp2VGBkm2lImnb"

model = SentenceTransformer('all-mpnet-base-v2')

def get_description_vector(value):
    return model.encode(value)