#!/usr/bin/env python
"""
Takes a JSON file of tract ends and creates a single cifti mask of them. This
script depends on the ciftify module and connectome workbench.

Usage:
    tracts_cifti_mask.py [options] <masked_image> <b0_map> <hcp_data> <tracts_json> <output_loc>

Arguments:
    <masked_image>              The image to be masked.
    <b0_map>                    A b0_map for the image being masked (e.g. a
                                *_b0_bet.nii.gz file produced by dtifit)
    <hcp_data>                  The full path to the subject's folder of outputs
                                from the hcp pipeline
    <tracts_json>               The JSON file of tracts and their start/end
                                points
    <output_loc>                The path to the location to store results

Options:
    --save_results              Retain all intermediate results
    --smoothing INT             The Sigma value to use during smoothing.
                                [default: 5]
    --cost_function STR         Cost function for FLIRT registration
                                [default: corratio]
    --dof INT                   Degrees of freedom for FLIR registration
                                [default: 12]
    --output_name STR           Name to give the output file. If not given, the
                                input file will be assumed to follow the datman
                                naming convention and be named as
                                <masked image>_masks.dscalar.nii

"""

import os
import glob

from docopt import docopt

import tract_end_masks as nii_masks
import mni_transform
import utils

def main(temp_results):
    arguments = docopt(__doc__)
    masked_image = arguments['<masked_image>']
    b0_map = arguments['<b0_map>']
    hcp_data = arguments['<hcp_data>']
    tracts_file = arguments['<tracts_json>']
    output_loc = arguments['<output_loc>']
    save_results = arguments['--save_results']
    smoothing = arguments['--smoothing']
    cost = arguments['--cost_function']
    dof = arguments['--dof']

    final_output = get_output_name(output_loc, arguments['--output_name'],
            masked_image)
    results_dir = get_results_dir(temp_results, output_loc, save_results)

    print("Generating tract end point masks.")
    nifti_mask_folder = make_output_folder(results_dir, 'nii_masks')
    nii_masks.generate_masks(masked_image, tracts_file, nifti_mask_folder)

    print("Smoothing tract end point masks with Sigma {}.".format(smoothing))
    smoothed_mask_folder = make_output_folder(results_dir,
            'nii_sm{}'.format(smoothing))
    utils.prep_masks(nifti_mask_folder, smoothed_mask_folder, smoothing)

    print("Moving smoothed masks to MNI space.")
    mni_folder = make_output_folder(results_dir, 'nii_MNI')
    transform_to_MNI(smoothed_mask_folder, mni_folder, b0_map, hcp_data,
            cost, dof)

    print("Converting MNI space masks to cifti format.")
    cifti_folder = make_output_folder(results_dir, 'cifti_masks')
    project_to_surfaces(mni_folder, cifti_folder, hcp_data)

    print("Merging individual cifti masks to one.")
    utils.merge_ciftis(cifti_folder, final_output)

def get_output_name(output_loc, user_arg, masked_image):
    if user_arg:
        final_name = user_arg
    else:
        base_name = os.path.basename(masked_image)
        final_name = utils.remove_extension(base_name) + '_masks.dscalar.nii'

    return os.path.join(output_loc, final_name)

def get_results_dir(temp_dir, perm_dir, save):
    if save:
        return perm_dir
    return temp_dir

def make_output_folder(output_loc, folder_name):
    new_path = os.path.join(output_loc, folder_name)
    if not os.path.exists(new_path):
        os.makedirs(new_path)
    return new_path

def transform_to_MNI(input_dir, output_dir, b0_map, hcp_data, cost, dof):
    for mask in glob.glob(os.path.join(input_dir, '*.nii*')):
        mni_transform.transform_to_MNI(mask, output_dir, cost, dof, hcp_data,
                b0_map)

def project_to_surfaces(input_dir, output_dir, hcp_data):
    for mask in glob.glob(os.path.join(input_dir, '*.nii*')):
        utils.project_to_surfaces(mask, output_dir, hcp_data)

if __name__ == "__main__":
    with utils.TempDir() as temp_results:
        main(temp_results)
