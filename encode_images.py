from sentence_transformers import SentenceTransformer

from qdrant_client.http import models as rest
from qdrant_client import QdrantClient
from tqdm import tqdm
from PIL import Image

import pandas as pd
import numpy as np
import time
import uuid
import os


def generate_folder_dataset_metadata(path_to_dataset_dir):
    """
    Abstract function to generate the rows of a dataframe describing images in a folder.
    Each row of the dataset will contain a unique id, the path to the image and the image name.
    :param path_to_dataset_dir:
    :return:
    """

    dataframe_rows = []
    for image_name in os.listdir(path_to_dataset_dir):
        image_path = os.path.join(path_to_dataset_dir, image_name)
        dataframe_rows.append({
            'id': str(uuid.uuid4()),
            'image_path': image_path,
            'image_name': image_name
        })

    return dataframe_rows


def generate_ad_dataset_dataframe(path_to_ad_dataset):
    """
    Function to generate the dataframe describing the ad dataset provided in the task.
    :param path_to_ad_dataset:
    :return:
    """
    part_1_rows = generate_folder_dataset_metadata(path_to_dataset_dir=os.path.join(path_to_ad_dataset, '0'))
    part_2_rows = generate_folder_dataset_metadata(path_to_dataset_dir=os.path.join(path_to_ad_dataset, '1'))

    return pd.DataFrame(part_1_rows + part_2_rows)


def batch_encode_images(qd_client, collection_name, df_dataset, batch_size=32):

    clip_model = SentenceTransformer("clip-ViT-B-32")

    batches_df = df_dataset.groupby(np.arange(len(df_dataset)) // batch_size)

    for _, batch_df in tqdm(batches_df):
        image_batch = [Image.open(image_path) for image_path in batch_df[:]['image_path']]
        embeddings_batch = clip_model.encode(image_batch)

        upsert_batch_to_collection(qd_client, collection_name, batch_df, embeddings_batch)


def upsert_batch_to_collection(qd_client, collection_name, batch_df, embeddings_batch):
    qd_client.upsert(
        collection_name=collection_name,
        points=[
            rest.PointStruct(
                id=batch_df.iloc[batch_index]['id'],
                vector=embeddings_batch[batch_index],
                payload={'url': batch_df.iloc[batch_index]['image_path']}
            )
            for batch_index in range(len(batch_df))])


def encode_images(df_dataset):
    """

    :param df_dataset:
    :return:
    """

    points = []

    clip_model = SentenceTransformer("clip-ViT-B-32")

    for i in tqdm(range(0, len(df_dataset))):
        df_row = df_dataset.iloc[i]
        image_path = df_row['image_path']

        if os.path.isfile(image_path):
            start = time.time()
            embedding = clip_model.encode(Image.open(image_path))
            print('regular encoding took {}'.format(time.time() - start))
            points.append({
                "id": str(uuid.uuid4()),
                "vector": embedding,
                "payload": {"url": df_dataset.iloc[i, 1]}
            })

        if i % 50 == 0:
            print("{} images encoded".format(i))

    return points


def upsert_to_collection(qd_client, collection_name, points):
    qd_client.upsert(
        collection_name=collection_name,
        points=[
            rest.PointStruct(
                id=point['id'],
                vector=point['vector'].tolist(),
                payload=point['payload']
            )
            for point in points])


df_dataset = generate_ad_dataset_dataframe('./ad_dataset')
collection_name = 'ad_dataset'

qd_client = QdrantClient("localhost", port=6333)

qd_client.create_collection(
   collection_name=collection_name,
   vectors_config=rest.VectorParams(size=512, distance=rest.Distance.COSINE),
)

batch_encode_images(qd_client, collection_name, df_dataset, batch_size=32)