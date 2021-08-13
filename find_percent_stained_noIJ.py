'''
Goal of program:
	1. determine area of tissue stained and area of tissue in total
	2. compare ratio of tissue stained vs tissue unstained but present
Place green-stained images inside some directory and run with python 3
NOTE: ensure that there are only images of interest in selected directory. Other files will crash the program
Then select output format when promted:
	1. CSV file
	2. the file name and data output in the command line
Input images can be in most formats but only PNG/JPG/TIF have been tested
Program is used to detect areas of tissue that has been stained and unstained
If stain is not green, edit FLATTEN and IS_BLACK and ADJUST_CONTRAST functions
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

# Adjusts contrast by multiplying by some factor F. Takes RGB pixel as input and outputs RGB pixel
def adjust_contrast(p, f):
	n = p[1] * f
	if n > 255:
		n = 255
	elif n < 0:
		n = 0
	p[1] = int(n)
	return p

# Iterates through image IMAGE and adjusts contrast by factor C and brightness by factor B
# Note brightness adjustment is not implemented
def adjust_img(img, c=1, b=0):
	for row in img:
		for pixel in row:
			adjust_contrast(pixel, c)

# Load image named NAME from user selected directory and blurs
def load_img(directory, name):
	print (directory)
	return cv2.imread(directory + '/' + name)

# Adjust image IMG contrast by factor F and gaussian blur by 3x3. Returns contrasted and blurred image
def adjust_blur(img, f = 1):
	adjust_img(img, f)
	return cv2.blur(img, (3,3))

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
	1. load images into python, apply contrast adjustment (factor of 3 for img1, factor of 150 for img2)
	2. apply some gaussian blur
	3. find low and high peaks of the dual-peak distribution of blurred image
	4. find threshold between black and stained
	5. count number of black and stained pixels in blurred image
Here, all variables ending in 1 refer to image highlighting only stained areas, and variables ending in 2 refer to image highlighting all tissue areas
'''
def process_img(directory, name):
	img1 = load_img(directory, name)
	img2 = img1.copy()
	img1 = adjust_blur(img1, 3)
	img2 = adjust_blur(img2, 150)
	peaks1 = find_peaks(flatten(img1))
	peaks2 = find_peaks(flatten(img2))
	thresh1 = (peaks1[0] + peaks1[1]) / 2
	thresh2 = (peaks2[0] + peaks2[1]) / 2
	count1 = count_black(img1, thresh1)[0]
	count2 = count_black(img2, thresh2)[0]
	return [count1, count2, count1/count2]

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
	f.write("image name,pixels stained, pixels in total tissue, percent tissue stained\n")
	return f

# Helper function to write processed data (image name IMAGE_NAME and pixels stained NUM_PIXELS) into CSV file FILE
def write_to_output(file, image_name, num_pixels, num_pixels_tissue, percent_pixels):
	file.write(str(image_name) + "," + str(num_pixels) + "," + str(num_pixels_tissue) + "," + str(percent_pixels) + "\n")

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
		result[name] = process_img(image_directory, name)
	while True:
		to_csv = input("Would you like to save data to csv file (spreadsheet)? [Y/N]")
		if to_csv not in ["N", "n", "Y", "y"]:
			print ("Input not accepted. Please enter either 'Y' or 'N'")
		else:
			break
	if to_csv == "Y" or to_csv == "y":
		dest_file = create_output(ask_output_dest(image_directory))
		for key in result:
			write_to_output(dest_file, key, result[key][0], result[key][1], result[key][2])
			counter += 1
	elif to_csv == "N" or to_csv == "n":
		for key in result:
			print ("For image " + str(key) + " stained area (pixels) is " + str(
				result[key][0]) + "; total tissue area (pixels) is " + str(
				result[key][1]) + "; and percent stained is " + str(result[key][2]))
			counter += 1
	return counter

# Prints length of time program took to run and number of files processed
counter = initialize_all()
print ("Program took " + str(time.perf_counter() - begin) + " seconds to complete successfully")
print ("Processing completed on " + str(counter) + "files")
