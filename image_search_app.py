import numpy as np
import streamlit as st

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# initialize connection to qdrant database
qd_client = QdrantClient("localhost", port=6333)

# instantiate encoder model
model = SentenceTransformer("clip-ViT-B-32")


def search_dataset(text_query):
    """
    Perform a semantic search based on the text query, in the ad dataset collection.
    :param text_query:
    :return:
    """
    results = qd_client.search(
        collection_name="ad_dataset",
        query_vector=model.encode(text_query).tolist(),
        with_payload=True,
        score_threshold=0.2
    )

    return results


def display_results(results):
    """
    Displays results of qdrant client search with streamlit.
    :param results:
    :return:
    """

    st.header('Results')
    st.write('Query found {} results  with a score >0.2 in the database...'.format(len(results)))

    if len(results) == 0:
        return

    for result in results:
        confidence_score = np.round(result.score, 3)
        st.image(result.payload['url'],
                 width=400,
                 caption='score {}'.format(confidence_score))


# streamlit page set up
st.set_page_config(page_title="Image Search Engine", page_icon="🧐", layout="wide")
st.title("Image Search Engine")

text_search = st.text_input("Search dataset", value="")

# on submitting a search
if text_search:
    query_results = search_dataset(text_search)
    display_results(query_results)
