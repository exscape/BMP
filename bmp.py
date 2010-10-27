import sys, struct

DEBUG=True

###
### TODO: Add docstrings and comments; clean up code
### TODO: Add code to create separate R/G/B pictures from one input image w/ dynamic naming
###

def die(str="Unspecified error"):
	sys.stderr.write("Fatal error: {0}\n".format(str))
	exit(1)

def warn(str="FIXME"):
	sys.stderr.write("Warning: {0}\n".format(str))
	sys.stderr.flush()

class BMP(object):
	bmp_header_len = 14

	def __init__(self, filename):
		try:
			self.file = open(filename, 'r')
		except IOError as e:
			die (str(e))
		
		###
		### Read BMP header
		###

		self.file.seek(0)
		bmp_header = struct.unpack('<2bIHHI', self.file.read(self.bmp_header_len))

		if DEBUG: print 'BMP header:', bmp_header

		# Verify magic
		magic = str(chr(bmp_header[0])) + chr(bmp_header[1])
		if magic != "BM":
			die("Invalid magic")
		
		# Verify size
		prevpos = self.file.tell()
		self.file.seek(0, 2)
		if self.file.tell() != bmp_header[2]:
			die("Malformed BMP header; file size in header doesn't match file size; {0} (actual) vs {1} (header) bytes".format(f.tell(), file_size))
		self.file.seek(prevpos)

		# Save useful header info
		self.file_size = bmp_header[2]
		self.bitmap_offset = bmp_header[5]

		###
		### Read DIB header
		###

		self.file.seek(self.bmp_header_len)
		self.dib_header_len = struct.unpack('I', self.file.read(4))[0]

		# Check for the one (out of five) header types we don't support
		if self.dib_header_len == 64:
			die("V2 DIB-header BMPs not supported")

		# Re-read the whole header 
		self.file.seek(-4, 1)

		# Read and parse the header data
		if self.dib_header_len == 12:
			# OS/2 V1 header
			raw_dib_header = struct.unpack('I4H', self.file.read(12))
			if DEBUG: print 'OS/2 V1 DIB header'
		elif self.dib_header_len in (40,108,124):
			# Windows V3/V4/V5 header - only the necessary parts are read
			raw_dib_header = struct.unpack('I2i2H', self.file.read(16))
			if DEBUG: print 'V3/V4/V5 DIB header'
		else:
			die("Unsupported/corrupt DIB header")

		# Save the important parts from the DIB header
		self.dib_header = {'dib_header_len': self.dib_header_len, 'color_planes': raw_dib_header[3], 'width': raw_dib_header[1], 'height': raw_dib_header[2], 'bpp': raw_dib_header[4]}
		self.width = raw_dib_header[1]
		self.height = raw_dib_header[2]
		self.bpp = raw_dib_header[4]

		# Some basic error checking
		if self.dib_header["color_planes"] != 1:
			die("Invalid/corrupt DIB header; # of color planes must be 1")

		if self.bpp != 24:
			die("Only 24 bits per pixel is supported at the moment; this image appears to have {0}".format(self.bpp))

		# Calculate padding. Each row needs to be 4-byte aligned.
		# If the width is 1, we use 1*3 = 3 bytes for bitmap data, and need 1 for padding.
		# If the width is 2, we use 2*3 = 6 bytes for bitmap data, and need 2 for padding.
		# If the width is 3, we use 3*3 = 9 bytes for bitmap data, and need 3 for padding.
		# If the width is 4, we use 4*3 = 12 bytes for bitmap data, and need 0 for padding.
		# If the width is 5, we use 5*3 = 15 bytes for bitmap data, and need 1 for padding.
		# ... etc.
		self.padding_size = self.dib_header["width"] & 3 # Magic! (Quite simple, actually.)

		if DEBUG: print 'DIB header:', self.dib_header

		# Save both headers as a binary blob that can be used when modifying the bitmap data,
		# without changing image dimensions (affecting file size) or such
		self.file.seek(0)
		self.all_headers = self.file.read(self.bmp_header_len + self.dib_header["dib_header_len"])

		###
		### Read the bitmap data
		###

		self.file.seek(self.bitmap_offset) 
		self.bitmap_data = self.file.read()
		if DEBUG: print '{0} bytes of bitmap data read'.format(len(self.bitmap_data))
		if DEBUG: print 'Padding per row should be {0} bytes'.format(self.padding_size)
