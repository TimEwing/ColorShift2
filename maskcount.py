import argparse
import numpy as np

import omnichrome

parser = argparse.ArgumentParser(description="Count unmasked pixels in an mask")
parser.add_argument('filename', type=str, help="mask")
parser.add_argument('mask_color', type=int, nargs=3, default=[255, 255, 255], help="mask color")
args = parser.parse_args()

mask_arr = omnichrome.get_mask(args.filename, args.mask_color)

count = np.sum(mask_arr)
print("File contains {} pixels".format(count))

colorsize = count**(1./3.)
print("Colorsize:{}".format(colorsize))

height, width = mask_arr.shape

new_colorsize = 1<<int(colorsize).bit_length()-1
new_count = new_colorsize ** 3

aspect_ratio = width/height

scale_factor = (new_count**0.5)/(count**0.5)

print("Target size: {} by {}".format(width*scale_factor, height*scale_factor))
