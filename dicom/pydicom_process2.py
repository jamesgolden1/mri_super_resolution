
"""

James Golden
jamesgolden1@gmail.com

Task 2 - simulating fast acquisitions

Your function takes the 3D volume from Task I and generates a new 3D volume
with the same matrix size but reduced image resolution using a Gaussian blurring filter (refer to
scipy.ndimage.gaussian_filter).

Inputs: 3D volume data, sigma for filter
Outputs: blurred 3D volume data

JRG
10/07/201
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

from scipy.ndimage import gaussian_filter

def blurring3d(input3d, sigma):
    
    return gaussian_filter(input3d, sigma, mode = 'reflect')

def blur_volume(dicom_folder):
    # Get names of image files
    print(dicom_folder)
    image_files =glob.glob(dicom_folder+'/*.mag')
    print(len(image_files))
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
    
    sigma_filt = 5.
    im_array_blurred = blurring3d(im_array_sorted, sigma_filt)
    
#    dtrainx = '/home/james/Documents/mri/batches_sc/train/p'+str(pf)
#    if not os.path.exists(dtrainx):
#        os.makedirs(dtrainx)
    # Get the dicom folder name for the hdf5 file name
    hdf5_name = os.path.basename(os.path.normpath(dicom_folder)) + '_blurred.hdf5'
    
    # Create the hdf5 folder name by going up two directories (may change due to file layout)
    hdf5_full_name = os.path.dirname(os.path.dirname(dicom_folder)) + '/' + hdf5_name
    
    # Create the hdf5 file, add image data, close to save
    hf = h5py.File(hdf5_full_name, 'w')
    hf.create_dataset('data1', data = im_array_sorted)
    hf.close()
    
    return hdf5_full_name


dicon_folder_input ='/home/james/Documents/mri/dicom/P2/'
#dicom_folder='/home/james/Documents/mri/dicom/P2/'
# Get dicom folder name from command line
#dicom_folder_input = sys.argv[1]

# Run function to save hdf5 file
im_array_blurred_hdf5 = blur_volume(dicon_folder_input)

#print(hdf_folder_output)

# Run the script from task 1b to generate .mag files for blurred images
#bashCommand = "python pydicom_process1b.py " + "'" + im_array_blurred_hdf5 + "'" 
##bashCommand = "python pydicom_process1b.py '/home/james/Documents/mri/dicom/P3/' "
#os.system(bashCommand)
