import argparse
import os
import numpy as np
from collections import deque
from PIL import Image

MASK_COLOR = (255, 255, 255)
DIST_CUTOFF = (2 * 3)**2

def main():
    parser = argparse.ArgumentParser(description="Fuck up an image")
    parser.add_argument('filename', type=str, help="File to fuck")
    parser.add_argument('colorsize', type=int, help="Minimum = ceil(cbrt(width*height)); this is the colors per channel")
    parser.add_argument('--output_dir', type=str, default=os.getcwd(), help="Where to put the fucked file")
    parser.add_argument('--output_file', type=str, help="Where to put the fucked file, but also the name")
    parser.add_argument('--mask', type=str, help="file to pull mask from")
    parser.add_argument('--write', action='store_true', help="Just write to tmp.bin")
    parser.add_argument('--read', action='store_true', help="Just read from tmp.bin")
    args = parser.parse_args()

    # Output file stuff
    if args.output_file is None:
        if args.output_dir is None:
            output_filename = os.path.join(args.filename, '_output00')
        else:
            output_filename = os.path.join(args.output_dir, os.path.basename(args.filename) + '_output00')
        # Default to not overwriting files
        filename_version = 0
        while os.path.exists(output_filename + '.bmp'):
            output_filename = output_filename[:-2] + str(filename_version).zfill(2)
            filename_version += 1
        output_filename = output_filename + '.bmp'
    else:
        output_filename = args.output_file

    # Load image
    print("Loading image %s" % args.filename)
    input_arr = get_image(args.filename)
    height, width = input_arr.shape[:2]
    input_arr = input_arr*(args.colorsize/256.0)
    input_arr = input_arr.astype('uint8')

    # Build input_list, maybe with a mask
    print("Building input list...")
    input_list = []
    if args.mask:
        print("Loading mask %s"%args.mask)
        mask_arr = get_mask(args.mask)
        for x,y in np.ndindex(width, height):
            if mask_arr[x,y]:
                r,g,b = input_arr[x,y]
                input_list.append(((x,y),(r,g,b)))
    else:
        for x,y in np.ndindex(width, height):
            r,g,b = input_arr[x,y]
            input_list.append(((x,y),(r,g,b)))

    output_list = omnichrome(input_list, args.colorsize)


    print("Setting up output...")
    for (x,y), (r,g,b) in output_list:
        input_arr[x,y] = r,g,b

    input_arr = input_arr*(256.0/args.colorsize)
    input_arr = input_arr.astype('uint8')
    img = Image.fromarray(input_arr)
    img.save(output_filename)
    img.show()

def omnichrome(input_list, colorsize):
    print("Setting up colorspace...")
    # Expects input list as a list of ((x,y),(r,g,b)) tuples
    colorspace = np.empty([colorsize, colorsize, colorsize, 2], dtype=int)
    colorspace_added = np.empty([colorsize, colorsize, colorsize], dtype=bool)
    for r,g,b in np.ndindex(colorsize, colorsize, colorsize):
        colorspace[r,g,b] = -1, -1
        colorspace_added[r,g,b] = False

    queues = {}
    for (x,y),(r,g,b) in input_list:
        try:
            queues[(r,g,b)].append((x,y))
        except KeyError:
            queues[(r,g,b)] = deque([(x,y)])
            queues[(r,g,b)].append((x,y))

    # Pop one item from each queue (always place one of the coords at their o.g. color)
    for col, q in queues.items():
        pt = q.popleft()
        colorspace[col] = pt
        colorspace_added[col] = True

    print("Setting up empty queue...")
    next_empty = deque()
    adj = [
        (1,0,0),
        (-1,0,0),
        (0,1,0),
        (0,-1,0),
        (0,0,1),
        (0,0,-1)
    ]
    for r,g,b in np.ndindex(colorsize, colorsize, colorsize):
        # check if this spot is empty
        if not colorspace_added[r,g,b]:
            # check adjacent spots
            for ro,go,bo in adj:
                try:
                    if colorspace_added[r+ro, g+go, b+bo]:
                        next_empty.append((r, g, b))
                        colorspace_added[(r, g, b)] = True
                        break
                except IndexError:
                    continue

    print("Processing queues...")
    # Search the keys
    while len(next_empty):
        print(len(next_empty))
        r,g,b = next_empty.popleft()

        # Find nearest available pixel
        min_dist = float('inf')
        min_key = None
        for key in queues:

            kr, kg, kb = key
            cur_dist = (r-kr)**2 + (g-kg)**2 + (b-kb)**2
            if cur_dist < min_dist:
                min_dist = cur_dist
                min_key = key
            if min_dist < DIST_CUTOFF:
                break
        assert min_key is not None, "Colorsize too small"

        # pop and lock
        colorspace[r,g,b] = queues[min_key].popleft()
        if len(queues[min_key]) == 0:
            del queues[min_key]

        # add new keys to next_empty
        for ro,go,bo in adj:
            try:
                if not colorspace_added[r+ro, g+go, b+bo]:
                    next_empty.append((r+ro, g+go, b+bo))
                    colorspace_added[(r+ro, g+go, b+bo)] = True
            except IndexError:
                continue


    print("Queues processed")
    output_list = []
    for r,g,b in np.ndindex(colorsize, colorsize, colorsize):
        x,y = colorspace[r,g,b]
        if x != -1:
            output_list.append(((x,y),(r,g,b))) # needs more parens
    return output_list

def get_image(filename):
    input_image = Image.open(filename)
    input_image = input_image.convert(mode='RGB')
    input_image = np.asarray(input_image)
    return input_image

def get_mask(filename):
    mask_img = get_image(filename)
    width, height, _ = mask_img.shape
    mask_arr = np.empty([width, height], dtype=bool)
    for x,y in np.ndindex(width, height):
        if all(mask_img[x, y] == MASK_COLOR):
            mask_arr[x,y] = True
        else:
            mask_arr[x,y] = False
    return mask_arr

if __name__ == '__main__':
    main()
