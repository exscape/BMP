###
### Flip an image vertically.
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

rows = []

# Let's pretend it's a file to make things easy
f = StringIO(b.bitmap_data)
for row_num in xrange(0, b.height):
	rows.append(f.read( b.width * 3 + b.padding_size ))
for row in rows[::-1]:
	out.write(row)

out.close()
print 'done'
