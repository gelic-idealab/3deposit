import os
from pymediainfo import MediaInfo as mi
import subprocess
import pprint
import json
import requests
# import logging
import zipfile
import time
import trimesh
import numpy as np


def main():
    """
    ## NOTES:
		- Use this as a sample app to get metadata for: https://github.com/Grainger-Engineering-Library/webvr-unity-src

		- Get at least very general info about repo: number of files, size of repo, etc., what engine was used to build it, metadata on assets, unreal, target hardware this is for, a "score" for the complexity or the app (based on maybe number of vertices), what hardware would be able to run it
			- For the build directory--not that interested in metadata for these files, but may want to at least get what was used to build it, and stats on filetypes (e.g., mainly .js files?), and how long the source code is, etc...very broad encompassing sorts of metadata
			- Depending on what the app is for, we will know what folders to look for

		- For VR apps, maybe consider getting the following info:
			- number of subdirectories
			- number of types of files
			- type of headset supported (e.g., Oculus Go), so you can filter by support

		- A-frame is an example of an app

		- Project settings
			- files containing presets that the user setup in their editor
			- may just make the contents of each file the entire metadata itself

		- "premis" field, or 'pbcore'

		- U. Oklahoma publishing about VR app metadata standards
			- look for bookchapther from conference
			- http://vrpreservation.oucreate.com/vr3d-metadata/

		- Edward's schemas:
			- https://github.com/Grainger-Engineering-Library/3deposit/tree/master/docs/metadata_templates


    ## TODO:

    ## DONE:

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

    # supported_3d_mesh_types = ['gltf','glb','obj','stl'] # add more

    all_file_metadata = {}

    # Get number of files in each base directory folder
    app_package_metadata = {}
    app_package_metadata.update( {"Total file/directory count" : len(filename_list)} )

    main_sub_directories = {}
    f_count, d_count, sum_size = 0, 0, 0

    for fn in filename_list:
        if os.path.isfile(fn):
            f_count +=1
        if os.path.isdir(fn):
            d_count +=1
        sum_size += os.path.getsize(fn)


        if os.path.isdir(fn) and 2 < len(fn.split('/')) < 4:
            print("DIRECTORY",fn)
            main_sub_directories.update( {fn:{}} )
            num_sub_files = 0
            subdir_sum_size = 0
            for f in os.walk(fn):
                num_sub_files += len(f[2])
                # subdir_sum_size += sum(os.path.getsize(f_i) for f_i in f[2])
            print("NUMBER FILES:", num_sub_files)
            # print("SUB-DIRECTORY SIZE:", subdir_sum_size)
            main_sub_directories[fn].update( {"File count":num_sub_files} )
            # main_sub_directories[fn].update( {"Directory size (bytes)":subdir_sum_size} )


    app_package_metadata.update( {"File count" : f_count} )
    app_package_metadata.update( {"Directory count" : d_count} )
    app_package_metadata.update( {"App size (bytes)" : sum_size} )
    app_package_metadata.update( {"Main sub-directories" : main_sub_directories} )

    pprint.pprint(app_package_metadata)
    exit()


    for fn in filename_list:
        # logging.debug(fn)
        fn_path = os.path.join(unzip_path, fn)
        # logging.debug(fn_path)
        extracted_files_list.append(fn_path)

        # Clear previous properties
        # gltf_metadata = None
        # mesh_metadata = None
        file_metadata = None
        # animated = False

        file_metadata = get_vr_file_metadata(fn_path)

        # if file_metadata["ext"] is not None:
        #     if file_metadata["ext"].lower() == "gltf" or file_metadata["ext"].lower() == "glb":
        #         gltf_metadata = get_3d_model_gltf_metadata(fn_path, file_metadata)
        #
        #         if gltf_metadata is not None:
        #             if gltf_metadata['animated']:
        #                 animated = True
        #
        #     # Check if extension is in supported type list (OR, could simply TRY for all file to see if it can be loaded)
        #     if file_metadata["ext"] in supported_3d_mesh_types:
        #         mesh_metadata = get_3d_model_mesh_metadata(fn_path, file_metadata, animated)

        metadata_dict = {}

        if file_metadata is not None:
            metadata_dict.update( {"General properties" : file_metadata} )

        # if gltf_metadata is not None:
        #     metadata_dict.update( {"GLTF metadata" : gltf_metadata} )

        # if mesh_metadata is not None:
        #     metadata_dict.update( {"Mesh metadata" : mesh_metadata} )

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
            file_info_dict.update({"file_tree_path":None})
            file_info_dict.update({"filename":None})
            file_info_dict.update({"ext":None})

        return file_info_dict

    except Exception as emsg:
        # logging.error("EXCEPTION:", str(emsg))
        return None


def get_vr_metadata(vr_file, file_info_dict, is_animimated):

    """
    Function to extract the VR-related metadata from a VR package.

	*** CURRENTLY JUST A COPY OF FUNCTION FROM 3D MODEL METADATA EXTRACT SCRIPT ***
	*** NOT ACTUALLY USEFUL RIGHT NOW ***

    """

    try:
        m = trimesh.load(vr_file)
    except Exception as emsg:
        print("EXCEPTION:", str(emsg))
        return None

    mesh_data_dict = {}

    def get_mesh_obj_attrs(mesh, anim):
        attr_dict = {}

        # Get all mesh metadata for STILL objects only (animated files will overload system)
        if not anim:    # For animations, this gets stuck when getting the "bounding_box_oriented" attribute
            for a in dir(mesh):
                if not a.startswith('_'):  # and a in mesh_attr_list:
                    try:
                        if not callable(getattr(mesh, a)):
                            json.dumps( {a : getattr(mesh, a)} )   # Check to see if it can be serialized (e.g., not a numpy array or unfamiliar object)
                            attr_dict.update( {a : getattr(mesh, a)} )
                    except Exception:
                        try:
                            if type(getattr(mesh, a)) == np.ndarray: # If it's a numpy array, but a small one, keep it (e.g., 'centroid')
                                if getattr(mesh, a).size <= 20:
                                    attr_dict.update( { a : str(getattr(mesh, a)) } )

                            if a == 'triangles':
                                attr_dict.update( { "num_triangles" : len(getattr(mesh, a)) } )

                            if a == 'vertices':
                                attr_dict.update( { "num_vertices" : len(getattr(mesh, a)) } )

                            else:
                                continue
                        except Exception:
                            continue

        elif anim:
            # List of reasonably-sized attributes to gather from animated GLTF models (as certain other attributes will cause the process to stall if you try to get them (e.g., all "bounding_" attrs))
            anim_attrs = ['bounds', 'camera', 'camera_transform', 'centroid', 'extents', 'is_empty', 'is_valid', 'metadata', 'scale', 'triangles', 'triangles_node', 'units']
            for a in anim_attrs:
                try:
                    json.dumps( {a : getattr(mesh, a)} )   # Check to see if it can be serialized (e.g., not a numpy array or unfamiliar object)
                    attr_dict.update( {a : getattr(mesh, a)} )
                except Exception:
                    try:
                        if type(getattr(mesh, a)) == np.ndarray: # If it's a numpy array, but a small one, keep it (e.g., 'centroid')
                            if getattr(mesh, a).size <= 20:
                                attr_dict.update( { a : str(getattr(mesh, a)) } )

                        if a == 'triangles':
                            attr_dict.update( { "num_triangles" : len(getattr(mesh, a)) } )

                        else:
                            continue

                    except Exception:
                        continue

        return attr_dict

    try:
        mesh_data_dict.update( get_mesh_obj_attrs(m, is_animimated) )
    except Exception:
        pass

    if file_info_dict["ext"].lower() in ["gltf", "glb"] and not is_animimated:
        # Make a dump of the current mesh objects and analyze those (Only for non-animated models!)
        mesh_dump = m.dump()
        for (index, obj) in enumerate(mesh_dump):
            try:
                mesh_data_dict.update( { "mesh object "+str(index) : get_mesh_obj_attrs(obj, is_animimated) } )
            except Exception:
                continue

    return mesh_data_dict


if __name__ == "__main__":
	main()
