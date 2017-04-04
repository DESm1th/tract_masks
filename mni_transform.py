#!/usr/bin/env python
"""
This code was swiped and modified from edickie's ciftify/func2hcp.py module.

Takes an fMRI image and a b0 map and transform the image to MNI space.

Usage:
    mni_transform.py [options] <input_fmri> <b0_map> <hcp_data>

Arguments:
    <input_fmri>                A nifti image to transform
    <b0_map>                    A b0 map, such as the b0_bet.nii.gz produced
                                by dtifit
    <hcp_data>                  The full path to a subject's folder of outputs
                                from the hcp pipeline

Options:
    --cost_function STR         Cost function for FLIRT registration
                                [default: corratio]
    --dof INT                   Degrees of freedom for FLIRT registration
                                [default: 12]
"""
import os
import sys

from docopt import docopt

import utils

def main():
    arguments = docopt(__doc__)
    input_fmri = arguments['<input_fmri>']
    b0_map = arguments['<b0_map>']
    hcp_data = arguments['<hcp_data>']
    cost = arguments['--cost_function']
    dof = arguments['--dof']

    output_dir = os.path.join(os.path.dirname(input_fmri), 'MNI_space')
    transform_to_MNI(input_fmri, output_dir, cost, dof, hcp_data,
            b0_map)

def transform_to_MNI(input_fmri, output_loc, cost_function, degrees_of_freedom,
        hcp_data, b0_map):
    '''
    Transform the fMRI image to MNI space 2x2x2mm using FSL RegTemplate. An
    optional 3D MRI Image from the functional to use for registration
    '''
    ### these inputs should already be in the subject HCP folder
    T1w_image = os.path.join(hcp_data,'T1w', 'T1w_brain.nii.gz')
    T1w2MNI_mat = os.path.join(hcp_data, 'MNINonLinear', 'xfms',
            'T1w2StandardLinear.mat')
    T1w2MNI_warp = os.path.join(hcp_data, 'MNINonLinear', 'xfms',
            'T1w2Standard_warp_noaffine.nii.gz')

    MNI_template_2mm = get_MNI_brain()

    ### calculate the linear transform to the T1w
    func2T1w_mat =  os.path.join(output_loc, 'mat_EPI_to_T1.mat')

    ## calculate the fMRI to native T1w transform
    utils.run(['flirt',
        '-in', b0_map,
        '-ref', T1w_image,
        '-omat', func2T1w_mat,
        '-dof', str(degrees_of_freedom),
        '-cost', cost_function, '-searchcost', cost_function,
        '-searchrx', '-180', '180', '-searchry', '-180', '180', '-searchrz',
        '-180', '180'])

    ## concatenate the transforms
    func2MNI_mat = os.path.join(output_loc, 'mat_EPI_to_TAL.mat')
    utils.run(['convert_xfm','-omat', func2MNI_mat, '-concat', T1w2MNI_mat,
            func2T1w_mat])

    output_name = os.path.basename(input_fmri)
    output_file = os.path.join(output_loc, output_name)
    ## now apply the warp!!
    utils.run(['applywarp',
        '--ref={}'.format(MNI_template_2mm),
        '--in={}'.format(input_fmri),
        '--warp={}'.format(T1w2MNI_warp),
        '--premat={}'.format(func2MNI_mat),
        '--interp=spline',
        '--out={}'.format(output_file)])
    return output_file

def get_MNI_brain():
    try:
        fsl_dir = os.environ['FSLDIR']
    except KeyError:
        print("FSLDIR not found. Is FSL installed/loaded?")
        sys.exit(1)

    mni_brain = os.path.join(fsl_dir, 'data', 'standard',
            'MNI152_T1_2mm_brain.nii.gz')
    return mni_brain

if __name__ == '__main__':
    main()
