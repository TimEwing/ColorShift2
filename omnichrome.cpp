#include <iostream>
#include <stdint.h>
#include <fstream>
#include <limits.h>
#include <cstdlib>
#include <algorithm>
#include <cmath>

using namespace std;

#define PIX_SIZE 7

/*
    memblock shape:
    
    ==Header==
    byte 0: colorsize
    ==Data==
    byte 0-1:   x
    byte 2-3:   y
    byte 4:     r
    byte 5:     g
    byte 6:     b
*/

struct Color
{
    uint8_t r;
    uint8_t g;
    uint8_t b;
} t_color;
// Total size: 4+4+1+1+1 = 11
struct Pixel
{
    uint16_t x;
    uint16_t y;
    Color color;
} t_pixel;

struct PixelQ
{
    Pixel p;
    PixelQ* next = NULL;
};

int dist(Color c1, Color c2)
{
    return pow(c1.r-c2.r, 2) + pow(c1.g-c2.g, 2) + pow(c1.b-c2.b, 2);
}

int ri, le;
bool pixel_sorter(Pixel const& lhs, Pixel const& rhs)
{
    le = lhs.color.r + lhs.color.g + lhs.color.b;
    ri = rhs.color.r + rhs.color.g + rhs.color.b;
    return le < ri;
}

int main () 
{
    cout << "Opening file tmp.bin" << endl;

    ifstream infile("tmp.bin", ios::in|ios::binary);

    // Build image
    char colorsize;
    if(!infile.read(&colorsize, 1))
    {
        return 1;
    }
    int color_count = colorsize * colorsize * colorsize;

    Pixel* pixels = new Pixel[color_count];
    int pix_itr = 0;
    char* in_pix = new char[PIX_SIZE];
    while(infile.read(in_pix, PIX_SIZE))
    {
        t_pixel.x = (uint32_t)in_pix[0] 
                    | (uint32_t)in_pix[1]<<8;
        t_pixel.y = (uint32_t)in_pix[2]
                    | (uint32_t)in_pix[3]<<8;
        t_pixel.color.r = in_pix[4];
        t_pixel.color.g = in_pix[5];
        t_pixel.color.b = in_pix[6];
        pixels[pix_itr] = t_pixel;
        pix_itr++;
    }
    int pix_count = pix_itr + 1;

    cout << "Opened tmp.bin; file contained " << pix_count << " pixels." << endl;
    cout << "Building unique pixel array..." << endl;

    // Build array of unique colors
    Color* colors_unique = new Color[color_count];
    bool* colors_unique_available = new bool[color_count];
    int color_itr = 0;
    uint8_t r,g,b;
    for(r = 0; r < colorsize; r++)
    {
        for(g = 0; g < colorsize; g++)
        {
            for(b = 0; b < colorsize; b++)
            {
                t_color.r = r;
                t_color.g = g;
                t_color.b = b;
                colors_unique[color_itr] = t_color;
                colors_unique_available[color_itr] = true;
                color_itr++;
            }
        }
    }

    cout << "Built unique pixel array. " << endl;
    cout << "Running color matching..." << endl;

    sort(pixels, pixels + pix_count, &pixel_sorter);

    // For each pixel, pick the best color match that hasn't been picked
    int min_dist;
    int min_pix;
    int min_color;
    int cur_dist;
    int dist_cutoff = 0;
    for(int pix_itr = 0; pix_itr < pix_count; pix_itr++)
    {
        min_dist = INT_MAX;
        min_pix = 0;
        for(int color_itr = 0; color_itr < color_count; color_itr++)
        {
            if(!colors_unique_available[color_itr])
            {
                continue;
            }
            cur_dist = dist(colors_unique[color_itr], pixels[pix_itr].color);
            if(min_dist > cur_dist)
            {
                min_dist = cur_dist;
                min_pix = pix_itr;
                min_color = color_itr;
            }

            if(cur_dist < dist_cutoff)
            {
                break;
            }
        }
        pixels[min_pix].color = colors_unique[min_color];
        colors_unique_available[min_color] = false;
        if(dist_cutoff <= min_dist)
        {
            dist_cutoff = min_dist+1;
        }

        if((pix_itr & 0x100) && !(pix_itr & 0xff))
        {
            cout << pix_itr*100/pix_count << endl;
        }
    }

    // Write to output
    ofstream outfile("tmp_out.bin", ios::out|ios::binary);
    outfile.write((char*)&colorsize,1);
    for(int i = 0; i < pix_count; i++)
    {
        const char* x = (char*)&pixels[i].x;
        const char* y = (char*)&pixels[i].y;
        const char* r = (char*)&pixels[i].color.r;
        const char* g = (char*)&pixels[i].color.g;
        const char* b = (char*)&pixels[i].color.b;
        outfile.write(x, 2);
        outfile.write(y, 2);
        outfile.write(r, 1);
        outfile.write(g, 1);
        outfile.write(b, 1);
    }

    return 0;
}