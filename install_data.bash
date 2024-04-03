#!/bin/bash

wget https://storage.googleapis.com/ads-dataset/subfolder-0.zip
wget https://storage.googleapis.com/ads-dataset/subfolder-1.zip

mkdir ad_dataset
unzip ./subfolder-0.zip -d ./ad_dataset/0
unzip ./subfolder-1.zip -d ./ad_dataset/1
