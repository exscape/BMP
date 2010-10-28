import sys, struct
from bmp import BMP
from cStringIO import StringIO

if len(sys.argv) != 4:
	print 'I need three arguments; in order: red, green and blue. All pictures must have the same properties (size, bpp etc.)'
	exit(1)
else:
	red_filename = sys.argv[1]
	green_filename = sys.argv[2]
	blue_filename = sys.argv[3]

r = BMP(red_filename)
g = BMP(green_filename)
b = BMP(blue_filename)

# Ugh...
if len(set((r.width, g.width, b.width))) != 1 or len(set((r.height, g.height, b.height))) != 1 or len(set((r.bpp, g.bpp, b.bpp))) != 1:
	print 'The dimensions and/or bpp differs between the input images!'
	exit(1)

print 'Images are {0}x{1} @ {2} bpp'.format(b.width, b.height, b.bpp)

print 'Working...',
sys.stdout.flush()

out_bitmap_data = ""

rf = StringIO(r.bitmap_data)
gf = StringIO(g.bitmap_data)
bf = StringIO(b.bitmap_data)

for row_num in xrange(0, b.height):
	for pix in xrange(0, b.width):
		red_pixel = struct.unpack("3B", rf.read(3))[2]
		green_pixel = struct.unpack("3B", gf.read(3))[1]
		blue_pixel = struct.unpack("3B", bf.read(3))[0]

		out_bitmap_data += "".join( (chr(blue_pixel), chr(green_pixel), chr(red_pixel)) )

	if r.padding_size > 0:
		for i in range(0, r.padding_size):
			out_bitmap_data += chr(0x00)

	rf.seek(r.padding_size, 1)
	gf.seek(g.padding_size, 1)
	bf.seek(b.padding_size, 1)
	
# ... and then save the results, with unmodified headers, since the size, bpp etc. are all the same

out = open('out_combined.bmp', 'w')
out.write(b.all_headers)
out.write(out_bitmap_data)

print 'done'
