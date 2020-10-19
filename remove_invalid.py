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

def main(save_root_dir):
    count_invalid=0

    pathname=os.path.join(save_root_dir,"*")
    directories=glob.glob(pathname)
    for directory in tqdm(directories):
        pathname=os.path.join(directory,"*[!txt]")
        files=glob.glob(pathname)

        for file in files:
            try:
                image=Image.open(file)
            except Exception as e:
                os.remove(file)
                count_invalid+=1
                
                continue

    logger.info("Total number of invalid images: {}".format(count_invalid))

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--save_root_dir",type=str,default="./Images")
    args=parser.parse_args()

    main(args.save_root_dir)
