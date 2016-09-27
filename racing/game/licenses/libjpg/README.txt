Independent JPEG Group's free JPEG software
-------------------------------------------

This package contains C software to implement JPEG image encoding, decoding,
and transcoding.  JPEG is a standardized compression method for full-color
and gray-scale images.

The distributed programs provide conversion between JPEG "JFIF" format and
image files in PBMPLUS PPM/PGM, GIF, BMP, and Targa file formats.  The
core compression and decompression library can easily be reused in other
programs, such as image viewers.  The package is highly portable C code;
we have tested it on many machines ranging from PCs to Crays.

We are releasing this software for both noncommercial and commercial use.
Companies are welcome to use it as the basis for JPEG-related products.
We do not ask a royalty, although we do ask for an acknowledgement in
product literature (see the README file in the distribution for details).
We hope to make this software industrial-quality --- although, as with
anything that's free, we offer no warranty and accept no liability.

For more information, contact jpeg-info@jpegclub.org.


Contents of this directory
--------------------------

jpegsrc.vN.tar.gz contains source code, documentation, and test files for
release N in Unix format.

jpegsrN.zip contains source code, documentation, and test files for
release N in Windows format.

jpegaltui.vN.tar.gz contains source code for an alternate user interface for
cjpeg/djpeg in Unix format.

jpegaltuiN.zip contains source code for an alternate user interface for
cjpeg/djpeg in Windows format.

wallace.ps.gz is a PostScript file of Greg Wallace's introductory article
about JPEG.  This is an update of the article that appeared in the April
1991 Communications of the ACM.

jpeg.documents.gz tells where to obtain the JPEG standard and documents
about JPEG-related file formats.

jfif.ps.gz is a PostScript file of the JFIF (JPEG File Interchange Format)
format specification.

jfif.txt.gz is a plain text transcription of the JFIF specification; it's
missing a figure, so use the PostScript version if you can.

TIFFTechNote2.txt.gz is a draft of the proposed revisions to TIFF 6.0's
JPEG support.

pm.errata.gz is the errata list for the first printing of the textbook
"JPEG Still Image Data Compression Standard" by Pennebaker and Mitchell.

jdosaobj.zip contains pre-assembled object files for JMEMDOSA.ASM.
If you want to compile the IJG code for MS-DOS, but don't have an assembler,
these files may be helpful.
