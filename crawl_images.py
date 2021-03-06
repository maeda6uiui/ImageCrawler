#!python3.6
"""
Bing画像検索を用いて画像を収集する。
"""
import argparse
import glob
import hashlib
import logging
import os
from icrawler.builtin import BingImageCrawler
from PIL import Image
from typing import List

logging_fmt = "%(asctime)s %(levelname)s: %(message)s"
logging.basicConfig(format=logging_fmt)

def create_custom_logger(progress_log_filepath:str)->logging.Logger:
    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.INFO)
    logger.propagate=False
    handler=logging.FileHandler(progress_log_filepath,"w",encoding="utf_8")
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(logging_fmt))
    logger.addHandler(handler)

    return logger

def get_md5_hash(keyword:str)->str:
    return hashlib.md5(keyword.encode()).hexdigest()

def crawl_images(
    keyword:str,
    max_num_images:int,
    save_dir:str,
    feeder_threads:int,
    parser_threads:int,
    downloader_threads:int):
    crawler=BingImageCrawler(
        feeder_threads=feeder_threads,
        parser_threads=parser_threads,
        downloader_threads=downloader_threads,
        log_level=logging.ERROR,
        storage={"root_dir":save_dir},
    )
    crawler.crawl(keyword=keyword,max_num=max_num_images)

def remove_unsupported_images(target_dir:str):
    supported_extensions=[".jpg",".jpeg",".png"]

    pathname=os.path.join(target_dir,"*[!txt]")
    files=glob.glob(pathname)

    for file in files:
        extension=os.path.splitext(file)[1]
        if extension not in supported_extensions:
            os.remove(file)

def format_images(target_dir:str,width:int,height:int,logger:logging.Logger):
    """
    画像のJPEG形式への変換およびリサイズを行う。
    """
    pathname=os.path.join(target_dir,"*[!txt]")
    files=glob.glob(pathname)

    for file in files:
        try:
            image=Image.open(file)

            #アルファチャンネルは使用しない。
            if image.mode in ("RGBA","P"):
                image=image.convert("RGB")
            
            #リサイズ
            image=image.resize((width,height))

            base_filepath=os.path.splitext(file)[0]
            save_filepath=base_filepath+".jpg"
            image.save(save_filepath)
        
        except Exception as e:
            logger.error(e)
            continue

def main(
    keyword_list_filepath:str,
    max_num_images:int,
    image_width:int,
    image_height:int,
    save_root_dir:str,
    progress_log_filepath:str,
    index_lower_bound:int,
    index_upper_bound:int,
    feeder_threads:int,
    parser_threads:int,
    downloader_threads:int):
    logger=create_custom_logger(progress_log_filepath)
    logger.info("keyword_list_filepath: {}".format(keyword_list_filepath))
    logger.info("max_num_images: {}".format(max_num_images))
    logger.info("image_size: ({},{})".format(image_width,image_height))
    logger.info("save_root_dir: {}".format(save_root_dir))
    logger.info("progress_log_filepath: {}".format(progress_log_filepath))
    logger.info("index lower_bound: {}\tindex upper bound: {}".format(index_lower_bound,index_upper_bound))
    logger.info("feader_threads: {}\tparser_threads: {}\tdownloader_threads: {}".format(
        feeder_threads,parser_threads,downloader_threads))

    os.makedirs(save_root_dir,exist_ok=True)

    with open(keyword_list_filepath,"r",encoding="utf_8") as r:
        keywords=r.read().splitlines()

    for idx,keyword in enumerate(keywords):
        if idx<index_lower_bound:
            continue
        if index_upper_bound>=0 and idx>=index_upper_bound:
            break

        logger.info("{}\t{}".format(idx,keyword))

        title_hash=get_md5_hash(keyword)
        save_dir=os.path.join(save_root_dir,title_hash)
        os.makedirs(save_dir,exist_ok=True)

        info_filepath=os.path.join(save_dir,"info.txt")
        with open(info_filepath,"w",encoding="utf_8") as w:
            w.write(keyword)
            w.write("\n")

        crawl_images(keyword,max_num_images,save_dir,feeder_threads,parser_threads,downloader_threads)
        remove_unsupported_images(save_dir)
        format_images(save_dir,image_width,image_height,logger)

if __name__=="__main__":
    parser=argparse.ArgumentParser()

    parser.add_argument("--keyword_list_filepath",type=str)
    parser.add_argument("--max_num_images",type=int)
    parser.add_argument("--image_width",type=int)
    parser.add_argument("--image_height",type=int)
    parser.add_argument("--save_root_dir",type=str)
    parser.add_argument("--progress_log_filepath",type=str)
    parser.add_argument("--index_lower_bound",type=int) #Inclusive
    parser.add_argument("--index_upper_bound",type=int)    #Exclusive  -1: No uppper bound
    parser.add_argument("--feeder_threads",type=int)
    parser.add_argument("--parser_threads",type=int)
    parser.add_argument("--downloader_threads",type=int)

    args=parser.parse_args()

    main(
        args.keyword_list_filepath,
        args.max_num_images,
        args.image_width,
        args.image_height,
        args.save_root_dir,
        args.progress_log_filepath,
        args.index_lower_bound,
        args.index_upper_bound,
        args.feeder_threads,
        args.parser_threads,
        args.downloader_threads
    )
