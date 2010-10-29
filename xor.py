###
### XORs the bitmap data of two images together... why? Uh, I'm not quite sure...
###

import sys, struct
from bmp import BMP
from cStringIO import StringIO

if len(sys.argv) != 3:
	print 'I need two arguments, and the images provided need to have the same dimensions and color depth!'
	exit(1)
else:
	first_filename = sys.argv[1]
	second_filename = sys.argv[2]

first = BMP(first_filename)
second = BMP(second_filename)

if first.width != second.width or first.height != second.height or first.bpp != second.bpp:
	print 'The dimensions and/or bpp differs between the input images!'
	exit(1)

print 'Images are {0}x{1} @ {2} bpp'.format(first.width, first.height, first.bpp)

print 'Working...',
sys.stdout.flush()

out_bitmap_data = ""

ff = StringIO(first.bitmap_data)
sf = StringIO(second.bitmap_data)

for row_num in xrange(0, first.height):
	for pix in xrange(0, first.width):
		first_pixel = struct.unpack("3B", ff.read(3))
		second_pixel = struct.unpack("3B", sf.read(3))

		out_bitmap_data += "".join( (chr(first_pixel[0] ^ second_pixel[0]), chr(first_pixel[1] ^ second_pixel[1]), chr(first_pixel[2] ^ second_pixel[2])) )

	out_bitmap_data += chr(0x00) * first.padding_size
	ff.seek(first.padding_size, 1)
	sf.seek(second.padding_size, 1)
	
# ... and then save the results, with unmodified headers, since the size, bpp etc. are all the same

out = open('out_xor.bmp', 'w')
out.write(first.all_headers)
out.write(out_bitmap_data)

print 'done'
