import argparse
import numpy as np

import omnichrome

parser = argparse.ArgumentParser(description="Count unmasked pixels in an mask")
parser.add_argument('filename', type=str, help="mask")
args = parser.parse_args()

count = 0
mask_arr = omnichrome.get_mask(args.filename)
for x,y in np.ndindex(mask_arr.shape[:2]):
    if mask_arr[x,y]:
    	count += 1

print(count)