# MRI Super Resolution

A high-resolution MRI dataset from http://old.mridata.org/fullysampled/knees is blurred to simulate fast, low-resolution acquisition. A deep network was trained to carry out super resolution on the blurred volumetric data. There are 19 patients total, and 16 were used for training and validation while the remaining three were used for testing.

<p align="center"> 
![](volume_animations/mri_p6.gif)
</p>

## General approach

I implemented a resnet-like 3D super resolution network in Pytorch. I generated a training set of 32x32x32 volume blocks from the MRI data for each of the 19 patients, and trained/validated on the first 15 patients and tested on the last 4 patients. The network is fully convolutional, so it can be trained on small volumes and tested on any size volume.

The network I built generally followed the approach of "Enhanced Deep Residual Networks for Single Image Super-Resolution" (https://arxiv.org/abs/1707.02921 by Bee Lim, Sanghyun Son, Heewon Kim, Seungjun Nah, Kyoung Mu Lee), but adapted for 3D volume data. The residual block was composed of 64 3x3x3 conv kernels followed by a ReLu followed by another block of 64 3x3x3 conv kernels, and I used a total of 9 res blocks. (I wanted to use more, but this filled up the 12 GB of GPU memory I had available.) 

The original version of this network with MSE loss is implemented in one notebook, and in the other a version is implemented where the loss function is supplemented with a perceptual loss based on the first three convolutional layers of VGG16. The super resolution volumes are compared from the only MSE-loss network and the MSE + perceptual loss network, and I found that the perceptual loss indeed improves the resolution.

I also used the Fast AI toolbox as well (https://github.com/fastai by Jeremy Howard, Rachel Thomas, et al., a bit like Keras for Pytorch but with so much more), which has a nice data loader tool that comes with easy data augmentation. Fast AI also has a super resolution image demo with a resnet variant that I used as a scaffold for my network, as well as code for perceptual loss with VGG16 that I expanded upon.

## Conclusions

3D convolutional kernels are necessary to take full advantage of the structure of the input data. MSE loss with a typical resnet structure works to a degree, but adding a perceptual component with VGG16 activations further improves the super resolution output

### Note

I still have to post the changes I made to the FastAI data loader to make it work with volumetric data - I will do this shortly on a fork of the fastai repo.

