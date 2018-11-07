
"""

James Golden
jamesgolden1@gmail.com

Task 1b - data manipulation

1. Read the DICOM files in the directory as a template
2. Build a 3D volume (3D numpy array) by sorting against each file’s Slice Location DICOM tag
in ascending order
3. Read the 3D volume stored in the hdf5 file and rescale this 3D volume to match the dynamic
range and data type (check pydicom.dataset.pixel_array.dtype) of the 3D volume read
in Step 2
4. Replace the 3D volume from Step 2 with the new one from Step 3 and save the results into
new DICOM files into the output DICOM directory

Inputs:
• --input-dicom, --i
• --input-hdf5, --h
path to input DICOM directory
path to input hdf5 file

Outputs:
• --output-dicom, --o
path to output DICOM directory

Run script from command line:
python pydicom_process1b.py '/home/james/Documents/mri/dicom/P3/' 

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
from pydicom.dataset import Dataset, FileDataset

import glob

import h5py

def build_3d_hdf5(dicom_folder):

    # Get names of image files
    image_files =glob.glob(dicom_folder+'/*.mag')
    print(len(image_files))
    # Use pydicom to read image files
    slices_2d_unsorted = [pydicom.dcmread(image_file) for image_file in image_files]
    
    # Build empty array to hold images
    im_array_sorted = np.zeros([list(np.shape(slices_2d_unsorted[0].pixel_array))[0],
                                list(np.shape(slices_2d_unsorted[0].pixel_array))[1],
                                len(slices_2d_unsorted)])

    # Get data type
    dicom_dtype = slices_2d_unsorted[0].pixel_array.dtype
    
    # Get sorted image location
    sorted_loc = []
    for ii in range(len(slices_2d_unsorted)):
        sorted_loc.append(slices_2d_unsorted[ii].get('SliceLocation'))
    # plt.plot(sloc,marker='x')

    # Get the sorted index for images
    sorted_loc_arg = np.argsort(sorted_loc)
#    print(sorted_loc_arg[:5])    
#    unsorted_loc_arg = np.argsort(sorted_loc_arg)
#    print(unsorted_loc_arg[:5])

    # Build new array with pixel_array data as float32 from sorted images 
    for ii in range(len(slices_2d_unsorted)):
        im_array_sorted[:,:,ii] = (slices_2d_unsorted[sorted_loc_arg[ii]].pixel_array).astype('float32')
    
    # Get the dicom folder name for the hdf5 file name
    hdf5_name = os.path.basename(os.path.normpath(dicom_folder)) + '.hdf5'
    
    # Create the hdf5 folder name by going up two directories (may change due to file layout)
    hdf5_full_name = os.path.dirname(os.path.dirname(dicom_folder)) + '/' + hdf5_name
    
    # Load the hdf5 file
    hf = h5py.File(hdf5_full_name, 'r')
    im_hf = hf.get('data1')
    # Convert hdf5 data to numpy array
    im_array_hf = np.array(im_hf)
              
    # Scale data to range of 0.0 - 1.0
    im_array_hf *= np.max(im_array_sorted[:])/np.max(im_array_hf[:])
    im_array_hf += np.min(im_array_sorted[:])
    im_array_hf = im_array_hf.astype(dicom_dtype)
    
    # Check that 
    if ~(np.max(im_array_hf) == np.max(im_array_sorted)):
        return "Max values differ"
    
    if ~(np.min(im_array_hf) == np.min(im_array_sorted)):
        return "Min values differ"
    # print(np.max(im_array_hf),np.max(im_array_sorted),np.min(im_array_hf),np.min(im_array_sorted))
    
    # Take unsorted slices as template for new dcm
    slices_2d_orig_sort = slices_2d_unsorted
    new_slice_path = os.path.dirname(os.path.dirname(dicom_folder)) 
    for ii in range(2):#len(slices_2d_unsorted)):
        # Need to copy first in order to be able to set values
        new_array = slices_2d_orig_sort[ii].pixel_array.copy()
        # Set the new array with the denormalized , originally sorted values
        new_array = im_array_hf[:,:,sorted_loc_arg[ii]]
        # Put in pixel data field
        slices_2d_orig_sort[ii].PixelData = new_array.tostring()
        # Save the new file
        new_slice_filename = new_slice_path + os.path.basename(os.path.normpath(dicom_folder)) + '_' + str(ii) + '_new.mag'
        
        slices_2d_orig_sort[ii].save_as(new_slice_filename)
    
    return new_slice_path

# Get dicom folder name from command line
dicom_folder_input = sys.argv[1]
#dicon_folder_input ='/home/james/Documents/mri/dicom/P2/'
# Run function to save hdf5 file
hdf_folder_output = build_3d_hdf5(dicom_folder_input)

print(hdf_folder_output)
