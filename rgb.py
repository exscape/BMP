###
### Split a file into three; one with only the red channel, one with only the green, and one with only the blue
###

import sys, struct
from bmp import BMP
from cStringIO import StringIO

if len(sys.argv) == 1:
	filename = "test.bmp"
else:
	filename = sys.argv[1]

img = BMP(filename)

print 'Image is {0}x{1} @ {2} bpp'.format(img.width, img.height, img.bpp)

print 'Working...',
sys.stdout.flush()

f = StringIO(img.bitmap_data)
red_bitmap_data = ""
green_bitmap_data = ""
blue_bitmap_data = ""

for row_num in xrange(0, img.height):
	for pix in xrange(0, img.width):
		pixel = struct.unpack("3B", f.read(3))
		red_bitmap_data += "".join( (chr(0x00), chr(0x00), chr(pixel[2])) )
		green_bitmap_data += "".join( (chr(0x00), chr(pixel[1]), chr(0x00)) )
		blue_bitmap_data += "".join( (chr(pixel[0]), chr(0x00), chr(0x00)) )

	if img.padding_size != 0:
		for i in range(0, img.padding_size):
			red_bitmap_data += chr(0x00)
			blue_bitmap_data += chr(0x00)
			green_bitmap_data += chr(0x00)
		f.seek(img.padding_size, 1)
	
# ... and then save the results, with unmodified headers, since the size, bpp etc. are all the same
out_blue = open('out_blue.bmp', 'w')
out_blue.write(img.all_headers)
out_blue.write(blue_bitmap_data)

out_green = open('out_green.bmp', 'w')
out_green.write(img.all_headers)
out_green.write(green_bitmap_data)

out_red = open('out_red.bmp', 'w')
out_red.write(img.all_headers)
out_red.write(red_bitmap_data)

print 'done'
