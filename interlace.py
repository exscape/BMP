###
### "Interlace" a picture - divide every second row's brightness by two, creating a striped appearance
###

import sys
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

mod_bitmap = ""

# Let's pretend it's a file to make things easy
f = StringIO(b.bitmap_data)
for row_num in xrange(0, b.height):
	if row_num & 1 == 0:
		# Simply copy the data from even rows...
		mod_bitmap += f.read((b.width * 3) + b.padding_size)
	else:
		# ... and divide all pixel values by two on odd rows
		data = f.read((b.width * 3) + b.padding_size)
		mod_bitmap += "".join(map (lambda x: chr(ord(x)/2), data))

# ... and then save the results, with unmodified headers, since the size, bpp etc. are all the same
out = open('out.bmp', 'w')
out.write(b.all_headers)
out.write(mod_bitmap)
out.close()

print 'done'
