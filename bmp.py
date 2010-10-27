import sys, struct

DEBUG=True
bmp_header_len = 14

def die(str="Unspecified error"):
	sys.stderr.write("Fatal error: {0}\n".format(str))
	exit(1)

def warn(str="FIXME"):
	sys.stderr.write("Warning: {0}\n".format(str))
	sys.stderr.flush()

def open_bmp_file(filename):
	try:
		file = open(filename, 'r')
	except IOError as e:
		die (str(e))
	return file

def get_bmp_header(file):
	# Read header
	file.seek(0)
	header = struct.unpack('<2bIHHI', file.read(bmp_header_len))

	if DEBUG: print 'BMP header:', header

	# Verify magic
	magic = str(chr(header[0])) + chr(header[1])
	if magic != "BM":
		die("Invalid magic")
	
	# Verify size
	prevpos = file.tell()
	file.seek(0, 2)
	if file.tell() != header[2]:
		die("Malformed header; file size in header doesn't match file size; {0} (actual) vs {1} (header) bytes".format(f.tell(), file_size))
	file.seek(prevpos)

	# All OK; return a dictionary containing the two relevant fields - 
	# file size and bitmap data offset
	return {'file_size': header[2], 'bitmap_offset': header[5]}

def get_dib_header(file):
	file.seek(bmp_header_len)
	dib_header_len = struct.unpack('I', f.read(4))[0]

	if dib_header_len == 64:
		die("V2 DIB-header BMPs not supported")

	file.seek(-4, 1) # Re-read the header

	if dib_header_len == 12:
		# OS/2 V1 header
		dib_header = struct.unpack('I4H', f.read(12))
		if DEBUG: print 'OS/2 V1 DIB header'
	elif dib_header_len in (40,108,124):
		# Windows V3/V4/V5 header - only the necessary parts are read
		dib_header = struct.unpack('I2i2H', f.read(16))
		if DEBUG: print 'V3/V4/V5 DIB header'
	else:
		die("Unsupported/corrupt DIB header")
	
	if dib_header[3] != 1:
		die("Invalid/corrupt DIB header; # of color planes must be 1")

	if dib_header[4] != 24:
		die("Only 24 bits per pixel is supported at the moment; this image appears to have {0}".format(bpp))

	if DEBUG: print 'DIB header:', dib_header

	return {'dib_header_len': dib_header_len, 'width': dib_header[1], 'height': dib_header[2], 'bpp': dib_header[4]}

############################################

if len(sys.argv) == 1:
	filename = "3x3.bmp"
else:
	filename = sys.argv[1]

f = open_bmp_file(filename)
bmp_header = get_bmp_header(f)
dib_header = get_dib_header(f)

print 'Image is {0}x{1} @ {2} bpp'.format(dib_header["width"], dib_header["height"], dib_header["bpp"])

# We need to skip te rest of the header, if any, to get to the actual data
f.seek(bmp_header["bitmap_offset"]) 

bitmap_data = f.read()
if DEBUG: print '{0} bytes of bitmap data read'.format(len(bitmap_data))

# Calculate padding. Each row needs to be 4-byte aligned.
# If the width is 1, we use 1*3 = 3 bytes for bitmap data, and need 1 for padding.
# If the width is 2, we use 2*3 = 6 bytes for bitmap data, and need 2 for padding.
# If the width is 3, we use 3*3 = 9 bytes for bitmap data, and need 3 for padding.
# If the width is 4, we use 4*3 = 12 bytes for bitmap data, and need 0 for padding.
# If the width is 5, we use 5*3 = 15 bytes for bitmap data, and need 1 for padding.
# ... etc.
padding_size = dib_header["width"] & 3 # Magic! (Quite simple, actually.)

if DEBUG: print 'Padding per row should be {0} bytes'.format(padding_size)

mod_bitmap = "".join(map(lambda x: chr(ord(x)/2), bitmap_data))

f.seek(0)
all_headers = f.read(bmp_header_len + dib_header["dib_header_len"])

out = open('out.bmp', 'w')
out.write(all_headers)
out.write(mod_bitmap)
out.close()
