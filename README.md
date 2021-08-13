Short script that analyses a fluorescent image to calculate the percent of cells visible that have been stained by a green Fluorescent dye. The code looks for green in RGB values, and can be changed as needed. The code does the following:

1. Since expected magnification is large enough, sparse unlit cells within a properly stained cell should be counted as stained, so a Gaussian Blur is applied.
2. Pixels above a certain threshold brightness of desired channel (default is Green) are counted as lit cells.
3. Gain on the image is then increased significantly so all the imaged cells (stained and unstained) can be visible. 
4. Pixels above a certain threshold brightness of desired channel (default is Green) are counted as total cell area.
5. The percent of cell areas that have been stained can then be calculated by dividing the number of pixels in step 2 by the total area of all cells from step 5.
