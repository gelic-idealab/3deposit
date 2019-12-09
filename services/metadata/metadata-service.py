import os
import json
import logging
import shutil
import zipfile
import subprocess
import requests
import time
import yaml
import copy
import trimesh
import numpy as np
from flask import Flask, request, jsonify
from pymediainfo import MediaInfo as mi
# https://pymediainfo.readthedocs.io/en/stable/


'''
Flask app that generates & harvests metadata from 3d media,
handles POST requests with media payload, responds with metadata.
'''

app = Flask(__name__)

filename_360_video = ''

# logging boilerplate
service_name = str(os.path.basename(__file__))
logfile = 'service.log'
logging.basicConfig(level=logging.DEBUG, filename=logfile)
logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logging.info(f'Starting {service_name}...')

@app.route('/log', methods=['GET'])
def log_handler():
    try:
        with open(logfile, 'r') as f:
            resp = f.read()
            return jsonify({'logfile': str(resp)})
    except Exception as emsg:
        return jsonify({'emsg': str(emsg)})


@app.route('/', methods=['POST', 'GET'])
def handler():

    if request.method == 'POST':

        try:
            # unpack request data
            data = json.loads(request.form.get('data'))
            did = data.get('deposit_id')
            media_type = data.get('media_type')

            # deposit_form_metadata = data.get('metadata')

            logging.info(f"POST request for deposit_id: {did}, data: {data}")

            # unzip file payload
            file = request.files.get('file')
            if file and did:
                fzip = did
                file.save(fzip)

                extracted_files_to_delete_later = []

                if media_type == 'model':
                    zipped_model_file = fzip   # Path to zipped model file from which to gather metadata
                    base_model_file_path = ''

                    all_model_metadata = unzip_and_extract_model_metadata(zipped_model_file, base_model_file_path, extracted_files_to_delete_later)
                    logging.debug(f'all_model_metadata: {all_model_metadata}')

                    all_keys = list(all_model_metadata.keys())
                    for k in all_keys:
                        if '.' in k:
                            k_new = k.replace('.', '_')
                            all_model_metadata[k_new] = all_model_metadata.pop(k)

                    logging.debug(f'all_model_metadata replaced: {all_model_metadata}')

                    return jsonify({"deposit_id": did, "technical_metadata": all_model_metadata})


                elif media_type == 'video':
                    with zipfile.ZipFile(fzip, 'r') as zip_ref:
                        filename_360_video = zip_ref.namelist()[0]
                        logging.debug(f'filename_360_video: {filename_360_video}')
                        zip_ref.extract(filename_360_video)
                        extracted_files_to_delete_later.append(filename_360_video)

                    exiftool_dir = 'Image-ExifTool-11.65'   # Example: exiftool_dir = '/path/to/exiftool/toplevel/directory/Image-ExifTool-11.65'

                    mediainfo_metadata = get_mediainfo_metadata(filename_360_video)
                    spherical_metadata = get_360_metadata(filename_360_video, exiftool_dir)

                    metadata_dict = {}

                    if mediainfo_metadata is not None:
                        metadata_dict.update( mediainfo_metadata )

                    if spherical_metadata is not None:
                        metadata_dict.update( {len(metadata_dict) : spherical_metadata} ) # len(metadata_dict) determines the next key/index to use

                    if mediainfo_metadata is None and spherical_metadata is None:
                        return jsonify({"emsg": "No media metadata information was found for this file."})

                    return jsonify({"deposit_id": did, "technical_metadata": metadata_dict})


                elif media_type == 'vr':
                    zipped_vr_file = fzip   # Path to zipped vr app from which to gather metadata
                    base_vr_path = ''

                    all_vr_metadata = unzip_and_extract_vr_metadata(zipped_vr_file, base_vr_path, extracted_files_to_delete_later)
                    logging.debug(f'all_vr_metadata: {all_vr_metadata}')

                    all_keys = list(all_vr_metadata.keys())
                    for k in all_keys:
                        if '.' in k:
                            k_new = k.replace('.', '_')
                            all_vr_metadata[k_new] = all_vr_metadata.pop(k)

                    logging.debug(f'all_vr_metadata replaced: {all_vr_metadata}')

                    return jsonify({"deposit_id": did, 'technical_metadata': all_vr_metadata})


        except Exception as emsg:
            logging.error(str(emsg))
            return jsonify({'emsg': str(emsg)})

        finally:
            if os.path.exists(did):
                os.remove(did)
            if os.path.exists(fzip):
                os.remove(fzip)
            if len(extracted_files_to_delete_later) > 0:
                for fdel in extracted_files_to_delete_later:
                    if os.path.exists(fdel):
                        if os.path.isdir(fdel):
                            shutil.rmtree(fdel)
                        else:
                            os.remove(fdel)


def get_mediainfo_metadata(media_file):
    """
    Function to extract the general video and audio metadata from a media file (e.g., MP4).
    This function makes use of the MediaInfo library via the 'pymediainfo' Python package.

    # For Later:
    May want to use "track_type, index" as keys later, since that would be useful to users
    to see what type of track each index represents (e.g., "General 0," "Video 1," "Audio 2").
        E.g.:   md_dict.update( { (temp_track_id, track.track_type) : d } )


    :param media_file: Path and filename of the media file (e.g., an MP4 file) from which
                       to extract MediaInfo metadata.

    :return md_dict: Dictionary of mediainfo metadata for the given media file, if existent.
                     Otherwise, return None.
    """

    try:
        m = mi.parse(media_file)

        md_dict = {}

        for (index, track) in enumerate(m.tracks):
            d = track.to_data()
            md_dict.update( { index : d } )

        return md_dict

    except Exception as emsg:
        logging.error(emsg)
        return None


def get_360_metadata(mp4_file, path_to_exif_toolkit):
    """
    Function to gather 360 spherical metadata from an MP4 file. This function uses the ExifTool
    kit/package created by Phil Harvey: https://www.sno.phy.queensu.ca/~phil/exiftool/

    :param mp4_file: Path and filename of a 360 MP4 file from which to extract metadata.
    :param path_to_exif_toolkit: Path to the ExifTool directory installed on your machine.
                                 Should be named something like, "Image-ExifTool-11.65".

    :return spherical_data_dict: Dictionary of sphereical metadata parameters and their values
                                 for the given MP4 file, if existent. Otherwise, returns None.
    """

    exiftool_exe = os.path.join(path_to_exif_toolkit, 'exiftool' )

    get_360_info = subprocess.run( [exiftool_exe, "-a", "-u", "-g1", mp4_file], stdout=subprocess.PIPE)

    output_360_info = str(get_360_info.stdout)

    try:
        spherical_start = output_360_info.find('XMP-GSpherical') + len('XMP-GSpherical ----')
        spherical_end = output_360_info.find('----', spherical_start)
        spherical_data_extract = output_360_info[spherical_start : spherical_end]
        spherical_data = spherical_data_extract.split('\\n')
        spherical_data_clean = [i.replace(' ','') for i in spherical_data[1:-1]]

        spherical_data_dict = {}
        for s in spherical_data_clean:
            s_k = s.split(':')[0]
            s_v = s.split(':')[1]
            spherical_data_dict.update( {s_k : s_v} )

        spherical_data_dict.update( {"track_type" : "XMP-GSpherical"} )

        return spherical_data_dict

    except:
        return None



def unzip_and_extract_model_metadata(model_zip_file, unzip_path, extracted_files_list):
    """
    Function to unzip a 3D model file and extract all of the metadata for each of the unzipped files
    (including further zip files within the original zip file).

    :param model_zip_file: Path and filename of zipped model file from which to extract metadata.
    :param unzip_path: Current working path to which the zipped file should be unzipped.
    :param extracted_files_list: List of files that have been extracted (and to delete later)

    :reutrn all_file_metadata: Dictionary of all files in uncompressed zip file, along with the metadata
                               associated with each file, including model-specific metadata if the file
                               is of a model type (e.g., gltf, glb, obj, stl).
    """

    logging.info(f'Exctracting file: {model_zip_file}')
    with zipfile.ZipFile(model_zip_file, 'r') as zip_ref:
        filename_list = zip_ref.namelist()
        logging.info(f'File list: {filename_list}')
        for fn in filename_list:
            zip_ref.extract(fn, path=unzip_path)

    supported_3d_mesh_types = ['gltf','glb','obj','stl'] # add more

    all_file_metadata = {}

    for fn in filename_list:
        logging.debug(fn)
        fn_path = os.path.join(unzip_path, fn)
        logging.debug(fn_path)
        extracted_files_list.append(fn_path)

        # Clear previous properties
        gltf_metadata = None
        mesh_metadata = None
        file_metadata = None
        animated = False

        file_metadata = get_general_file_metadata(fn_path)

        if file_metadata["ext"] is not None:
            if file_metadata["ext"].lower() == "gltf" or file_metadata["ext"].lower() == "glb":
                gltf_metadata = get_3d_model_gltf_metadata(fn_path, file_metadata)

                if gltf_metadata is not None:
                    if gltf_metadata['animated']:
                        animated = True

            # Check if extension is in supported type list (OR, could simply TRY for all file to see if it can be loaded)
            if file_metadata["ext"] in supported_3d_mesh_types:
                mesh_metadata = get_3d_model_mesh_metadata(fn_path, file_metadata, animated)

        metadata_dict = {}

        if file_metadata is not None:
            metadata_dict.update( {"General properties" : file_metadata} )

        if gltf_metadata is not None:
            metadata_dict.update( {"GLTF metadata" : gltf_metadata} )

        if mesh_metadata is not None:
            metadata_dict.update( {"Mesh metadata" : mesh_metadata} )

        all_file_metadata.update( {fn_path : metadata_dict} )

        # Now check if the file was a zipped file, and if so, recursively gather subzipped file metadata
        if file_metadata["ext"] == "zip":
            zipfile_root = '/'.join(file_metadata['file_tree_path'].split('/')[0:-1])
            subzip_metadata = unzip_and_extract_model_metadata(fn_path, zipfile_root, extracted_files_list)
            for subzip_file in subzip_metadata:
                logging.debug('subzip iteration')
                all_file_metadata.update( {subzip_file : subzip_metadata[subzip_file]} )

    logging.debug(f'all_file_metadata: {all_file_metadata}')
    return all_file_metadata


def get_general_file_metadata(in_file):
    """
    Function to extract the general file metadata/properties from a file (e.g., size, date modified, etc.).
    Note that this does not need to actually be a "3D" type file. It can be any file (or directory).

    :param in_file: Path and filename of the file from which to extract generic metadata.

    :return file_info_dict: Dictionary of file metadata for the given file; otherwise, return None.
    """

    try:
        (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(in_file)  # Example output:  os.stat_result(st_mode=33204, st_ino=5522179, st_dev=64513, st_nlink=1, st_uid=1000, st_gid=1000, st_size=28869, st_atime=1570141042, st_mtime=1562097398, st_ctime=1570141042)

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
            file_info_dict.update({"file_tree_path":in_file})

            if in_file.endswith('/'): # means it's a directory
                dirname = in_file.split('/')[-2]
                file_info_dict.update({"directory_name":dirname})
                file_info_dict.update({"ext":None})

            else:
                filename = in_file.split('/')[-1]    # in case the full path is given, get just the file of interest name
                file_info_dict.update({"filename":filename})
                file_ext = filename.split('.')[-1] # use this to "assume" filetype (since other general libraries for determing filetype tend to think that 3d files are just text files...)
                if file_ext != '':
                    file_info_dict.update({"ext":file_ext})
                else:
                    file_info_dict.update({"ext":None})

        except Exception as emsg:
            logging.error("EXCEPTION:", str(emsg))
            # print("Problem getting file path, name, and extension.")
            file_info_dict.update({"file_tree_path":None})
            file_info_dict.update({"filename":None})
            file_info_dict.update({"ext":None})

        return file_info_dict

    except Exception as emsg:
        logging.error("EXCEPTION:", str(emsg))
        return None



def get_3d_model_gltf_metadata(gltf_file, file_info_dict):
    """
    Function to get the GLTF/GLB-related metadata from a GLTF or GLB file. In a GLTF file,
    this is the data contained within the GLTF file itself. In the case of a GLB file, this
    is the header information from the file (which, by no coincidence, is essentially the
    same as the data in its corresponding GLTF file.)

    :param gltf_file: Path and filename of a 3D model in GLTF from which to extract metadata.
    :param file_info_dict: Dictionary of generic file metadata for the file.

    :return gltf_data_dict: Dictionary of GLTF metadata parameters and their values
                            for the given file, if existent. Otherwise, returns None.
    """

    if file_info_dict["ext"].lower() == "gltf": # Get entire file info
        try:
            with open(gltf_file, 'rb') as gltf:
                gltf_data_dict = json.load(gltf)

            if "animations" in gltf_data_dict.keys():
                gltf_data_dict.update({'animated':True})    # Add "animated" metadata field as True
                # Remove super long metadata fields
                long_metadata_fields = ['accessors', 'animations', 'meshes', 'nodes'] # For an example animated file, these were at least 1000 lines each (accessors was 15,000 lines)
                for lmf in long_metadata_fields:
                    gltf_data_dict.pop(lmf)
            else:
                gltf_data_dict.update({'animated':False})   # Add "animated" metadata field as False

            return gltf_data_dict

        except Exception as emsg:
            logging.error("EXCEPTION:", str(emsg))
            return None

    elif file_info_dict["ext"].lower() == "glb": # Get header info
        # Not sure if string search below will work for ALL glb files...
        try:
            with open(gltf_file, 'rb') as glb:
                for l in glb:
                    header_line = l
                    break   # only need the first line

            header_line_str = str(header_line)

            json_start = header_line_str.find('JSON') + 4   # + 4 to get rid of 'JSON'
            json_end = header_line_str.find('}]} ,', json_start) + 3    # + 3 to keep the '}]}'
            json_data_extract = header_line_str[json_start : json_end]
            gltf_data_dict = json.loads(json_data_extract)

            return gltf_data_dict

        except Exception as emsg:
            logging.error("EXCEPTION:", str(emsg))
            return None


def get_3d_model_mesh_metadata(mesh_file, file_info_dict, is_animimated):

    """
    Function to extract the triangular mesh-related metadata from a 3D model file.

    This function makes use of the 'trimesh' Python package, which is an awesome
    tool for getting a lot of valuable properties from a variety of 3D model file
    types ('.stl', '.obj', '.glb', and more...), as well as exporting the file as
    a GLTF-formatted file (i.e., '.glb' file type).

    Source: https://github.com/mikedh/trimesh

    Example usage (based on usage on GitHub):

        >>> import numpy as np
        >>> import trimesh
        >>> m = trimesh.load('kirby_mario_fixed.obj')
        >>> m.vertices
        TrackedArray([[-0.04256,  0.02314,  0.05334],
                      [ 0.06496,  0.00356,  0.0877 ],
                      [-0.05824,  0.1355 , -0.11658],
                      ...
                      [-0.10954,  0.00496,  0.0792 ]])
        >>> m.is_watertight     # is the current mesh watertight?
        True
        >>> m.euler_number      # what's the euler number for the mesh?
        2

        # the convex hull is another Trimesh object that is available as a property
        # lets compare the volume of our mesh with the volume of its convex hull
        >>> print(m.volume / m.convex_hull.volume)
        0.8138045118070378

        >>> m.center_mass
        array([5.68660268e-18, 1.26368949e-17, 7.58213691e-18])

        # since the mesh is watertight, it means there is a
        # volumetric center of mass which we can set as the origin for our mesh
        >>> m.vertices -= m.center_mass

        >>> m.moment_inertia     # what's the moment of inertia for the mesh?
        array([[ 1.37703808e-04, -5.37003582e-07,  8.76083403e-08],
               [-5.37003582e-07,  1.21990603e-04,  4.54513592e-06],
               [ 8.76083403e-08,  4.54513592e-06,  1.48334150e-04]])


    :param mesh_file: 3D object file from which to extract metadata.
    :param file_info_dict: Dictionary of generic file metadata for the file.
    :param is_animimated: Boolean indicating if the model file is animated or not.

    :return mesh_data_dict: Dictionary containing all of the mesh-related metadata for the file.
    """

    try:
        m = trimesh.load(mesh_file)
    except Exception as emsg:
        logging.error("EXCEPTION:", str(emsg))
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

    logging.info(f'Exctracting file: {vr_zip_file}')
    with zipfile.ZipFile(vr_zip_file, 'r') as zip_ref:
        filename_list = zip_ref.namelist()
        logging.info(f'File list: {filename_list}')
        for fn in filename_list:
            zip_ref.extract(fn, path=unzip_path)

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
        if os.path.isdir(fn) and 2 < len(fn.split('/')) < 5:
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

    engine_used_to_generate_app, potential_supported_platforms, potential_supported_sdks = determine_engine_used(app_package_metadata)
    if engine_used_to_generate_app is not None:
        app_package_metadata.update( {"Engine used to generate VR application" : engine_used_to_generate_app} )
        app_package_metadata.update( {"Potentially supported platforms (based on engine used)" : potential_supported_platforms} )
        app_package_metadata.update( {"Potentially supported SDKs (based on engine used)" : potential_supported_sdks} )

        ## Get VR Headset support for Unreal Engine
        if engine_used_to_generate_app == 'Unreal Engine':
             # FOR THIS, WILL WANT TO USE USER FORM INPUT OF SDKS ENABLED FOR APP (INSTEAD OF "POTENTIAL_SDKS")
            compatibility_info = get_compatibility_info(potential_supported_sdks)
            if compatibility_info is not None:
                all_file_metadata["VR application compatibility"] = compatibility_info

    if app_package_metadata is not None:
        all_file_metadata.update( {"VR application package metadata" : app_package_metadata} )


    # Second, gather file-specific metadata
    for fn in filename_list:
        logging.debug(fn)
        fn_path = os.path.join(unzip_path, fn)
        logging.debug(fn_path)
        extracted_files_list.append(fn_path)

        # Clear previous properties
        file_metadata = None
        vr_asset_metadata = None
        mesh_metadata = None
        compatibility_info = None

        file_metadata = get_general_file_metadata(fn_path)

        if not os.path.isdir(fn_path):
            if file_metadata['filename'].endswith('.asset'): # Unfortunately, all '.uasset' files in Unreal example are unreadable (binary)
                vr_asset_metadata = get_vr_asset_settings(fn_path)

                if vr_asset_metadata is not None and "VR application compatibility" not in all_file_metadata.keys():
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
                logging.debug('subzip iteration')
                all_file_metadata.update( {subzip_file : subzip_metadata[subzip_file]} )


    logging.debug(f'all_file_metadata: {all_file_metadata}')

    return all_file_metadata


def get_vr_asset_settings(asset_file):

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

    :param asset_file: Path and filename of asset file for which to try getting metadata (i.e., the contents of the file)

    :return asset_settings_dict: Dictionary of contents saved from asset file.
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

    except Exception as emsg:
        logging.error("EXCEPTION:", str(emsg))
        asset_settings_dict = None

    # Last, remove the temporary file if it exists
    try:
        if os.path.isfile('temp_yaml.txt'):
            os.remove('temp_yaml.txt')
    except Exception as emsg:
        logging.error("EXCEPTION:", str(emsg))

    return asset_settings_dict


def determine_engine_used(app_pkg_metadata):
    """
    Function for determining VR engine with which VR app was created, based on directory tree structure and files.

    For Unreal, check for a few of the "Common Directories":
         https://docs.unrealengine.com/en-US/Engine/Basics/DirectoryStructure/index.html

    :param app_pkg_metadata: Dictionary containig the application-wide metdata for the top-level directories of the application.

    :return engine_used: Name of engine used to build application, as a string.
    :return known_platform_support: List of platforms known to be supported by the engine used.
    :return known_sdk_support: List of SDKs known to be supported by the engine used.

    """

    known_engine_SDK_support = {
        'Unity':['OpenVR', 'Oculus PC', 'Oculus Mobile', 'Windows Mixed Reality', 'OSVR'],
        'Unreal Engine':['OpenVR', 'Oculus PC', 'Oculus Mobile', 'Windows Mixed Reality', 'OSVR'],
        'CryEngine':['OpenVR', 'Oculus PC', 'OSVR'],
        'Godot':['OpenVR', 'Oculus PC', 'OSVR']
        }

    try:
        top_lvl_dir_list = [d for k in app_pkg_metadata['Top-level directories'].keys() for d in str(k).split('/')]
        top_lvl_dir_list = list(set(top_lvl_dir_list))
        # print(top_lvl_dir_list)

        if all( [folder in top_lvl_dir_list for folder in ['Config','Content','Saved']] ):
            engine_used = "Unreal Engine"
            known_platform_support = ['SteamVR', 'Oculus PC', 'Oculus Mobile', 'Windows Mixed Reality', 'Open Source Virtual Reality (OSVR)']
            known_sdk_support = known_engine_SDK_support[engine_used]

        elif all( [folder in top_lvl_dir_list for folder in ['Assets','Library','ProjectSettings']] ):
            engine_used = "Unity"
            known_platform_support = ['SteamVR', 'Oculus PC', 'Oculus Mobile', 'Windows Mixed Reality', 'Open Source Virtual Reality (OSVR)']
            known_sdk_support = known_engine_SDK_support[engine_used]

        else:
            # Currently have only determined general ways of assuming app-generation engine
            engine_used = None
            known_platform_support = None
            known_sdk_support = None

    except Exception as emsg:
        logging.error("EXCEPTION:", str(emsg))
        engine_used = None
        known_platform_support = None
        known_sdk_support = None

    return engine_used, known_platform_support, known_sdk_support



def get_compatibility_info(sdk_device_list):
    """
    Function for getting/determining device compatibility information for the VR application
    (e.g., platforms, headsets, engines).

    For now, we can ask in the user form what Engine was used (Unity or Unreal, or other), and if not Unity, then ask what SDKs were selected for support.
    Based on that information, we can then present what headsets would be compatible, since we would know the Engine and SDK (which for unity we will do automatically),
    together which inform us which headsets would be supported.

    Information from: https://en.wikipedia.org/wiki/Comparison_of_virtual_reality_headsets
    (* PLEASE CORRECT ME IF INFORMATION IN TABEL BELOW IS WRONG *)

    SDKs 				PLATFORM		HEADSETS

    OpenVR				SteamVR			HTC Vive, HTC Vive Pro, HTC Vive Cosmos, Razer OSVR HDK 1.4, Razer OSVR HDK 2,
    									Pimax 4K, Pimax 8K, Pimax 5K Plus, Deepoon VR E3, Dell Visor, Asus HC102, Acer AH101,
    									Windows Mixed Reality (WMR) headsets, HP WMR headset, Lenovo Explorer, Samsung Odyssey, Samsung Odyssey+,
    									StarVR One,  HP Reverb, Varjo VR-1, Valve headsets, Valve Index, Varjo VR-2, GFL Developer Kit

    Oculus PC SDK		Oculus PC 		Oculus Rift and Oculus Rift S

    Oculus Mobile SDK	Oculus Mobile	Oculus Standalone headsets, Samsung Gear VR, Oculus Go, Oculus Quest

    OSVR								Razer OSVR HDK 1.4, Razer OSVR HDK 2


    :param sdk_device_list: List of konwn SDKs supported for the particular VR application.

    :return compatibility_dict: Dictionary of VR devices/headsets known to be compatible with the VR application.

    """

    known_SDK_platform_support = {
        'OpenVR':'SteamVR',
        'Oculus':'Oculus',
        'Oculus PC':'Oculus PC',
        'Oculus Mobile':'Oculus Mobile',
        'OSVR':'OSVR'
        }

    known_SDK_headset_support = {
        'OpenVR':['HTC Vive', 'HTC Vive Pro', 'HTC Vive Cosmos', 'Razer OSVR HDK 1.4', 'Razer OSVR HDK 2', 'Pimax 4K',  'Pimax 8K', 'Pimax 5K Plus', 'Deepoon VR E3', 'Dell Visor', 'Asus HC102', 'Acer AH101', 'Windows Mixed Reality (WMR) headsets', 'HP WMR headset', 'Lenovo Explorer', 'Samsung Odyssey', 'Samsung Odyssey+', 'StarVR One', 'HP Reverb', 'Varjo VR-1', 'Valve headsets', 'Valve Index', 'Varjo VR-2', 'GFL Developer Kit'],
        'Oculus': {'Oculus PC' : ['Oculus Rift', 'Oculus Rift S'], 'Oculus Mobile' : ['Oculus Standalone headsets', 'Oculus Go', 'Oculus Quest', 'Samsung Gear VR']},
         # Not sure if OSVR will appear as "OSVR", "OSVRUnity", or "OSVR-Unity", as haven't added OSVR SDK to Unity registry yet to test.
        'OSVR':['Razer OSVR HDK 1.4', 'Razer OSVR HDK 2'],
        'OSVRUniy':['Razer OSVR HDK 1.4', 'Razer OSVR HDK 2'],
        'OSVR-Uniy':['Razer OSVR HDK 1.4', 'Razer OSVR HDK 2']
        }

    compatibility_dict = {'SDKs':copy.deepcopy(sdk_device_list)} # This should be SDKs, not platforms. For Unity, can be either Oculus, OpenVR, or OSVR.

    try:
        for sdk in sdk_device_list:
            if sdk == 'Oculus PC' or sdk == 'Oculus Mobile':
                sdk_fill = 'Oculus'
            else:
                sdk_fill = sdk

            if sdk_fill in known_SDK_platform_support.keys() or sdk_fill in known_SDK_headset_support.keys():
                compatibility_dict.update({sdk_fill:{}})
                try:
                    compatibility_dict[sdk_fill].update({ 'Platforms':known_SDK_platform_support[sdk_fill] })
                except Exception:
                    pass

                try:
                    compatibility_dict[sdk_fill].update({ 'Headsets':known_SDK_headset_support[sdk_fill] })
                except Exception:
                    pass

    except Exception as emsg:
        logging.error("EXCEPTION:", str(emsg))

    return compatibility_dict


if __name__ == '__main__':
    app.run()
