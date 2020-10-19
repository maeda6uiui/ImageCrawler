"""
画像を収集する。
"""
import argparse
import glob
import hashlib
import logging
import os
from icrawler.builtin import BingImageCrawler
from PIL import Image

logging_fmt = "%(asctime)s %(levelname)s: %(message)s"
logging.basicConfig(format=logging_fmt)

def create_custom_logger(custom_log_filepath):
    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.INFO)
    logger.propagate=False
    handler=logging.FileHandler(custom_log_filepath,"w",encoding="utf_8")
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(logging_fmt))
    logger.addHandler(handler)

    return logger

def get_md5_hash(keyword):
    return hashlib.md5(keyword.encode()).hexdigest()

def crawl_images(keyword,max_num_images,save_dir,feeder_threads,parser_threads,downloader_threads):
    crawler=BingImageCrawler(
        feeder_threads=feeder_threads,
        parser_threads=parser_threads,
        downloader_threads=downloader_threads,
        log_level=logging.ERROR,
        storage={"root_dir":save_dir},
    )
    crawler.crawl(keyword=keyword,max_num=max_num_images)

def resize_images(width,height,save_dir,logger):
    pathname=os.path.join(save_dir,"*[!txt]")
    files=glob.glob(pathname)

    for file in files:
        try:
            image=Image.open(file)

            #Convert the image to RGB.
            if image.mode in ("RGBA","P"):
                image=image.convert("RGB")

            #Resize
            image=image.resize((width,height))

            #Save as JPG
            splits=os.path.splitext(file)
            dst_file=None
            if splits[1]==".jpg":
                dst_file=file
            else:
                dst_file=splits[0]+".jpg"

            image.save(dst_file)
        except Exception as e:
            os.remove(file)
            logger.error(e)

            continue

def main(
    keyword_list_filepath,
    max_num_images,
    image_width,
    image_height,
    save_root_dir,
    custom_log_filepath,
    index_lower_bound,
    index_upper_bound,
    feeder_threads,
    parser_threads,
    downloader_threads):
    logger=create_custom_logger(custom_log_filepath)
    logger.info("keyword_list_filepath: {}".format(keyword_list_filepath))
    logger.info("max_num_images: {}".format(max_num_images))
    logger.info("image_size: ({},{})".format(image_width,image_height))
    logger.info("save_root_dir: {}".format(save_root_dir))
    logger.info("custom_log_filepath: {}".format(custom_log_filepath))
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
        resize_images(image_width,image_height,save_dir,logger)

if __name__=="__main__":
    parser=argparse.ArgumentParser()

    parser.add_argument("--keyword_list_filepath",type=str,default="./keywords.txt")
    parser.add_argument("--max_num_images",type=int,default=200)
    parser.add_argument("--image_width",type=int,default=256)
    parser.add_argument("--image_height",type=int,default=256)
    parser.add_argument("--save_root_dir",type=str,default="./Images")
    parser.add_argument("--custom_log_filepath",type=str,default="./progress.txt")
    parser.add_argument("--index_lower_bound",type=int,default=0) #Inclusive
    parser.add_argument("--index_upper_bound",type=int,default=-1)    #Exclusive  -1: No uppper bound
    parser.add_argument("--feeder_threads",type=int,default=2)
    parser.add_argument("--parser_threads",type=int,default=4)
    parser.add_argument("--downloader_threads",type=int,default=8)

    args=parser.parse_args()

    main(
        args.keyword_list_filepath,
        args.max_num_images,
        args.image_width,
        args.image_height,
        args.save_root_dir,
        args.custom_log_filepath,
        args.index_lower_bound,
        args.index_upper_bound,
        args.feeder_threads,
        args.parser_threads,
        args.downloader_threads
    )
