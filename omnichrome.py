import argparse
import os
import numpy as np
from collections import deque
from PIL import Image

def main():
    parser = argparse.ArgumentParser(description="Fuck up an image")
    parser.add_argument('filename', type=str, help="File to fuck")
    parser.add_argument('colorsize', type=int, help="Minimum = ceil(cbrt(width*height)); this is the colors per channel")
    parser.add_argument('--output_dir', type=str, default=os.getcwd(), help="Where to put the fucked file")
    parser.add_argument('--output_file', type=str, help="Where to put the fucked file, but also the name")
    parser.add_argument('--write', action='store_true', help="Just write to tmp.bin")
    parser.add_argument('--read', action='store_true', help="Just read from tmp.bin")
    args = parser.parse_args()

    input_image = get_image(args.filename)
    height, width = input_image.shape[:2]
    input_image = input_image*(256.0/args.colorsize)
    input_image = input_image.astype('uint8')
    if not args.read:
        with open("tmp.bin", 'wb') as bin_file:
            bin_file.write(args.colorsize.to_bytes(1, byteorder='big', signed=False))
            for x,y in np.ndindex(width, height):
                out_bytes = bytearray()
                r,g,b = input_image[x,y]
                out_bytes.extend(x.to_bytes(2, byteorder='big', signed=False))
                out_bytes.extend(y.to_bytes(2, byteorder='big', signed=False))
                out_bytes.append(r)
                out_bytes.append(g)
                out_bytes.append(b)
                bin_file.write(out_bytes)

    if not args.read and not args.write:
        ret = os.system("g++ omnichrome.cpp -o omnichrome")
        if ret != 0:
            print("Something went wrong with the c++ code. :(")
            return
        ret = os.system("./omnichrome")
        if ret != 0:
            print("Something went wrong with the c++ code. :(")
            return

    if not args.write:
        output_arr = np.zeros([width, height, 3], dtype='uint8')
        with open("tmp_out.bin", 'rb') as bin_file:
            # We don't actually care about the colorsize, but read it anyway to setup the offset correctly
            bin_file.read(1)
            while True:
                bytes_in = bin_file.read(7)
                if not bytes_in:
                    break
                x = int.from_bytes(bytes_in[:2], byteorder="big")
                y = int.from_bytes(bytes_in[2:4], byteorder="big")
                r = bytes_in[4]
                g = bytes_in[5]
                b = bytes_in[6]
                output_arr[x,y] = r,g,b

            output_arr = output_arr * (256/args.colorsize)
            output_arr = output_arr.astype('uint8')
            output_image = Image.fromarray(output_arr)
            output_image.show()

def get_image(filename):
    input_image = Image.open(filename)
    input_image = input_image.convert(mode='RGB')
    input_image = np.asarray(input_image)
    return input_image

if __name__ == '__main__':
    main()