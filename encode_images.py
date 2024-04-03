from sentence_transformers import SentenceTransformer

from qdrant_client.http import models as rest
from qdrant_client import QdrantClient
from tqdm import tqdm
from PIL import Image

import pandas as pd
import numpy as np
import uuid
import os


def generate_folder_dataset_metadata(path_to_dataset_dir):
    """
    Abstract function to generate the rows of a dataframe describing images in a folder.
    Each row of the dataset will contain a unique id, the path to the image and the image name.

    :param path_to_dataset_dir: path to a folder containing the images in a dataset.
    :return: a list of dictionaries representing each row in a dataframe
    """

    dataframe_rows = []

    # iterate through all the files in the directory.
    for image_name in os.listdir(path_to_dataset_dir):

        image_path = os.path.join(path_to_dataset_dir, image_name)

        # give each one a unique uuid and store its path for the database payload.
        dataframe_rows.append({
            'id': str(uuid.uuid4()),
            'image_path': image_path,
            'image_name': image_name
        })

    return dataframe_rows


def generate_ad_dataset_dataframe(path_to_ad_dataset):
    """
    Function to generate the dataframe describing the ad dataset provided in the task.

    :param path_to_ad_dataset: path to the ad dataset.
    :return: pandas Dataframe where each row contains the path to an image, and its unique id.
    """
    part_1_rows = generate_folder_dataset_metadata(path_to_dataset_dir=os.path.join(path_to_ad_dataset, '0'))
    part_2_rows = generate_folder_dataset_metadata(path_to_dataset_dir=os.path.join(path_to_ad_dataset, '1'))

    return pd.DataFrame(part_1_rows + part_2_rows)


def batch_encode_images(qd_client, collection_name, df_dataset, batch_size=32):
    """
    Function to encode a batch of images at once and upsert the embeddings and corresponding payloads to the qdrant db.

    :param qd_client: qdrant_client
    :param collection_name: collection name for the qdrant_client
    :param df_dataset: dataframe describing the dataset
    :param batch_size:
    :return: None
    """
    # instantiate encoder model
    clip_model = SentenceTransformer("clip-ViT-B-32")

    # group dataframe into batches based on the selected batch size
    batches_df = df_dataset.groupby(np.arange(len(df_dataset)) // batch_size)

    # iterate through batches
    for _, batch_df in tqdm(batches_df):

        # load images and generate the embeddings
        image_batch = [Image.open(image_path) for image_path in batch_df[:]['image_path']]
        embeddings_batch = clip_model.encode(image_batch)

        # pass embeddings and data to qdrant collection
        upsert_batch_to_collection(qd_client, collection_name, batch_df, embeddings_batch)


def upsert_batch_to_collection(qd_client, collection_name, batch_df, embeddings_batch):
    """
    Upsert batch of embeddings with payloads to qdrant collection.
    :param qd_client: qdrant_client
    :param collection_name: collection name for the qdrant_client
    :param batch_df: dataframe describing the batch
    :param embeddings_batch: embeddings from the encoder.
    :return:
    """
    # each point gets upserted with its id, path and corresponding embeddings.
    qd_client.upsert(
        collection_name=collection_name,
        points=[
            rest.PointStruct(
                id=batch_df.iloc[batch_index]['id'],
                vector=embeddings_batch[batch_index],
                payload={'url': batch_df.iloc[batch_index]['image_path']}
            )
            for batch_index in range(len(batch_df))])


if __name__ == '__main__':
    df_dataset = generate_ad_dataset_dataframe('./ad_dataset')
    collection_name = 'ad_dataset'

    qd_client = QdrantClient("localhost", port=6333)

    qd_client.create_collection(
       collection_name=collection_name,
       vectors_config=rest.VectorParams(size=512, distance=rest.Distance.COSINE),
    )

    batch_encode_images(qd_client, collection_name, df_dataset, batch_size=32)