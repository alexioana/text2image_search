# Text2Image Search 

This is a **text2image search** application built for the purpose of completing [this task](https://gist.github.com/generall/45004be240d9130d52d62ca57d0e6175).

I have chosen to work with the `Advertisement Image Dataset` provided in the description. 

In this readme you will find instructions on how to install and run the application, while the dataset exploration and approach & evaluation description documents are in separate files.

* [dataset exploration](./dataset_exploration.md)
* [approach and evaluation documentation](./approach.md)


## Installation and setup
### Step 1
1. Set up an environment where the requirements are satisfied. Make sure to [install qdrant](https://qdrant.tech/documentation/quick-start/) and docker as well.
```bash
pip install -r requirements.txt
```
2. Install the dataset on your local machine. This is made easy with the bash script which downloads and unzips the data.
```bash
bash install_data.bash
```
### Step 2

Now that the environment and dataset are prepared, we can run the application. Since this is running the qdrant docker command, make sure you run it as admin.

```bash
bash run_app.bash
```
**NB** This bash script abstracts two commands that would continuously run in separate terminal windows. If your python environment is located at a different location than the one in this bash script, please change it so it runs as expected.

Alternatively, run these 2 commands in 2 terminal windows:
```bash
docker run -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_storage:/qdrant/storage:z qdrant/qdrant
```
```bash
streamlit run image_search_app.py
```
### Step 3
The app will run but we need to populate the database with our encodings in order to search. This is done by simply running the *encode_images.py* script, and it only needs to run once.

```bash
python encode_images.py
```

After the script finishes running, you will be able to visit the [search GUI](http://localhost:8501/) and query the database! 
