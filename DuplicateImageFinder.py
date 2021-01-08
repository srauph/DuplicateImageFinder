import os
import traceback
import random
import shutil
import argparse
import time
import sys
from os import path
from datetime import datetime
from PIL import Image
from colorthief import ColorThief

# Program version
VERSION = "1.0.B4"


# Opening message
print("ChunkyPotato's crappy image duplicate finder " + VERSION)
print(str(datetime.now()).split('.', 1)[0] + "\n")

formatter = lambda prog: argparse.HelpFormatter(prog,max_help_position=40)
def my_int_type(arg):
    try:
        i = int(arg)
    except ValueError:    
        raise argparse.ArgumentTypeError("must be an integer")
    if i < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return i

parser = argparse.ArgumentParser(formatter_class=formatter,
                                    description="Crappy utility to try and find duplicate images, version "+VERSION)
parser.add_argument("-s", "--space-check", action="store_false",
                    help="check that two images consume similar disk space.")
parser.add_argument("-nr", "--no-res-check", action="store_true",
                    help="don't check that two images have the same resolution.")
parser.add_argument("-nc", "--no-cthief-check", action="store_true",
                    help="don't check that two images have the same dominant color.")
parser.add_argument("-st", "--space-tol", default=20, metavar="tolerance", type=my_int_type,
                    help="checks that two files' disk space are within the specified %% of the larger. ineffective if -s isn't set.")
parser.add_argument("-cq", "--ct-quality", default=10, metavar="quality", type=my_int_type,
                    help="sets the quality of the dominant color checking. lower values are more accurate but slower. ineffective if -nc is set.")
parser.add_argument("-v", "--verbose", action="store_true",
                    help="prints extra data in the output.")

args = parser.parse_args()

# Constants
SKIP_SPACE_CHECK = args.space_check             # Skip checking if the file sizes are similar
SKIP_RESOLUTION_CHECK = args.no_res_check       # Skip checking if the images' resolution are the same
SKIP_COLORTHIEF_CHECK = args.no_cthief_check    # Skip using colorthief to check if the images' dominant color are the same
TOLERANCE_FILESIZE = args.space_tol/100.0       # Size percentage between two files that suggest duplication
TOLERANCE_COLORTHIEF = args.ct_quality          # Quality of the colorthief checker to find an image's dominant color
VERBOSE = args.verbose                          # Verbose mode

# Variables
files = os.listdir()    # List of files to analyze
checked = []            # List of file pairs checked so far
duplicates = []         # List of potential duplicates

# Verbose strings
v_space = "Space check: " + str(not SKIP_SPACE_CHECK)
v_res = "Resolution check: " + str(not SKIP_RESOLUTION_CHECK)
v_ct = "Colorthief (Dominant color) check: " + str(not SKIP_COLORTHIEF_CHECK)
if not SKIP_SPACE_CHECK:
    v_space_t = "Space checker tolerance: " + str(TOLERANCE_FILESIZE*100) + "%%"
else:
    v_space_t = "Space checker tolerance: N/A"
if not SKIP_COLORTHIEF_CHECK:
    v_ct_q = "Colorthief quality level: " + str(TOLERANCE_COLORTHIEF)
else:
    v_ct_q = "Colorthief quality level: N/A"

# Print constants data if verbose mode is on
if VERBOSE:
    print(v_space)
    print(v_res)
    print(v_ct)
    print(v_space_t)
    print(v_ct_q)
    print()
    start_time = time.time()

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
                tolerance = max(os.path.getsize(f1), os.path.getsize(f2))*TOLERANCE_FILESIZE
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
                s1 = ColorThief(tempDir+"/t1.png")
                s2 = ColorThief(tempDir+"/t2.png")
                if s1.get_color(quality=TOLERANCE_COLORTHIEF) == s2.get_color(quality=TOLERANCE_COLORTHIEF):
                    cthief_result = True
                # cthief_result = (s1.get_color(quality=TOLERANCE_COLORTHIEF) == s2.get_color(quality=TOLERANCE_COLORTHIEF))

            if space_result and res_result and cthief_result:
                print(f1 + " may match " + f2)
                duplicates.append(f1 + " may match " + f2)

        except Exception as e:
            traceback.print_exc()
            shutil.rmtree(tempDir)
            print("\nAn error has occured. Exiting program.")
            sys.exit(1)

# Print number of duplicates and execution time
print()
print(str(len(duplicates)) + " possible duplicates found.")

execution_time = lambda: str(round(end_time-start_time, 3))+" seconds"
if VERBOSE:
    end_time = time.time()
    print("Execution time: " + execution_time())

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

if VERBOSE:
    output_file.write("\n" + v_space + "\n")
    output_file.write(v_res + "\n")
    output_file.write(v_ct + "\n")
    output_file.write(v_space_t + "\n")
    output_file.write(v_ct_q + "\n")
    output_file.write("\nExecution time: " + execution_time() + "\n\n\n")

if len(duplicates) > 0:
    output_file.write(str(len(duplicates)) + " possible duplicates found:\n\n\n")
    for i in duplicates:
        output_file.write(i+"\n")
else:
    output_file.write("No possible duplicates found.\n")
    output_file.write("This doesn't mean there aren't any, only that I couldn't find any lol.\n")

# Print output file name to console
print("Output file saved to " + output_to_open + "\n")
output_file.close()

# Clean up the temporary working directory
shutil.rmtree(tempDir)

# Closing message
print("Job done.")
