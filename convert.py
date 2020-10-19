"""
画像フォーマットの変換およびリサイズを行う。
"""
import argparse
import glob
import logging
import os
from PIL import Image
from tqdm import tqdm

logging_fmt = "%(asctime)s %(levelname)s: %(message)s"
logging.basicConfig(format=logging_fmt)
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

def main(save_root_dir,image_width,image_height,resume_index):
    pathname=os.path.join(save_root_dir,"*")
    directories=glob.glob(pathname)

    count_errors=0

    for idx,directory in tqdm(enumerate(directories),total=len(directories)):
        if idx<resume_index:
            continue

        pathname=os.path.join(directory,"*[!txt]")
        files=glob.glob(pathname)

        for file in files:
            splits=os.path.splitext(file)
            if splits[1]==".jpg":
                continue

            dst_file=splits[0]+".jpg"
            try:
                image=Image.open(file)

                #Convert the image to RGB.
                if image.mode in ("RGBA","P"):
                    image=image.convert("RGB")

                #Resize
                if image.width!=image_width or image.height!=image_height:
                    image=image.resize((image_width,image_height))
                    
                image.save(dst_file)

            except Exception as e:
                os.remove(file)
                logger.error(e)

                count_errors+=1

                continue
    
    logger.info("Total number of errors: {}".format(count_errors))

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--save_root_dir",type=str,default="./Images")
    parser.add_argument("--image_width",type=int,default=256)
    parser.add_argument("--image_height",type=int,default=256)
    parser.add_argument("--resume_index",type=int,default=0)
    args=parser.parse_args()

    main(args.save_root_dir,args.image_width,args.image_height,args.resume_index)
