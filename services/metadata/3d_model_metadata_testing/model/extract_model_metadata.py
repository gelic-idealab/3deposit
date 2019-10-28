import os
from pymediainfo import MediaInfo as mi
import subprocess
import pprint
import json
import requests
import logging
import zipfile
import time
import trimesh
import numpy as np
import sys


def main():

    """
    ## Still to do/test
        # Set max allowable limit of number of unzip events to be 10 times (in case of a "compression bomb")
        # Test different file types and animated models

    ## DONE:
        # If zip file contains more zip files, then unzip them as well (e.g., this is present in the animated zip)
        # Add sub-directory searching (or see if it can already do that, depending on how the files are included in the filename_list;
            # For example, if they're like "./dir1/dir2/filename.txt", then don't need to worry about it I think...)
        # Add counts of vertices and triangles
        # Determine if animated or not, then say Yes or No
            # If so, then only get subset of mesh metadata from model file, to prevent stalling or overloading system

    """

    zipped_model_file = './anitest/model_anim.zip'   # Path to zipped model file from which to gather metadata
    base_model_file_path = './anitest/' # set as base directory, or '' if already in working base direcotry
    # base_model_file_path = '/'.join(zipped_model_file.split('/')[0:-1])
    print(zipped_model_file)
    print(base_model_file_path)
    exit()
    # unzip_counter = 0   # counter of number of times unzip occurs, to prevent problem in case of file with too many layers of compression

    # all_model_metadata = unzip_and_extract_model_metadata('test_subdir_file_tree.zip')
    # all_model_metadata = unzip_and_extract_model_metadata('test_subdir_subzip_file_tree.zip')

    all_model_metadata = unzip_and_extract_model_metadata(zipped_model_file, base_model_file_path)

    # all_model_metadata = unzip_and_extract_model_metadata('./anitest/model_anim.zip', '')     # USE THIS

    metadata_json = json.dumps(all_model_metadata)
    pprint.pprint(json.loads(metadata_json))


    # for k1 in all_model_metadata:
    #     print(k1)
    #     for k2 in all_model_metadata[k1]:
    #         print('\t',k2)
    #         for k3 in all_model_metadata[k1][k2]:
    #             print('\t\t',k3)
    #

    return all_model_metadata


def unzip_and_extract_model_metadata(model_zip_file, unzip_path):



    # Will this return any subdirectories and their contents, if present? --- YES!
    # If so, will want to iterate over all of them and get the metadata for them -- DONE!
    print("Exctracting file: ", model_zip_file)
    with zipfile.ZipFile(model_zip_file, 'r') as zip_ref:
        filename_list = zip_ref.namelist()
        print(filename_list)
        for fn in filename_list:
            # print(fn)
            zip_ref.extract(fn, path=unzip_path)

    supported_3d_mesh_types = ['gltf','glb','obj','stl'] # add more

    all_file_metadata = {}

    for fn in filename_list:
        print(fn)
        fn_path = os.path.join(unzip_path, fn)
        print(fn_path)

        # print(fn)

        # Clear previous properties
        gltf_metadata = None
        mesh_metadata = None
        file_metadata = None
        animated = False

        file_metadata = get_3d_model_file_metadata(fn_path)

        # May need to do this check for all files in the tree
        if file_metadata["ext"] is not None:
            if file_metadata["ext"].lower() == "gltf" or file_metadata["ext"].lower() == "glb":

                gltf_metadata = get_3d_model_gltf_metadata(fn_path, file_metadata)

                if gltf_metadata is not None:
                    # print(gltf_metadata)
                    # exit()
                    # print(gltf_metadata['animated'])
                    # exit()
                    if gltf_metadata['animated']:
                        # print("HERE- ANIMATED")
                        animated = True
                        # print("ANIMATED")
                        # exit()

            # if gltf_metadata is not None:
            #     metadata_dict.update( {"GLTF metadata" : gltf_metadata} )

            # Get mesh metadata for STILL objects only (animated files will overload system)
            # Can either check if extension is in supported type list,
            # OR simply TRY for all file to see if it can be loaded
            if file_metadata["ext"] in supported_3d_mesh_types:
                mesh_metadata = get_3d_model_mesh_metadata(fn_path, file_metadata, animated)


            # gltf_metadata = get_3d_model_gltf_metadata(fn)
            # mesh_metadata = get_3d_model_mesh_metadata(fn)

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
            # print(fn_path)
            zipfile_root = '/'.join(file_metadata['file_tree_path'].split('/')[0:-1])
            # print(zipfile_root)
            # exit()
            subzip_metadata = unzip_and_extract_model_metadata(fn_path, zipfile_root)
            # exit()
            for subzip_file in subzip_metadata:
                # print(subzip_file)
                # zipfile_root = '/'.join(file_metadata['file_tree_path'].split('/')[0:-1])
                # print(zipfile_root)
                # exit()
                # subzip_file_path = zipfile_root+'/'+subzip_file
                # print(subzip_file_path)

                # print(fn+'/'+k)
                all_file_metadata.update( {subzip_file : subzip_metadata[subzip_file]} )
                # pprint.pprint(all_file_metadata)
                # exit()

            # metadata_json = json.dumps(all_file_metadata)
            # pprint.pprint(json.loads(metadata_json))

    # metadata_json = json.dumps(all_file_metadata)
    #
    # pprint.pprint(json.loads(metadata_json))

    return all_file_metadata




def get_3d_model_file_metadata(model_file):
    """
    Function to extract the general file metadata from a model file (e.g., size, date modified, etc.).

    :param model_file: Path and filename of the model file (e.g., an OBJ or GLB file) from which
                       to extract metadata.

    :return file_info_dict: Dictionary of file metadata for the given media file; otherwise, return None.
    """

    try:

        (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(model_file)
        # Example output:  os.stat_result(st_mode=33204, st_ino=5522179, st_dev=64513, st_nlink=1, st_uid=1000, st_gid=1000, st_size=28869, st_atime=1570141042, st_mtime=1562097398, st_ctime=1570141042)
        # print("created: %s" % time.ctime(ctime))
        # print("last modified: %s" % time.ctime(mtime))

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
            file_info_dict.update({"file_tree_path":model_file})

            if model_file.endswith('/'): # means it's a directory
                dirname = model_file.split('/')[-2]
                file_info_dict.update({"directory_name":dirname})
                file_info_dict.update({"ext":None})

            else:
                filename = model_file.split('/')[-1]    # in case the full path is given, get just the file of interest name
                file_info_dict.update({"filename":filename})
                file_ext = filename.split('.')[-1] # use this to "assume" filetype (since other general libraries for determing filetype tend to think that 3d files are just text files...)
                if file_ext != '':
                    file_info_dict.update({"ext":file_ext})
                else:
                    file_info_dict.update({"ext":None})

        except Exception as emsg:
            print("EXCEPTION:", str(emsg))
            print("Problem getting file path, name, and extension.")
            file_info_dict.update({"file_tree_path":None})
            file_info_dict.update({"filename":None})
            file_info_dict.update({"ext":None})

        # for k,v in file_info_dict.items():
        #     print(k,v)

        return file_info_dict

    except Exception as emsg:
        print("EXCEPTION:", str(emsg))
        return None



def get_3d_model_gltf_metadata(gltf_file, file_info_dict):
    """

    :param gltf_file: Path and filename of a 3D model in GLTF from which to extract metadata.

    :return gltf_data_dict: Dictionary of GLTF metadata parameters and their values
                            for the given file, if existent. Otherwise, returns None.
    """

    if file_info_dict["ext"].lower() == "gltf": # Get entire file info
        # print("HERE")
        # exit()
        try:
            with open(gltf_file, 'rb') as gltf:
                gltf_data_dict = json.load(gltf)

            if "animations" in gltf_data_dict.keys():
                # print("ANIMATED")
                gltf_data_dict.update({'animated':True})    # Add "animated" metadata field as True

                # Remove super long metadata fields
                long_metadata_fields = ['accessors', 'animations', 'meshes', 'nodes'] # For an example animated file, these were at least 1000 lines each (accessors was 15,000 lines)
                for lmf in long_metadata_fields:
                    gltf_data_dict.pop(lmf)

            else:
                # print("NOT ANIMATED")
                gltf_data_dict.update({'animated':False})   # Add "animated" metadata field as False

                # sys.exit(1)
                # exit()

            return gltf_data_dict

        except Exception as emsg:
            print("EXCEPTION:", str(emsg))
            # exit()
            return None

        # print("HERE")
        # print(gltf_data_dict.keys())
        # exit()



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
            print("EXCEPTION:", str(emsg))
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

    """

    try:
        m = trimesh.load(mesh_file)

    except:
        return None

    mesh_data_dict = {}

    def get_mesh_obj_attrs(mesh, anim):
        attr_dict = {}

        if not anim:    # For animations, this gets stuck when getting the "bounding_box_oriented" attribute
            # print(dir(mesh))
            for a in dir(mesh):
                # print(a)
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
                # print(a)    # For animations, this gets stuck when getting the "bounding_box_oriented" attribute
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

    # if not is_animimated:
    try:
        mesh_data_dict.update( get_mesh_obj_attrs(m, is_animimated) )
    except Exception:
        pass

    if file_info_dict["ext"].lower() in ["gltf", "glb"] and not is_animimated:
        # Make a dump of the current mesh objects and analyze those
        # print("HERE 5")

        mesh_dump = m.dump()
        for (index, obj) in enumerate(mesh_dump):
            try:
                mesh_data_dict.update( { "mesh object "+str(index) : get_mesh_obj_attrs(obj, is_animimated) } )
            except Exception:
                continue



    return mesh_data_dict


if __name__ == "__main__":
	main()
