DEBUG=True

import sys
from struct import pack,unpack

def die(str="Unspecified error"):
	sys.stderr.write("Fatal error: {0}\n".format(str))
	exit(1)

def warn(str="FIXME"):
	sys.stderr.write("Warning: {0}\n".format(str))

f = open('test.bmp', 'r')
bmp_header = unpack('<2bIHHI', f.read(14))
magic = str(chr(bmp_header[0])) + chr(bmp_header[1])
if DEBUG: print 'First header:', bmp_header

### Validate the header
if magic != "BM":
	die("Sorry, I can't read this file; invalid magic number")

bmp_header_len = bmp_header[2]
bitmap_offset = bmp_header[5]
prevpos = f.tell()
f.seek(0, 2) # Seek to end of file, to check its size
if f.tell() != bmp_header_len:
	die("Malformed header; file size in header doesn't match actual file size; {0} vs {1}".format(f.tell(), bmp_header_len))
f.seek(prevpos, 0)

if DEBUG: print "first header good; data offset = {0}".format(bitmap_offset)

dib_header_len = unpack('I', f.read(4))

if dib_header_len in (12, 64):
	die("V1/V2 BMPs not supported")
elif dib_header_len != 40:
	warn("V4/V5 header. Stuff may break... but should work.")

f.seek(-4, 1) # Re-read the whole header, size included
dib_header =  unpack('I2i2H2I', f.read(24))
print 'Second header (relevant parts):', dib_header

(dib_header_len,width,height,color_planes,bpp,comp_method,bitmap_size) = dib_header

if bpp != 24:
	die("Only 24 bits per pixel is supported at the moment; this image appears to be {0}".format(bpp))
if comp_method != 0:
	die("BMP file is using a non-supported compression method.")
if color_planes != 1:
	die("Invalid DIB header! Color planes needs to be 1.")

print 'Image is {0}x{1} @ {2} bpp; {3} bytes of bitmap data'.format(width, height, bpp, bitmap_size)

# If the header was a V4/V5 one we need to skip ahead to get to the actual data
f.seek(bitmap_offset) 

bitmap_data = f.read()
if DEBUG: print '{0} bytes of bitmap data read'.format(len(bitmap_data))
