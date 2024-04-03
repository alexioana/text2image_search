import numpy as np
import streamlit as st

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# initialize connection to qdrant database
qd_client = QdrantClient("localhost", port=6333)

# instantiate encoder model
model = SentenceTransformer("clip-ViT-B-32")


def search_dataset(text_query: str, results_limit: int, confidence_threshold: float):
    """
    Perform a semantic search based on the text query, in the ad dataset collection.
    :param text_query: string representing a textual query
    :return: a list of result items as returned from qdrant_client.search
    """
    results = qd_client.search(
        collection_name="ad_dataset",
        query_vector=model.encode(text_query).tolist(),
        with_payload=True,
        limit=results_limit,
        score_threshold=confidence_threshold
    )

    return results


def display_results(results):
    """
    Displays results of qdrant client search with streamlit.
    """

    st.header('Results')
    st.write('Query found {} results in the database...'.format(len(results)))

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

# form to submit a query
with st.form("text2image_search"):
    text_search = st.text_input("Search dataset", value="")

    # add sliders for control over score and results limit in one row.
    col1, col2 = st.columns(2)
    limit_slider = col1.slider(label='number of results', min_value=4, max_value=50, value=4)
    confidence_threshold = col2.slider(label='score threshold', min_value=0.0, max_value=1.0, value=0.2)

    # on submitting a search
    submit_search = st.form_submit_button("🔎")

    if submit_search:
        query_results = search_dataset(text_search, limit_slider, confidence_threshold)
        display_results(query_results)
