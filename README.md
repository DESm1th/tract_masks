# tract_masks
A set of scripts and functions for producing masks from a JSON file of tract end points (which can be parsed from a MRML file).

## Requirements
	1. @edickie's ciftify module
	2. Connectome work bench
	3. FSL
	4. The following python modules: docopt, nibabel, numpy
	5. Also implicitly requires outputs from some commonly used pipelines (hcp, dtifit) for some functions to be run

## Contents

### tracts_cifti_mask.py:
	Can generate a cifti file of masks for each tract in the JSON file. This file is just a
	composition of the code in the other classes/util script.
		1. Uses tract_end_masks to make nifti masks for all end points for the tracts
		2. Smoothes the nifti masks by some given value
		3. Moves the smoothed nifti masks into MNI space
		4. Converts the masks to cifti format
		5. Merges the cifti masks into one single mask

### tract_end_masks.py:
	Will generate a set of simple nifti masks from the tract end points in the given JSON file

### mni_transform.py:
	Adapted from a function in Erin W. Dickie's ciftify/func2hcp module. Transforms a given fmri
	image into MNI space

### utils.py:
	A mess of useful functions.
