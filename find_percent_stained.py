'''
Place green-stained images inside some directory and run with python 3
NOTE: ensure that there are only images of interest in selected directory. Other files will crash the program
Then select output format when promted:
	1. a CSV file can be generatre
	2. the file and print out the data in the command line
Input images can be in most formats but only PNG/JPG/TIF have been tested
Program is used to detect areas of tissue that has been stained and unstained
To determine ratio of stained to unstained images, two images must be used:
	1. an image of only stained area (edit min/max in ImageJ to be the same ~40-50)
	2. an image of all stained area (edit min/max in ImageJ to be 0)
Currently WIP to eliminate the imageJ steps
If stain is not green, edit FLATTEN and IS_BLACK functions
Tom Ding 2020 | tom.ding@berkeley.edu
'''
import cv2
import numpy as np
from matplotlib import pyplot as plt
from os import listdir
import time
import tkinter as tk
from tkinter import filedialog
import csv


# Set a time counter for time taken for code to run
begin = time.perf_counter()

# Load image named NAME from user selected directory
def load_img(name):
	img = cv2.imread("images/" + name)
	return cv2.blur(img,(3,3))

# Checks pixel A. only if value of A is less than N, the threshold value, A is considered to be black
def is_black(a, n):
	if a[1] < n:
		return True
	return False

# Takes image IMAGE, and some threshold THRESH (deafult to 110), and returns array: [number not black pixels, number black pixels]
def count_black(image, thresh=110):
	not_black = 0
	black = 0
	for row in image:
		for pixel in row:
			if is_black(pixel, thresh):
				black += 1
			else:
				not_black += 1
	return [not_black, black]

# Takes image IMAGE, a 2D array of triplets [R, G, B] and flattens to a 1D array where R and B are discarded and only G is kept. Order may not be kept
def flatten(image):
	combined = []
	for row in image:
		for pixel in row:
			combined += [pixel[1]]
	return combined

# Helper function for FIND_PEAKS(A). Takes in flattened array A, low starting peak estimate MIN_VAL, high starting peak estimate MAX_VAL
def find_peak_helper(a, min_val, max_val):
	left = []
	right = []
	for num in a:
		if max_val - num > num - min_val:
			left += [num]
		else:
			right += [num]
	new_min = sum(left) / len(left)
	new_max = sum(right) / len(right)
	if abs(new_min - min_val) <= 4 and abs(new_max - max_val) <= 4:
		return [new_min, new_max]
	else:
		return find_peak_helper(a, new_min, new_max)

# Given flattened array A, find center points for A, which is assumed to be a dual-peak distribution
def find_peaks(a):
	min_val = min(a)
	max_val = max(a)
	return find_peak_helper(a, min_val, max_val)

'''
Combines all above helper functions to take an image named NAME from selected directory and executes the following functions:
1. load image into python and apply some gaussian blur
2. find low and high peaks of the dual-peak distribution of blurred image
3. find threshold between black and stained
4. count number of black and stained pixels in blurred image
'''
def process_img(name):
	blur = load_img(name)
	peaks = find_peaks(flatten(blur))
	thresh = (peaks[0] + peaks[1]) / 2
	count = count_black(blur, thresh)
	return count[0]

# Asks user where their images are located. User must select a single directory
def ask_path():
	root = tk.Tk()
	root.withdraw()
	return filedialog.askdirectory(title="Select image directory")

# Asks user for where to save CSV file. Input is where to start looking for destination directory
def ask_output_dest(init_path='/'):
	root2 = tk.Tk()
	root2.withdraw()
	return filedialog.asksaveasfilename(initialdir = init_path,title = "Select output file/destination",filetypes = (("csv files","*.csv"),("all files","*.*")))

# Makes sure that the name of the output file is in CSV format, creates the file, opens it, and sets header. Takes DEST, file path with file as input
def create_output(dest):
	if dest[-4:] != ".csv":
		dest = dest + ".csv"
	f = open(dest, "w")
	f.write("image name,pixels stained\n")
	return f

# Helper function to write processed data (image name IMAGE_NAME and pixels stained NUM_PIXELS) into CSV file FILE
def write_to_output(file, image_name, num_pixels):
	file.write(str(image_name) + "," + str(num_pixels) + "\n")

'''
Function that runs all the helper functions in the correct order:
	1. asks user for directory with images
	2. processes all images in directory and saves in dictionary RESULT
	3. asks user if output should be command line print or CSV file
	4a. if CSV selected, asks for save file, creates file, writes to it
	4b. if CSV not selected, prints image and number pixels stained pairs
	5. ouputs the number of files printed/written to CSV file
'''
def initialize_all():
	counter = 0
	image_directory = ask_path()
	result = {}
	for name in listdir(image_directory):
		result[name] = process_img(name)
	while True:
		to_csv = input("Would you like to save data to csv file (spreadsheet)? [Y/N]")
		if to_csv not in ["N", "n", "Y", "y"]:
			print ("Input not accepted. Please enter either 'Y' or 'N'")
		else:
			break
	if to_csv == "Y" or "y":
		dest_file = create_output(ask_output_dest(image_directory))
		for key in result:
			write_to_output(dest_file, key, result[key])
			counter += 1
	elif to_csv == "N" or "n":
		for key in result:
			print ("For image " + str(key) + " stained area (pixels) is " + str(result[key]))
			counter += 1
	return counter

# Prints length of time program took to run and number of files processed
counter = initialize_all()
print ("Program took " + str(time.perf_counter() - begin) + " seconds to complete successfully")
print ("Processing completed on " + str(counter) + "files")











'''
------------------------------------------------------------------------------
 PLEASE IGNORE EVERYTHING BELOW - THEY ARE EARLIER TESTS AND OTHER TEST CASES
------------------------------------------------------------------------------


peaks = find_peaks(flatten(blur))
thresh = (peaks[0] + peaks[1]) / 2
print (thresh)
count2 = count_black(blur, thresh)
count = count_black(blur)
print(count)
print(count2)


flat = flatten(blur)
d = {}
for i in flat:
	d.setdefault(i, 0)
	d[i] += 1
print (d)

flat = flatten(cv2.imread("images/image_test.tif"))
flat2 = []
for i in flat:
	if i>120:
		flat2 += [i]

plt.hist(flat, bins = 255)
plt.show()




# Runs program and prints out the program return values
# image_directory = ask_path()
# for name in listdir(image_directory):
	# print ("For image " + name + " stained area (pixels) is " + str(process_img(name)))
	# counter += 1










plt.subplot(121),plt.imshow(img),plt.title('Original')
plt.xticks([]), plt.yticks([])
plt.subplot(122),plt.imshow(blur),plt.title('Blurred')
plt.xticks([]), plt.yticks([])
plt.show()




from PIL import Image, ImageEnhance, ImageFilter

img = Image.open("images/one_p.jpg")

img.show()

def adjust_contrast_brightness(image, contrast, brightness):
	contrast_enhancer = ImageEnhance.Contrast(image)
	img2 = contrast_enhancer.enhance(contrast)
	brightness_enhancer = ImageEnhance.Brightness(img2)
	img3 = brightness_enhancer.enhance(brightness)
	return img3

def count_pixel(image):
	print("not implemented")
'''
