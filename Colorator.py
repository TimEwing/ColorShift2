#!/usr/bin/python3

import Image
import pandas
import math
import argparse
import os
from collections import deque

def main():
	parser = argparse.ArgumentParser(description="Fuck up an image")
	parser.add_argument('filename', type=str, help="File to fuck")
	parser.add_argument('color_size', type=int, help="Minimum: ceil(cbrt(width*height)) - color resolution")
	parser.add_argument('--output_dir', type=str, default=os.getcwd(), help="Where to put the fucked file")
	parser.add_argument('--output_filename', type=str, help="Where to put the fucked file, but also the name")
	args = parser.parse_args()

	# Get output filename
	if args.output_filename is None:
		if args.output_dir is None:
			output_filename = os.path.join(filename, '_output00')
		else:
			output_filename = os.path.join(args.output_dir, os.path.basename(filename) + '_output00')
		# Default to not overwriting files
		filename_version = 0
		while os.path.exists(output_filename + '.bmp'):
			output_filename = output_filename[:-2] + str(filename_version).zfill(2)
			filename_version += 1
		output_filename = output_filename + '.bmp'
	else:
		output_filename = args.output_filename

	# Load file
	input_image = Image.open(filename).convert()
	width, height = input_image.size

if __name__ == '__main__':
	main()
