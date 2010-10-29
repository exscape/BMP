import sys, struct
from cStringIO import StringIO

DEBUG=True

###
### TODO: Add docstrings and comments; clean up code
###

def die(str="Unspecified error"):
	sys.stderr.write("Fatal error: {0}\n".format(str))
	exit(1)

def warn(str="FIXME"):
	sys.stderr.write("Warning: {0}\n".format(str))
	sys.stderr.flush()

class BMP(object):
	bmp_header_len = 14

	def __init__(self, arg=None, open_as_data=False):
		""" Ugly hack due to Python's lack of method overloading. This constructor can be used in three ways:
			1) BMP(filename[, False]) -> returns a BMP object with data read from the filename
			2) BMP(bmp_data, [open_as_data=]True) -> returns a BMP object with data read from supplied string/blob.
			3) BMP() -> returns an "empty" BMP object that cannot be used except with rgb_merge(). """

		if arg == None:
			self.empty = True
			return
		else:
			self.empty = False

		if open_as_data == False:
			try:
				self.file = open(arg, 'r')
			except IOError as e:
				die (str(e))

			print 'Opened file {0}...'.format(arg)
		else:
			self.file = StringIO(arg)
		
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
			die("Malformed BMP header; file size in header doesn't match file size; {0} (actual) vs {1} (header) bytes".format(self.file.tell(), bmp_header[2]))
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

		if self.height < 0:
			self.height = -self.height
			warn("Bitmap pixel data is stored \"upside down\"")

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
		self.padding_size = self.width & 3 # Magic! (Quite simple, actually.)

		if DEBUG: print 'DIB header:', self.dib_header

		# Save both headers as a binary blob that can be used when modifying the bitmap data,
		# without changing image dimensions (affecting file size) or such
		self.file.seek(0)
		self.all_headers = self.file.read(self.bmp_header_len + self.dib_header_len)

		###
		### Read the bitmap data
		###

		self.file.seek(self.bitmap_offset) 
		self.bitmap_data = self.file.read()
		if DEBUG: print '{0} bytes of bitmap data read'.format(len(self.bitmap_data))
		if DEBUG: print 'Padding per row should be {0} bytes'.format(self.padding_size)

		self.file.close()	

	def horizontal_flip(self):
		if self.empty == True:
			die("Attempted to call horizontal_flip() on an empty BMP object!")

		mod_bitmap = ""

		# Let's pretend it's a file to make things easy
		f = StringIO(self.bitmap_data)
		for row_num in xrange(0, self.height):
			row = ""
			for pix in xrange(0, self.width):
				# Insert each pixel first on its respective row
				pixel = struct.unpack("3B", f.read(3))
				row = chr(pixel[0]) + chr(pixel[1]) + chr(pixel[2]) + row

			# Skip the padding in the input file
			f.seek(self.padding_size, 1)
			
			# Write the padding to the output file
			row += chr(0x00) * self.padding_size
			mod_bitmap += row
		self.bitmap_data = mod_bitmap
		return self

	def vertical_flip(self):
		if self.empty == True:
			die("Attempted to call vertical_flip() on an empty BMP object!")

		mod_bitmap = ""
		rows = []

		# Let's pretend it's a file to make things easy
		f = StringIO(self.bitmap_data)
		for row_num in xrange(0, self.height):
			rows.append(f.read(self.width * 3 + self.padding_size))
		for row in rows[::-1]:
			 mod_bitmap += row
		self.bitmap_data = mod_bitmap

		return self

	def rotate_180(self):
		if self.empty == True:
			die("Attempted to call rotate_180() on an empty BMP object!")

		self.vertical_flip()
		self.horizontal_flip()
		return self

	def save(self, filename):
		if self.empty == True:
			die("Attempted to call save() on an empty BMP object!")

		f = open(filename, 'w')
		f.write(self.all_headers)
		f.write(self.bitmap_data)
		f.close()

	def rgb_split(self):
		"""Splits one BMP object into three; one with only the red channel, one with the green, and one with the blue.
		
		Returns a tuple (R, G, B) of BMP instances."""

		if self.empty == True:
			die("Attempted to call rgb_split() on an empty BMP object!")

		f = StringIO(self.bitmap_data)
		red_data = self.all_headers
		green_data = self.all_headers
		blue_data = self.all_headers

		for row_num in xrange(0, self.height):
			for pix in xrange(0, self.width):
				pixel = struct.unpack("3B", f.read(3))
				red_data += chr(0x00) + chr(0x00) + chr(pixel[2])
				green_data += chr(0x00) + chr(pixel[1]) + chr(0x00)
				blue_data += chr(pixel[0]) + chr(0x00) + chr(0x00)

			red_data += chr(0x00) * self.padding_size
			blue_data += chr(0x00) * self.padding_size
			green_data += chr(0x00) * self.padding_size
			f.seek(self.padding_size, 1)
			
		# I'm not fond of the constructor hack... but it was the easiest way.
		return (BMP(red_data, True), BMP(green_data, True), BMP(blue_data, True))

	def rgb_merge(self, r, g, b):
		""" (Re)combine the red, green and blue color channels from three separate pictures of identical size into one. """
		if self.empty != True:
			 warn("Running rgb_merge() on a non-empty BMP; the existing data will be overwritten!")

		# Ugh...
		if len(set((r.width, g.width, b.width))) != 1 or len(set((r.height, g.height, b.height))) != 1 or len(set((r.bpp, g.bpp, b.bpp))) != 1:
			die("The dimensions and/or bpp differs between the input images to rgb_merge()!")

		rf = StringIO(r.bitmap_data)
		gf = StringIO(g.bitmap_data)
		bf = StringIO(b.bitmap_data)

		out_bitmap_data = ""

		for row_num in xrange(0, b.height):
			for pix in xrange(0, b.width):
				red_pixel = struct.unpack("3B", rf.read(3))[2]
				green_pixel = struct.unpack("3B", gf.read(3))[1]
				blue_pixel = struct.unpack("3B", bf.read(3))[0]

				out_bitmap_data += "".join( (chr(blue_pixel), chr(green_pixel), chr(red_pixel)) )

			out_bitmap_data += chr(0x00) * r.padding_size

			rf.seek(r.padding_size, 1)
			gf.seek(g.padding_size, 1)
			bf.seek(b.padding_size, 1)

		self = BMP(r.all_headers + out_bitmap_data, True)
		return self
