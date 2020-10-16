#!/bin/bash

python3 ./crawl_images.py \
    --resume_index 0 \
    --feeder_threads 4 \
    --parser_threads 8 \
    --downloader_threads 16
