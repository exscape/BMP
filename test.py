import sys
from BMP import BMP,DEBUG

if len(sys.argv) == 1:
	filename = "3x3.bmp"
else:
	filename = sys.argv[1]

b = BMP(filename)

print 'Image is {0}x{1} @ {2} bpp'.format(b.dib_header["width"], b.dib_header["height"], b.dib_header["bpp"])

# We need to skip te rest of the header, if any, to get to the actual data
b.file.seek(b.bmp_header["bitmap_offset"]) 

bitmap_data = b.file.read()
if DEBUG: print '{0} bytes of bitmap data read'.format(len(bitmap_data))

if DEBUG: print 'Padding per row should be {0} bytes'.format(b.padding_size)

print 'Working...',
sys.stdout.flush()
mod_bitmap = "".join(map(lambda x: chr(ord(x)/2), bitmap_data))
print 'done'

b.file.seek(0)
all_headers = b.file.read(b.bmp_header_len + b.dib_header["dib_header_len"])

out = open('out.bmp', 'w')
out.write(all_headers)
out.write(mod_bitmap)
out.close()
