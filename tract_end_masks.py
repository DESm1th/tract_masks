#!/usr/bin/env python
"""
Loads a JSON file containing a dictionary of tracts and the start and end
points for each fiber.

Usage:
    tract_end_masks.py [options] <base_image> <tracts_json> <output_loc>

Arguments:
    <base_image>                The path to the nifti that the mask is being
                                made for
    <tracts_json>               The path to a json file that was created from
                                a mrml file. Should contain a dictionary of
                                tracts, with each a list of each tracts starts
                                and end points for all the fibers

    <output_loc>                The location to store the created nifti masks.

Options:
    --allow-other               When true, tracts with the name 'other' will
                                be included in the results
"""

import os
import json

from docopt import docopt
import nibabel as nib
import numpy as np
import numpy.linalg as npl

def main():
    arguments = docopt(__doc__)
    base_image = arguments['<base_image>']
    tracts_file = arguments['<tracts_json>']
    output_loc = arguments['<output_loc>']
    allow_other = arguments['--allow-other']

    generate_masks(base_image, tracts_file, output_loc, allow_other)

def generate_masks(base_image, tracts_file, output_loc, allow_other=False):
    with open(tracts_file, 'r') as tracts_data:
        tracts = json.load(tracts_data)

    base_nifti = nib.load(base_image)
    shape = base_nifti.shape
    affine = base_nifti.affine

    for tract in tracts:
        if 'other' in tract.lower() and not allow_other:
            continue
        mask = create_mask_array(tracts[tract], shape, affine)
        mask_nii = nib.Nifti1Image(mask, affine)
        save_mask(output_loc, tract, mask_nii)

def create_mask_array(tract_ends, mask_shape, affine):
    mask_array = np.zeros((mask_shape[0], mask_shape[1], mask_shape[2], 1))

    start_voxels = mm_to_voxels(tract_ends['starts'], affine)
    fill_mask(mask_array, start_voxels)

    end_voxels = mm_to_voxels(tract_ends['ends'], affine)
    fill_mask(mask_array, end_voxels)

    return mask_array

def mm_to_voxels(mm_point_list, affine):
    voxels = nib.affines.apply_affine(npl.inv(affine), mm_point_list)
    return voxels

def fill_mask(mask, voxel_list):
    for voxel in voxel_list:
        x = int(round(voxel[0]))
        y = int(round(voxel[1]))
        z = int(round(voxel[2]))
        mask[x][y][z] = 1

def save_mask(output_path, tract_name, mask):
    output_file = os.path.join(output_path, "{}.nii".format(tract_name))
    nib.save(mask, output_file)

if __name__ == '__main__':
    main()
