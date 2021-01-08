import os
import traceback
import random
import shutil
from os import path
from datetime import datetime
from PIL import Image
from colorthief import ColorThief

# Constants
VERSION = "1.0.B3"              # Program version
TOLERANCE_FILESIZE = 0.2        # Size percentage between two files that suggest duplication
TOLERANCE_COLORTHIEF = 10       # Quality of the colorthief checker to find an image's dominant color
SKIP_SPACE_CHECK = False         # Skip cehcking if the file sizes are similar
SKIP_RESOLUTION_CHECK = False   # Skip checking if the images' resolution are the same
SKIP_COLORTHIEF_CHECK = False   # Skip using colorthief to check if the images' dominant color are the same

# Opening message
print("ChunkyPotato's crappy image duplicate finder " + VERSION)
print(str(datetime.now()).split('.', 1)[0] + "\n")


files = os.listdir()    # List of files to analyze
checked = []            # List of file pairs checked so far
duplicates = []         # List of potential duplicates

# Create temporary working directory
rand = random.random()
tempDir = "temp"+str(rand)
while path.exists("temp"+str(rand)):
    rand = random.random()
    tempDir = "temp"+str(rand)
os.mkdir(tempDir)

# Clear all non-images from the files array
to_remove = []
for f in files:
    if not f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        to_remove.append(f)
for f in to_remove:
    files.remove(f)

# Loop through each image and see if it matches another image
for f1 in files:
    for f2 in files:
        if f1 == f2 or [f1+f2] in checked:
            continue
        checked.append([f2+f1])

        space_result = SKIP_SPACE_CHECK
        res_result = SKIP_RESOLUTION_CHECK
        cthief_result = SKIP_COLORTHIEF_CHECK

        try:
            i1 = Image.open(f1)
            i2 = Image.open(f2)

            if not SKIP_SPACE_CHECK:
                tolerance = os.path.getsize(f1)*TOLERANCE_FILESIZE
                if -tolerance <= os.path.getsize(f1) - os.path.getsize(f2) <= tolerance:
                    space_result = True
                # space_result = (-tolerance <= os.path.getsize(f1) - os.path.getsize(f2) <= tolerance)
            
            if not SKIP_RESOLUTION_CHECK and space_result:
                if i1.size == i2.size:
                    res_result = True
                # res_result = (i1.size == i2.size)
            
            if not SKIP_COLORTHIEF_CHECK and space_result and res_result:
                i1.resize(((int)(i1.width/10), (int)(i1.height/10)), resample=0, box=None, reducing_gap=None).save(tempDir+"/t1.png")
                i2.resize(((int)(i2.width/10), (int)(i2.height/10)), resample=0, box=None, reducing_gap=None).save(tempDir+"/t2.png")
                #i11.save(tempDir+"/t1.png")
                #i22.save(tempDir+"/t2.png")
                s1 = ColorThief(tempDir+"/t1.png")
                s2 = ColorThief(tempDir+"/t2.png")
                if s1.get_color(quality=TOLERANCE_COLORTHIEF) == s2.get_color(quality=TOLERANCE_COLORTHIEF):
                    cthief_result = True
                # cthief_result = (s1.get_color(quality=TOLERANCE_COLORTHIEF) == s2.get_color(quality=TOLERANCE_COLORTHIEF))

            if space_result and res_result and cthief_result:
                print(f1 + " may match " + f2)
                duplicates.append(f1 + " may match " + f2)


        # try:
        #     i1 = Image.open(f1)
        #     i2 = Image.open(f2)
        #     if f1 == f2:
        #         continue

        #     # Check 1: File size tolerance: if two images are within this margin, they may be dupes
        #     tolerance = os.path.getsize(f1)*TOLERANCE_FILESIZE
        #     if -tolerance <= os.path.getsize(f1) - os.path.getsize(f2) <= tolerance:

        #         # Check 2: If the two images are the same resolution, they may be dupes
        #         if i1.size == i2.size :
        #             i11 = i1.resize(((int)(i1.width/10), (int)(i1.height/10)), resample=0, box=None, reducing_gap=None)
        #             i22 = i2.resize(((int)(i2.width/10), (int)(i2.height/10)), resample=0, box=None, reducing_gap=None)
        #             i11.save(tempDir+"/t1.png")
        #             i22.save(tempDir+"/t2.png")
        #             s1 = ColorThief(tempDir+"/t1.png")
        #             s2 = ColorThief(tempDir+"/t2.png")

        #             # Check 3: If the two images have the same dominant color, they may be dupes
        #             if s1.get_color(quality=TOLERANCE_COLORTHIEF) == s2.get_color(quality=TOLERANCE_COLORTHIEF):
        #                 print(f1 + " may match " + f2)
        #                 duplicates.append(f1 + " may match " + f2)

        except Exception as e:
            traceback.print_exc()
            print()

# Open output file
output_to_open = "output.txt"
num = 1
while path.exists(output_to_open):
    output_to_open = "output"+str(num)+".txt"
    num += 1
output_file = open(output_to_open, "w+")

# Write output to the file
output_file.write("ChunkyPotato's crappy image duplicate finder " + VERSION + "\n")
output_file.write("Completion time: " + str(datetime.now()).split('.', 1)[0] + "\n\n\n")
output_file.write("ONLY extensions .png, .jpg, .jpeg, .tiff, .bmp, and .gif are checked. Everything else is ignored." + "\n")
output_file.write("All files in any subfolders are also ignored." + "\n\n")
if len(duplicates) > 0:
    output_file.write(str(len(duplicates)) + " possible duplicates found:\n\n\n")
    for i in duplicates:
        output_file.write(i+"\n")
else:
    output_file.write("No possible duplicates found.\n")
    output_file.write("This doesn't mean there aren't any, only that I couldn't find any lol.\n")

# Print relevant information to the terminal
print()
print(str(len(duplicates)) + " possible duplicates found.")
print("Output file saved to " + output_to_open + "\n")
output_file.close()

# Clean up the temporary working directory
shutil.rmtree(tempDir)

# Closing message
print("Job done.")
