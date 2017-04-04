#!/usr/bin/env python
"""
Collection of utility functions
"""
import os
import sys
import glob
import shutil
import subprocess

def run(cmd):
    """
    Runs command in default shell, returning the return code. And logging the
    output. It can take a the cmd argument as a string or a list. If a list is
    given, it is joined into a string.
    """
    if type(cmd) is list:
        this_cmd = ' '.join(cmd)
    else:
        this_cmd = cmd

    p = subprocess.Popen(this_cmd, shell=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
    out, err = p.communicate()
    return p.returncode, out, err

def merge_ciftis(masks_path, output_loc):
    command = "wb_command -cifti-merge {} -cifti {}"

    masks = [mask for mask in glob.glob(os.path.join(masks_path,
             '*.dscalar.nii'))]

    if not masks:
        sys.exit("No masks found in {}".format(masks_path))

    ciftis = " -cifti ".join(masks)
    command = command.format(output_loc, ciftis)
    run(command)

def prep_masks(nifti_dir, output_dir, smoothing):
    # Optional dilation can go here, before or after smoothing

    base_command = 'wb_command -volume-smoothing {mask} {smoothing} {output}'

    for nii_mask in glob.glob(os.path.join(nifti_dir, '*.nii*')):
        old_name = os.path.basename(nii_mask)
        new_name = os.path.join(output_dir, old_name)
        command = base_command.format(mask=nii_mask, smoothing=smoothing,
                output=new_name)
        run(command)

def project_to_surfaces(mni_fmri, output_dir, hcp_data):
    file_name = remove_extension(mni_fmri)
    output_name = file_name + '.dscalar.nii'
    output_dscalar = os.path.join(output_dir, output_name)
    command = ['ciftify_a_nifti', '--hcp-subjects-dir {}'.format(hcp_data),
            mni_fmri, output_dscalar]

    return_val, output, error = run(command)
    if return_val:
        print("output: {} error: {}".format(output, error))
        sys.exit(1)

    set_cifti_map_name(output_dscalar, file_name)

def set_cifti_map_name(cifti, name, index=1):
    command = "wb_command -set-map-names {} -map {} {}".format(cifti, index,
            name)
    run(command)

def remove_extension(file_name):
    return file_name.replace('.nii', '').replace('.gz', '')

class TempDir(object):
    def __init__(self):
        self.path = None
        return

    def __enter__(self):
        self.path = tempfile.mkdtemp()
        return self.path

    def __exit__(self, type, value, traceback):
        if self.path is not None:
            shutil.rmtree(self.path)
