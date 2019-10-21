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

def main():

    ## Still to do/test
        # Determine if animated or not, then say Yes or No
        # Test different file types and animated models

    ## DONE:
        # Add sub-directory searching (or see if it can already do that, depending on how the files are included in the filename_list;
            # For example, if they're like "./dir1/dir2/filename.txt", then don't need to worry about it I think...)
        # Add counts of vertices and triangles


    # Will this return any subdirectories and their contents, if present? --- YES!
    # If so, will want to iterate over all of them and get the metadata for them -- DONE!
    with zipfile.ZipFile('test_subdir_file_tree.zip', 'r') as zip_ref:
        filename_list = zip_ref.namelist()
        print(filename_list)
        for fn in filename_list:
            zip_ref.extract(fn)

    supported_3d_mesh_types = ['gltf','glb','obj','stl'] # add more

    all_file_metadata = {}

    for fn in filename_list:
        # print(fn)

        # Clear previous properties
        gltf_metadata = None
        mesh_metadata = None
        file_metadata = None

        file_metadata = get_3d_model_file_metadata(fn)

        # May need to do this check for all files in the tree
        if file_metadata["ext"] is not None:
            if file_metadata["ext"].lower() == "gltf" or file_metadata["ext"].lower() == "glb":
                gltf_metadata = get_3d_model_gltf_metadata(fn, file_metadata)

            # Can either check if extension is in supported type list,
            # OR simply TRY for all file to see if it can be loaded
            if file_metadata["ext"] in supported_3d_mesh_types:
                mesh_metadata = get_3d_model_mesh_metadata(fn, file_metadata)

            # if file_metadata["ext"] == "obj":
            #     pass

            # gltf_metadata = get_3d_model_gltf_metadata(fn)
            # mesh_metadata = get_3d_model_mesh_metadata(fn)

        metadata_dict = {}

        if file_metadata is not None:
            metadata_dict.update( {"General properties" : file_metadata} )

        if gltf_metadata is not None:
            metadata_dict.update( {"GLTF metadata" : gltf_metadata} )

        if mesh_metadata is not None:
            metadata_dict.update( {"Mesh metadata" : mesh_metadata} )

        all_file_metadata.update( {fn : metadata_dict} )

    metadata_json = json.dumps(all_file_metadata)

    pprint.pprint(json.loads(metadata_json))




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

        except:
            print("Problem getting file path, name, and extension.")
            file_info_dict.update({"file_tree_path":None})
            file_info_dict.update({"filename":None})
            file_info_dict.update({"ext":None})

        # for k,v in file_info_dict.items():
        #     print(k,v)

        return file_info_dict

    except:
        return None



def get_3d_model_gltf_metadata(gltf_file, file_info_dict):
    """

    :param gltf_file: Path and filename of a 3D model in GLTF from which to extract metadata.

    :return gltf_data_dict: Dictionary of GLTF metadata parameters and their values
                            for the given file, if existent. Otherwise, returns None.
    """

    if file_info_dict["ext"].lower() == "gltf": # Get entire file info

        try:
            with open(gltf_file, 'rb') as gltf:
                gltf_data_dict = json.load(gltf)

            return gltf_data_dict

        except:
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

        except:
            return None


def get_3d_model_mesh_metadata(mesh_file, file_info_dict):

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

    def get_mesh_obj_attrs(mesh):
        attr_dict = {}
        for a in dir(mesh):
            if not a.startswith('_'):  # and a in mesh_attr_list:
                try:
                    if not callable(getattr(mesh, a)):
                        json.dumps( {a : getattr(mesh, a)} )   # Check to see if it can be serialized (e.g., not a numpy array or unfamiliar object)
                        attr_dict.update( {a : getattr(mesh, a)} )
                except:
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
                    except:
                        continue

        return attr_dict

    # if file_info_dict["ext"].lower() in ["obj", "stl"]:
    try:
        mesh_data_dict.update( get_mesh_obj_attrs(m) )
    except:
        pass

    if file_info_dict["ext"].lower() in ["gltf", "glb"]:
        # Make a dump of the current mesh objects and analyze those
        mesh_dump = m.dump()
        for (index, obj) in enumerate(mesh_dump):
            try:
                mesh_data_dict.update( { "mesh object "+str(index) : get_mesh_obj_attrs(obj) } )
            except:
                continue


    return mesh_data_dict


if __name__ == "__main__":
	main()
