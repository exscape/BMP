DEBUG=True

import sys
from struct import pack,unpack

def die(str="Unspecified error"):
	sys.stderr.write("Fatal error: {0}\n".format(str))
	exit(1)

def warn(str="FIXME"):
	sys.stderr.write("Warning: {0}\n".format(str))

filename = ""
if len(sys.argv) == 1:
	filename = "test.bmp"
else:
	filename = sys.argv[1]

f = open(filename, 'r')
bmp_header = unpack('<2bIHHI', f.read(14))
magic = str(chr(bmp_header[0])) + chr(bmp_header[1])
if DEBUG: print 'BMP header:', bmp_header

### Validate the header
if magic != "BM":
	die("Sorry, I can't read this file; invalid magic")

file_size = bmp_header[2]
bitmap_offset = bmp_header[5]
prevpos = f.tell()
f.seek(0, 2) # Seek to end of file, to check its size
if f.tell() != file_size:
	die("Malformed header; file size in header doesn't match actual file size; {0} (actual) vs {1} (header) bytes".format(f.tell(), file_size))
f.seek(prevpos, 0)

dib_header_len = unpack('I', f.read(4))[0]

if dib_header_len == 64:
	die("V2 DIB-header BMPs not supported")
elif dib_header_len != 40:
	warn("V1/V4/V5 DIB header. Stuff may break... but should work.")

f.seek(-4, 1) # Re-read the header
dib_header = "" # Lexical scoping

if dib_header_len == 12:
	# OS/2 V1 header
	dib_header = unpack('I4H', f.read(12))
	if DEBUG: print 'OS/2 V1 DIB header'
elif dib_header_len in (40,108,124):
	# Windows V3/V4/V5 header - only the necessary parts are read
	dib_header = unpack('I2i2H', f.read(16))
	if DEBUG: print 'V3/V4/V5 DIB header'
else:
	die("Unsupported/corrupt DIB header")

if DEBUG: print 'DIB header (relevant parts):', dib_header

(dib_header_len,width,height,color_planes,bpp) = dib_header

if color_planes != 1:
	die("Invalid/corrupt DIB header; # of color planes must be 1")

if bpp != 24:
	die("Only 24 bits per pixel is supported at the moment; this image appears to be {0}".format(bpp))

print 'Image is {0}x{1} @ {2} bpp'.format(width, height, bpp)

# We need to skip te rest of the header, if any, to get to the actual data
f.seek(bitmap_offset) 

bitmap_data = f.read()
if DEBUG: print '{0} bytes of bitmap data read'.format(len(bitmap_data))
