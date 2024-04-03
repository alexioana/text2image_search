#!/bin/bash

# Open the first terminal window and run a command
gnome-terminal -- bash -c 'docker run -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_storage:/qdrant/storage:z qdrant/qdrant;'

# Open the second terminal window and run a command
gnome-terminal -- bash -c 'venv/bin/streamlit run image_search_app.py; sleep 5;'




