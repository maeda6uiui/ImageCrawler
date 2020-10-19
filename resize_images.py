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

def main(save_root_dir,image_width,image_height):
    count_resized=0

    pathname=os.path.join(save_root_dir,"*")
    directories=glob.glob(pathname)
    for directory in tqdm(directories):
        pathname=os.path.join(directory,"*[!txt]")
        files=glob.glob(pathname)

        for file in files:
            try:
                image=Image.open(file)
                if image.width!=image_width or image.height!=image_height:
                    image=image.resize((image_width,image_height))
                    image.save(file)

                    count_resized+=1
            except Exception as e:
                logger.error(e)
                continue

    logger.info("Total number of images resized: {}".format(count_resized))

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--save_root_dir",type=str,default="./Images")
    parser.add_argument("--image_width",type=int,default=256)
    parser.add_argument("--image_height",type=int,default=256)
    args=parser.parse_args()

    main(args.save_root_dir,args.image_width,args.image_height)
