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


print("last modified: %s" % time.ctime(os.path.getmtime(file)))
print("created: %s" % time.ctime(os.path.getctime(file)))

(mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(file)
print("last modified: %s" % time.ctime(mtime))

file_stat_dict = {
    "mode" : mode,
    "ino" : ino,
    "dev" : dev,
    "nlink" : nlink,
    "uid" : uid,
    "gid" : gid,
    "size" : size,  # in bytes
    "atime" : time.ctime(atime),
    "mtime" : time.ctime(mtime),
    "ctime" : time.ctime(ctime),    # The “ctime” as reported by the operating system. On some systems (like Unix) is the time of the last metadata change, and, on others (like Windows), is the creation time (see platform documentation for details).
    }

file_ext = filename.split('.')[-1] # use this to "assume" filetype (since other general libraries for determing filetype tend to think that 3d files are just text files...)

os.stat_result(st_mode=33204, st_ino=5522179, st_dev=64513, st_nlink=1, st_uid=1000, st_gid=1000, st_size=28869, st_atime=1570141042, st_mtime=1562097398, st_ctime=1570141042)

print(["%s" % time.ctime(i) for i in (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime)])
# ['Thu Jan  1 03:13:24 1970', 'Thu Mar  5 15:56:19 1970', 'Thu Jan  1 11:55:13 1970', 'Wed Dec 31 18:00:01 1969', 'Wed Dec 31 18:16:40 1969', 'Wed Dec 31 18:16:40 1969', 'Thu Jan  1 02:01:09 1970', 'Thu Oct  3 17:17:22 2019', 'Tue Jul  2 14:56:38 2019', 'Thu Oct  3 17:17:22 2019']


def get_3d_model_file_metadata(model_file):
    """
    Function to extract the general file metadata from a model file (e.g., size, date modified, etc.).

    :param model_file: Path and filename of the model file (e.g., an OBJ or GLB file) from which
                       to extract metadata.

    :return file_md_dict: Dictionary of file metadata for the given media file; otherwise, return None.
    """

    try:
        m = mi.parse(media_file)

        md_dict = {}

        for (index, track) in enumerate(m.tracks):
            d = track.to_data()
            md_dict.update( { index : d } )

        return md_dict

    except:
        return None


def get_3d_model_gltf_metadata(gltf_file):
    """

    :param gltf_file: Path and filename of a 3D model in GLTF from which to extract metadata.

    :return gltf_data_dict: Dictionary of GLTF metadata parameters and their values
                            for the given file, if existent. Otherwise, returns None.
    """


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


def get_3d_model_mesh_metadata(mesh_file):

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

        ### All attributes of dir(mesh):
        apply_obb                   invert
        apply_scale                 is_convex
        apply_transform             is_empty
        apply_translation           is_volume
        area                        is_watertight
        area_faces                  is_winding_consistent
        body_count                  kdtree
        bounding_box                mass
        bounding_box_oriented       mass_properties
        bounding_cylinder           md5
        bounding_primitive          merge_vertices
        bounding_sphere             metadata
        bounds                      moment_inertia
        center_mass                 nearest
        centroid                    outline
        compute_stable_poses        permutate
        contains                    principal_inertia_components
        convert_units               principal_inertia_transform
        convex_decomposition        principal_inertia_vectors
        convex_hull                 process
        copy                        ray
        crc                         referenced_vertices
        density                     register
        difference                  remove_degenerate_faces
        edges                       remove_duplicate_faces
        edges_face                  remove_infinite_values
        edges_sorted                remove_unreferenced_vertices
        edges_sorted_tree           rezero
        edges_sparse                sample
        edges_unique                scale
        edges_unique_inverse        scene
        edges_unique_length         section
        euler_number                section_multiplane
        eval_cached                 show
        export                      slice_plane
        extents                     smoothed
        face_adjacency              split
        face_adjacency_angles       subdivide
        face_adjacency_convex       submesh
        face_adjacency_edges        symmetry
        face_adjacency_edges_tree   symmetry_axis
        face_adjacency_projections  symmetry_section
        face_adjacency_radius       to_dict
        face_adjacency_span         triangles
        face_adjacency_tree         triangles_center
        face_adjacency_unshared     triangles_cross
        face_angles                 triangles_tree
        face_angles_sparse          union
        face_attributes             units
        face_normals                unmerge_vertices
        faces                       update_faces
        faces_sparse                update_vertices
        faces_unique_edges          vertex_adjacency_graph
        facets                      vertex_attributes
        facets_area                 vertex_defects
        facets_boundary             vertex_degree
        facets_normal               vertex_faces
        facets_on_hull              vertex_neighbors
        facets_origin               vertex_normals
        fill_holes                  vertices
        fix_normals                 visual
        identifier                  volume
        identifier_md5              voxelized
        intersection































































        >>>


    """
    return None



with zipfile.ZipFile('test360_orig.zip', 'r') as zip_ref:
    filename_360_video = zip_ref.namelist()[0]
    zip_ref.extract(filename_360_video)
    print(filename_360_video)


# filename_360_video = 'test360_orig.mp4'
exiftool_dir = '/home/piehld/Dropbox/Work/GA_Grainger/IdeaLab/3deposit/services/metadata/Image-ExifTool-11.65'

mediainfo_metadata = get_mediainfo_metadata(filename_360_video)
spherical_metadata = get_360_metadata(filename_360_video, exiftool_dir)

metadata_dict = {}

if mediainfo_metadata is not None:
    metadata_dict.update( mediainfo_metadata )

if spherical_metadata is not None:
    metadata_dict.update( {len(metadata_dict) : spherical_metadata} ) # len(metadata_dict) determines the next key/index to use

metadata_json = json.dumps(metadata_dict)

pprint.pprint(json.loads(metadata_json))
