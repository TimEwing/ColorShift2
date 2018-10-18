import argparse
import omnichrome
import os
import numpy as np
from collections import deque
from PIL import Image

# TODO: Most of the comments here need to be done
# evaluator.py generates evaluations on the images being fucked with.
# Basically, there's a "perfect" solution where the average distance of ALL pixels in the image are as close to their
# original color as possible. We can determine an image's "accuracy" when compared to the perfect solution
#  as the following:
# (our_dist - perfect_dist)
# On top of this, we care about speed. we can penalize our evaluation by multiplying the distance by the time taken to
# complete the solution.
# (our_dist - perfect_dist)*time_taken
# Unfortunately, if our_dist = perfect_dist, we get a 'perfect score', as the function will evaluate to 0.
# So, we have to make our distance accuracy = (1+our_dist-perfect_dist) instead.
# Time should have the same property, starting at 1.

# In order to tune how important time_taken & accuracy is, we need to be able to scale them separately.
# One option is to exponentiate them by some constant that we define? Making full evaluation =
# (1 + our_dist - perfect_dist)**distance_tuner * (1+time_taken)**time_tuner
# Our "perfect score" (Perfect solution, with no time taken) should still be 0 afterwords, making the full eval function
# ((1 + our_dist - perfect_dist)**distance_tuner * (1+time_taken)**time_tuner) - 1
def generate_difference_graph(after,before):
    #print(before)
    #print(type(before[0][0][0]))
    print("Calculating distance graph...")
    print("For reference, black is the same color as originally, whiter = further away.")
    output = abs(np.subtract(before.astype(float),after.astype(float))/252)
    output = (output*252).astype(np.uint8)
    for x,y in np.ndindex(output.shape[0:2]):
        r,g,b = output[x][y]
        distance = np.ceil(np.sqrt((r) ** 2 + (g) ** 2 + (b) ** 2))
        output[x][y] = (distance,distance,distance)
        #print(distance)
    #print(before[93][97])
    #print(after[93][97])
    #print(output[93][97])
    return output

def main():
    parser = argparse.ArgumentParser(description="Evaluate a fuckup")
    parser.add_argument('before', type=str, help="File pre-fucking")
    parser.add_argument('after', type=str, help="File post-fucking")
    parser.add_argument('output_location', type=str, help="Place to put the distance graph")
    args = parser.parse_args()
    before = omnichrome.get_image(args.before)
    after = omnichrome.get_image(args.after)
    input_arr = generate_difference_graph(before,after)

    img = Image.fromarray(input_arr)
    img.save(args.output_location)
    img.show()

if __name__ == '__main__':
    main()
