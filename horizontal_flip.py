###
### Flip an image horizontally.
###

import sys, struct
from bmp import BMP
from cStringIO import StringIO

if len(sys.argv) == 1:
	filename = "test.bmp"
else:
	filename = sys.argv[1]

b = BMP(filename)

print 'Image is {0}x{1} @ {2} bpp'.format(b.width, b.height, b.bpp)

print 'Working...',
sys.stdout.flush()

out = open('out.bmp', 'w')
out.write(b.all_headers)

# Let's pretend it's a file to make things easy
f = StringIO(b.bitmap_data)
for row_num in xrange(0, b.height):
	row = ""
	for pix in xrange(0, b.width):
		# Insert each pixel first on its respective row
		pixel = struct.unpack("3B", f.read(3))
		row = chr(pixel[0]) + chr(pixel[1]) + chr(pixel[2]) + row

	# Skip the padding in the input file
	f.seek(b.padding_size, 1)
	
	# Write the padding to the output file
	row += chr(0x00) * b.padding_size

	out.write(row)

out.close()
print 'done'
