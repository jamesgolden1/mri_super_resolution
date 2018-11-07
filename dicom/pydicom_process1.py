
"""

James Golden
jamesgolden1@gmail.com

Task 1 - data manipulation

1. Read all the DICOM files in a directory
2. Build a 3D volume (3D numpy array) by sorting against each file’s Slice Location DICOM tag
in ascending order
3. Converting the data from the input data type to 32-bit float data type and normalize the 3D
volume to the range between 0.0 and 1.0
4. Export the normalized 3D volume (3D numpy array) into a hdf5 file

Inputs:
• --input-dicom, --i
path to input DICOM director

Outputs:
• --output-hdf5, --h
path to output hdf5 file

Run script from command line:
python pydicom_process1.py '/home/james/Documents/mri/dicom/P2/' 

returns:
/home/james/Documents/mri/dicom/P2.hdf5

JRG
10/07/2018
"""

# Imports

import sys, os

from os.path import dirname, join
from pprint import pprint

import numpy as np

import pydicom
from pydicom.data import get_testdata_files
from pydicom.filereader import read_dicomdir

import glob

import h5py

def build_3d_hdf5(dicom_folder):

    # Get names of image files
    image_files =glob.glob(dicom_folder+'/*.mag')

    # Use pydicom to read image files
    slices_2d_unsorted = [pydicom.dcmread(image_file) for image_file in image_files]

    # Build empty array to hold images
    im_array_sorted = np.zeros([list(np.shape(slices_2d_unsorted[0].pixel_array))[0],
                                list(np.shape(slices_2d_unsorted[0].pixel_array))[1],
                                len(slices_2d_unsorted)])

    # Get sorted image location
    sorted_loc = []
    for ii in range(len(slices_2d_unsorted)):
        sorted_loc.append(slices_2d_unsorted[ii].get('SliceLocation'))
    # plt.plot(sloc,marker='x')

    # Get the sorted index for images
    sorted_loc_arg = np.argsort(sorted_loc)

    # Build new array with pixel_array data as float32 from sorted images 
    for ii in range(len(slices_2d_unsorted)):
        im_array_sorted[:,:,ii] = (slices_2d_unsorted[sorted_loc_arg[ii]].pixel_array).astype('float32')
    
    # Scale data to range of 0.0 - 1.0
    im_array_sorted -= np.min(im_array_sorted[:])
    im_array_sorted *= 1.0/np.max(im_array_sorted[:])
    
    # Get the dicom folder name for the hdf5 file name
    hdf5_name = os.path.basename(os.path.normpath(dicom_folder)) + '.hdf5'
    
    # Create the hdf5 folder name by going up two directories (may change due to file layout)
    hdf5_full_name = os.path.dirname(os.path.dirname(dicom_folder)) + '/' + hdf5_name
    
    # Create the hdf5 file, add image data, close to save
    hf = h5py.File(hdf5_full_name, 'w')
    hf.create_dataset('data1', data = im_array_sorted)
    hf.close()

    return hdf5_full_name

# Get dicom folder name from command line
dicom_folder_input = sys.argv[1]

# Run function to save hdf5 file
hdf_folder_output = build_3d_hdf5(dicom_folder_input)

print(hdf_folder_output)
