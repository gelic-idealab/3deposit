import os
# from pymediainfo import MediaInfo as mi
import subprocess
import pprint
import json
import requests
import logging
import zipfile
import time
import trimesh
import numpy as np
import yaml
from metadata_service_copy import get_3d_model_mesh_metadata


def main():
    """
    ## NOTES:
		- Use this as a sample app to get metadata for: https://github.com/Grainger-Engineering-Library/webvr-unity-src
		- A-frame is an example of an app
		- "premis" field, or 'pbcore'

		- U. Oklahoma publishing about VR app metadata standards
			- look for bookchapther from conference
			- http://vrpreservation.oucreate.com/vr3d-metadata/

		- Edward's schemas:
			- https://github.com/Grainger-Engineering-Library/3deposit/tree/master/docs/metadata_templates

    ## TODO:
        - Update/expand list of supported VR headsets known for each platform (e.g., Oculus Go)
        - What engine was used to build it (e.g., unreal, )
        - Target hardware the app is for (what hardware would be able to run it?)
        - *Depending on what the app is for, we will know what folders to look for
        - A "score" for the complexity or the app (based on maybe number of vertices)
        - Stats on filetypes (e.g., mainly .js files?),
        - How long the source code is, etc.

    ## DONE:
        - Grap top-level directory data
        - Fix format of Dates in file info metadata on all of files --> These are actually in OK format, but pprint displays them oddly when spaces are present in a string...
        - Check through /webvr-unity-src-master/Assets folder to find .obj files and run 3dmodel metadata extract script on those as well
        - Grab Headset info from project settings

    """

    extracted_files_to_delete_later = []

    zipped_vr_file = './webvr-unity-src-master.zip'   # Path to zipped model file from which to gather metadata
    # base_path = '/'.join(zipped_vr_file.split('/')[0:-1]) # set as base directory, or '' if already in working base direcotry
    base_path = ''

    all_vr_metadata = unzip_and_extract_vr_metadata(zipped_vr_file, base_path, extracted_files_to_delete_later)
    # logging.debug(f'all_vr_metadata: {all_vr_metadata}')

    all_keys = list(all_vr_metadata.keys())
    for k in all_keys:
        if '.' in k:
            k_new = k.replace('.', '_')
            all_vr_metadata[k_new] = all_vr_metadata.pop(k)

    # logging.debug(f'all_vr_metadata replaced: {all_vr_metadata}')

    metadata_json = json.dumps(all_vr_metadata)
    pprint.pprint(json.loads(metadata_json))

    return all_vr_metadata


def unzip_and_extract_vr_metadata(vr_zip_file, unzip_path, extracted_files_list):
    """
    Function to unzip a 3D model file and extract all of the metadata for each of the unzipped files
    (including further zip files within the original zip file).

    :param vr_zip_file: Path and filename of zipped VR app from which to extract metadata.
    :param unzip_path: Current working path to which the zipped file should be unzipped.
    :param extracted_files_list: List of files that have been extracted (and to delete later)

    :reutrn all_file_metadata: Dictionary of all files in uncompressed zip file, along with the metadata
                               associated with each file, including model-specific metadata if the file
                               is of a model type (e.g., gltf, glb, obj, stl).
    """

    # logging.info(f'Exctracting file: {vr_zip_file}')
    with zipfile.ZipFile(vr_zip_file, 'r') as zip_ref:
        filename_list = zip_ref.namelist()
        # logging.info(f'File list: {filename_list}')
        # COMMENT BELOW LINES BACK IN
        # for fn in filename_list:
        #     zip_ref.extract(fn, path=unzip_path)

    all_file_metadata = {}

    supported_3d_mesh_types = ['gltf','glb','obj','stl'] # add more

    # First, gather overall application file-tree information
    top_level_directories = {}
    f_count, d_count, sum_size = 0, 0, 0
    app_package_metadata = {"Total file/directory count" : len(filename_list)}
    for fn in filename_list:
        if os.path.isfile(fn):
            f_count +=1
        if os.path.isdir(fn):
            d_count +=1
        sum_size += os.path.getsize(fn)

        # Get number of files in each base directory folder
        if os.path.isdir(fn) and 2 < len(fn.split('/')) < 4:
            top_level_directories.update( {fn:{}} )
            num_sub_files = 0
            subdir_sum_size = 0
            for fx in os.walk(fn):
                num_sub_files += len(fx[2])
                for fi in fx[2]:
                    fi_path = os.path.join(fx[0],fi)
                    subdir_sum_size += os.path.getsize(fi_path)
            top_level_directories[fn].update( {"File count":num_sub_files} )
            top_level_directories[fn].update( {"Directory size (bytes)":subdir_sum_size} )

    app_package_metadata.update( {"File count" : f_count} )
    app_package_metadata.update( {"Directory count" : d_count} )
    app_package_metadata.update( {"App size (bytes)" : sum_size} )
    app_package_metadata.update( {"Top-level directories" : top_level_directories} )

    if app_package_metadata is not None:
        all_file_metadata.update( {"VR application package metadata" : app_package_metadata} )


    # Second, gather file-specific metadata
    for fn in filename_list:
        # logging.debug(fn)
        print(fn)
        fn_path = os.path.join(unzip_path, fn)
        # logging.debug(fn_path)
        extracted_files_list.append(fn_path)

        # Clear previous properties
        file_metadata = None
        vr_asset_metadata = None
        mesh_metadata = None
        compatibility_info = None

        file_metadata = get_vr_file_metadata(fn_path)

        if not os.path.isdir(fn_path):
            if file_metadata['filename'].endswith('.asset'):
                vr_asset_metadata = get_vr_asset_settings(fn_path)

                if vr_asset_metadata is not None:
                    # Look for VR headset metdata
                    if 'PlayerSettings' in vr_asset_metadata.keys():
                        if 'm_BuildTargetVRSettings' in vr_asset_metadata['PlayerSettings'].keys():
                            if 'm_Devices' in vr_asset_metadata['PlayerSettings']['m_BuildTargetVRSettings'][0].keys():
                                vr_devices = vr_asset_metadata['PlayerSettings']['m_BuildTargetVRSettings'][0]['m_Devices']
                                if not isinstance(vr_devices, list):
                                    vr_devices = [vr_devices]
                                compatibility_info = get_compatibility_info(vr_devices)
                                if compatibility_info is not None:
                                    all_file_metadata["VR application compatibility"] = compatibility_info

        # Check if 3d obj files in Assets directory
        if '/Assets/' in fn_path and not os.path.isdir(fn_path):
            if file_metadata["ext"].lower() in supported_3d_mesh_types:
                mesh_metadata = get_3d_model_mesh_metadata(fn_path, file_metadata, is_animimated=False)

        metadata_dict = {}

        if file_metadata is not None:
            metadata_dict.update( {"General properties" : file_metadata} )

        if vr_asset_metadata is not None:
            metadata_dict.update( {"Asset metadata" : vr_asset_metadata} )

        if mesh_metadata is not None:
            metadata_dict.update( {"Mesh metadata" : mesh_metadata} )

        all_file_metadata.update( {fn_path : metadata_dict} )

        # Now check if the file was a zipped file, and if so, recursively gather subzipped file metadata
        if file_metadata["ext"] == "zip":
            zipfile_root = '/'.join(file_metadata['file_tree_path'].split('/')[0:-1])
            subzip_metadata = unzip_and_extract_vr_metadata(fn_path, zipfile_root, extracted_files_list)
            for subzip_file in subzip_metadata:
                # logging.debug('subzip iteration')
                all_file_metadata.update( {subzip_file : subzip_metadata[subzip_file]} )


    # logging.debug(f'all_file_metadata: {all_file_metadata}')
    return all_file_metadata


def get_vr_file_metadata(app_file):
    """
    Function to extract the general file metadata from a VR app file (e.g., size, date modified, etc.).
    Note that this does not even need to actually be a "VR app" file. It can be any file (or directory).

    :param app_file: Path and filename of the file from which to extract generic metadata.

    :return file_info_dict: Dictionary of file metadata for the given file; otherwise, return None.
    """

    try:
        (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(app_file)
        # Example output:  os.stat_result(st_mode=33204, st_ino=5522179, st_dev=64513, st_nlink=1, st_uid=1000, st_gid=1000, st_size=28869, st_atime=1570141042, st_mtime=1562097398, st_ctime=1570141042)

        file_info_dict = {
            "mode" : mode,
            "ino" : ino,
            "dev" : dev,
            "nlink" : nlink,
            "uid" : uid,
            "gid" : gid,
            "size" : size,  # in bytes
            "atime" : time.ctime(atime),    # time of last access
            "mtime" : time.ctime(mtime),    # time of last modified
            "ctime" : time.ctime(ctime),    # The “ctime” as reported by the operating system. On some systems (like Unix) is the time of the last metadata change, and, on others (like Windows), is the creation time (see platform documentation for details).
            }

        try:
            file_info_dict.update({"file_tree_path":app_file})

            if app_file.endswith('/'): # means it's a directory
                dirname = app_file.split('/')[-2]
                file_info_dict.update({"directory_name":dirname})
                file_info_dict.update({"ext":None})

            else:
                filename = app_file.split('/')[-1]    # in case the full path is given, get just the file of interest name
                file_info_dict.update({"filename":filename})
                file_ext = filename.split('.')[-1] # use this to "assume" filetype (since other general libraries for determing filetype tend to think that 3d files are just text files...)
                if file_ext != '':
                    file_info_dict.update({"ext":file_ext})
                else:
                    file_info_dict.update({"ext":None})

        except Exception as emsg:
            # logging.error("EXCEPTION:", str(emsg))
            print("Problem getting file path, name, and extension.")
            print("EXCEPTION:", err)
            file_info_dict.update({"file_tree_path":None})
            file_info_dict.update({"filename":None})
            file_info_dict.update({"ext":None})

        return file_info_dict

    except Exception as err:
        print("EXCEPTION:",err)
        # logging.error("EXCEPTION:", str(emsg))
        return None


def get_vr_asset_settings(asset_file): #, file_info_dict):

    """
    Function to extract the metadata from an asset file (e.g., 'ProjectSettings.asset') of a VR package.

    Files in current testing case are in the format of YAML 1.1, and need to be handled using the method below.

    This function makes use of the 'yaml' Python library (installed via pip as 'pyyaml').
    A few notes on the current limitations of this library:
        1.  For some reason, this library has trouble reading all the '.asset' YAML files due to the header lines, and so
            can only work if these lines are removed. This seems to be a common reported bug that normally is resolved by
            using the "Loader=yaml.Loader" argument, but apparently this does not work for the '.asset' files here.
            So, for now, just create a temporary file without the header. (Which is necessary becasuse trying to read in just
            beyond the header from the original file as a stream also creates an error.)
        2.  The library can only read in files using UTF-8 encoding, but not latin-1 encoding, which is the case for some
            '.asset' YAML files here.
    """

    try:
        with open(asset_file, 'r') as f:
            new_yaml=[]
            for line in f:
                if line.startswith('%') or line.startswith('-'):
                    continue
                else:
                    new_yaml.append(line)
        with open('temp_yaml.txt', 'w') as tmp:
            for l in new_yaml:
                tmp.write(l)

        # Load the project settings into asset_settings_dict
        asset_settings_stream = open('temp_yaml.txt','r')
        asset_settings_dict = yaml.load(asset_settings_stream, Loader=yaml.Loader)
        asset_settings_stream.close()

    except Exception as err:
        print("EXCEPTION:", err)
        asset_settings_dict = None

    # Last, remove the temporary file if it exists
    try:
        if os.path.isfile('temp_yaml.txt'):
            os.remove('temp_yaml.txt')
    except Exception as err:
        print("EXCEPTION:",err)

    return asset_settings_dict


def get_compatibility_info(vr_device_list):
    """
    Function for getting/determining device compatibility information for the VR application
    (e.g., platforms, headsets, engines).

    Information from: https://en.wikipedia.org/wiki/Comparison_of_virtual_reality_headsets
    """

    known_engine_support = {
        'OpenVR':['Unity', 'Unreal Engine', 'CryEngine', 'Godot'],
        'Oculus':['Unity', 'Unreal Engine', 'CryEngine', 'Godot']
        }

    known_headset_support = {
        'OpenVR':['Razer OSVR HDK 1.4', 'Razer OSVR HDK 2'],
        'Oculus':['Oculus Rift', 'Oculus Rift S']
        }

    compatibility_dict = {'Platforms':vr_device_list}

    for dev in vr_device_list:
        compatibility_dict.update({dev:{}})
        try:
            compatibility_dict[dev].update({ 'Engines':known_engine_support[dev] })
        except Exception:
            pass

        try:
            compatibility_dict[dev].update({ 'Headsets':known_headset_support[dev] })
        except Exception:
            pass

    return compatibility_dict


if __name__ == "__main__":
	main()
