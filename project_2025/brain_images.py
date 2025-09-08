# created by Elena

from normalized_cut import * 
import os
import nibabel 
import gzip
# from nibabel.testing import data_path

from pathlib import Path
import numpy as np
import nibabel as nib
from skimage import io,img_as_ubyte

input_path = "C:/Users/elena/Documents/GitHub/operations_research/project_2025/images/PKG_Brain_Mets_Lung_MRI_Path_Segs_radiology_images/input"
output_path = "C:/Users/elena/Documents/GitHub/operations_research/project_2025/images/PKG_Brain_Mets_Lung_MRI_Path_Segs_radiology_images/output"

if not os.path.isdir(output_path):
    os.mkdir(output_path)

folder = os.listdir(input_path)

def to_uint8(data):
    data -= data.min()
    if data.max() != 0:
        data /= data.max()
    data *= 255
    return data.astype(np.uint8)


def nii_to_pngs(input_path, output_dir, rgb=False):
    output_dir = Path(output_dir)
    data = nib.load(input_path).get_fdata()
    print(data)
    _, num_slices, num_channels = data.shape
    for channel in range(num_channels):
        print("Looking at channel " + str(channel))
        slice_2d = data[:, :, channel]
        slice_2d = to_uint8(slice_2d)
        if rgb:
                slice_2d = np.stack(3 * [slice_2d], axis=2)
        # print(volume)
        output_path = output_dir / f'channel_{channel}.png'
        io.imsave(output_path, slice_2d)





for little_folders in folder:
    if not os.path.isdir(output_path+"/"+little_folders):
        os.mkdir(output_path+"/"+little_folders)
    for files_gz in os.listdir(input_path+"/"+little_folders):
        if not os.path.isdir(output_path+"/"+little_folders+"/"+files_gz[:-7]):
            os.mkdir(output_path+"/"+little_folders+"/"+files_gz[:-7])
        print("INPUT PATH")
        print(input_path + "/"+little_folders+"/"+files_gz)
        print("OUTPUT PATH")
        print(output_path + "/"+little_folders+"/"+files_gz[:-7])
        nii_to_pngs(input_path + "/"+little_folders+"/"+files_gz, output_path + "/"+little_folders+"/"+files_gz[:-7])   
        
