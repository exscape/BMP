###
### Simply divide all pixel values in half, creating a darker image than the original.
###

import sys
from bmp import BMP,DEBUG

if len(sys.argv) == 1:
	filename = "3x3.bmp"
else:
	filename = sys.argv[1]

b = BMP(filename)

print 'Image is {0}x{1} @ {2} bpp'.format(b.width, b.height, b.bpp)

print 'Working...',
sys.stdout.flush()
mod_bitmap = "".join(map(lambda x: chr(ord(x)/2), b.bitmap_data))
print 'done'

out = open('out.bmp', 'w')
out.write(b.all_headers)
out.write(mod_bitmap)
out.close()
