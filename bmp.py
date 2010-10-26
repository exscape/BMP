DEBUG=True

import sys

def die(str="Oops"):
	sys.stderr.write(str)
	exit(1)

from struct import pack,unpack

f = open('test.bmp', 'r')
file_header = unpack('<2bIHHI', f.read(14))
if DEBUG: print 'First header:', file_header

### Validate the header
if file_header[0] != 0x42 or file_header[1] != 0x4d:
	die("Sorry, I can't read this file; invalid magic number")

prevpos = f.tell()
f.seek(0, 2) # Seek to end of file, to check its size
if f.tell() != file_header[2]:
	die("Malformed header; file size in header doesn't match actual file size; {0} vs {1}".format(f.tell(), file_header[2]))
f.seek(prevpos, 0)

bitmap_offset = file_header[5]
if DEBUG: print "first header good; data offset = {0}".format(bitmap_offset)

bmp_header_len = unpack('I', f.read(4))

if bmp_header_len in (12, 64):
	die("V1/V2 BMPs not supported")
elif bmp_header_len != 40:
	print 'Warning: V4/V5 header. Stuff may break... but should work.'

f.seek(-4, 1) # Re-read the whole header, size included
bmp_header = unpack('3I2H6I', f.read(40))
print 'Second header:', bmp_header

(bmp_header_len,width,height,unused1,bpp,comp_method,bitmap_size,unused2,unused3,palette_colors,important_colors) = bmp_header

print 'Image is {0}x{1} @ {2} bpp; {3} bytes of bitmap data'.format(width, height, bpp, bitmap_size)

# If the header was a V4/V5 one we need to skip ahead to get to the actual data
f.seek(bitmap_offset) 

bitmap_data = f.read()
if DEBUG: print '{0} bytes of bitmap data read'.format(len(bitmap_data))
