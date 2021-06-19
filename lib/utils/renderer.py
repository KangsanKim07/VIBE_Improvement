# -*- coding: utf-8 -*-

# Max-Planck-Gesellschaft zur Förderung der Wissenschaften e.V. (MPG) is
# holder of all proprietary rights on this computer program.
# You can only use this computer program if you have closed
# a license agreement with MPG or you get the right to use the computer
# program from someone who is authorized to grant you that right.
# Any use of the computer program without a valid license is prohibited and
# liable to prosecution.
#
# Copyright©2019 Max-Planck-Gesellschaft zur Förderung
# der Wissenschaften e.V. (MPG). acting on behalf of its Max Planck Institute
# for Intelligent Systems. All rights reserved.
#
# Contact: ps-license@tuebingen.mpg.de\
import sys
sys.path.append('/content/drive/MyDrive/VIBE_DEMO/lib/utils')
import torch
from model import NPT
import numpy as np
import pymesh
import math
import trimesh
import pyrender
import numpy as np
from pyrender.constants import RenderFlags
from lib.models.smpl import get_smpl_faces

net_G=NPT()
net_G.cuda()
net_G.load_state_dict(torch.load('original_169.model'))


class WeakPerspectiveCamera(pyrender.Camera):
    def __init__(self,
                 scale,
                 translation,
                 znear=pyrender.camera.DEFAULT_Z_NEAR,
                 zfar=None,
                 name=None):
        super(WeakPerspectiveCamera, self).__init__(
            znear=znear,
            zfar=zfar,
            name=name,
        )
        self.scale = scale
        self.translation = translation

    def get_projection_matrix(self, width=None, height=None):
        P = np.eye(4)
        P[0, 0] = self.scale[0]
        P[1, 1] = self.scale[1]
        P[0, 3] = self.translation[0] * self.scale[0]
        P[1, 3] = -self.translation[1] * self.scale[1]
        P[2, 2] = -1
        return P


class Renderer:
    def __init__(self, resolution=(224,224), orig_img=False, wireframe=False):
        self.resolution = resolution

        self.faces = get_smpl_faces()
        self.orig_img = orig_img
        self.wireframe = wireframe
        self.renderer = pyrender.OffscreenRenderer(
            viewport_width=self.resolution[0],
            viewport_height=self.resolution[1],
            point_size=1.0
        )

        # set the scene
        self.scene = pyrender.Scene(bg_color=[0.0, 0.0, 0.0, 0.0], ambient_light=(0.3, 0.3, 0.3))

        light = pyrender.PointLight(color=[1.0, 1.0, 1.0], intensity=1)

        light_pose = np.eye(4)
        light_pose[:3, 3] = [0, -1, 1]
        self.scene.add(light, pose=light_pose)

        light_pose[:3, 3] = [0, 1, 1]
        self.scene.add(light, pose=light_pose)

        light_pose[:3, 3] = [1, 1, 2]
        self.scene.add(light, pose=light_pose)

    def render(self, img, verts, cam, angle=None, axis=None, mesh_filename=None, color=[1.0, 1.0, 0.9]):
        random_sample = np.random.choice(6890,size=6890,replace=False)
        random_sample2 = np.random.choice(6890,size=6890,replace=False)
        def face_reverse(faces):
          identity_faces=faces
          face_dict={}
          for i in range(len(random_sample)):
              face_dict[random_sample[i]]=i
          new_f=[]
          for i in range(len(identity_faces)):
              new_f.append([face_dict[identity_faces[i][0]],face_dict[identity_faces[i][1]],face_dict[identity_faces[i][2]]])
          new_face=np.array(new_f)
          return new_face

        mesh = trimesh.Trimesh(vertices=verts, faces=self.faces, process=False)

        Rx = trimesh.transformations.rotation_matrix(math.radians(180), [1, 0, 0])
        mesh.apply_transform(Rx)

        if mesh_filename is not None:
            mesh.export(mesh_filename)

        if angle and axis:
            R = trimesh.transformations.rotation_matrix(math.radians(angle), axis)
            mesh.apply_transform(R)

        sx, sy, tx, ty = cam

        camera = WeakPerspectiveCamera(
            scale=[sx, sy],
            translation=[tx, ty],
            zfar=1000.
        )

        material = pyrender.MetallicRoughnessMaterial(
            metallicFactor=0.0,
            alphaMode='OPAQUE',
            baseColorFactor=(color[0], color[1], color[2], 1.0)
        )

        # id_mesh=pymesh.load_mesh('./demo_data/18_0.obj')
        # pose_mesh=pymesh.form_mesh(mesh.vertices, mesh.faces)

        # with torch.no_grad():
        #     id_mesh_points=id_mesh.vertices[random_sample]
        #     id_mesh_points=id_mesh_points - (id_mesh.bbox[0] + id_mesh.bbox[1]) / 2
        #     id_mesh_points = torch.from_numpy(id_mesh_points.astype(np.float32)).cuda()

        #     pose_mesh_points=pose_mesh.vertices#[random_sample2]
        #     pose_mesh_points=pose_mesh_points-(pose_mesh.bbox[0] + pose_mesh.bbox[1]) / 2
        #     pose_mesh_points = torch.from_numpy(pose_mesh_points.astype(np.float32)).cuda()


        #     pointsReconstructed = net_G(pose_mesh_points.transpose(0,1).unsqueeze(0),id_mesh_points.transpose(0,1).unsqueeze(0))  # forward pass

        # new_face=face_reverse(id_mesh.faces)

        # tmesh = trimesh.Trimesh(pointsReconstructed.cpu().numpy().squeeze(), faces=new_face, process=False)

        mesh =  pyrender.Mesh.from_trimesh(mesh)

        mesh_node = self.scene.add(mesh, 'mesh')

        camera_pose = np.eye(4)
        cam_node = self.scene.add(camera, pose=camera_pose)

        if self.wireframe:
            render_flags = RenderFlags.RGBA | RenderFlags.ALL_WIREFRAME
        else:
            render_flags = RenderFlags.RGBA

        rgb, _ = self.renderer.render(self.scene, flags=render_flags)
        valid_mask = (rgb[:, :, -1] > 0)[:, :, np.newaxis]
        output_img = rgb[:, :, :-1] * valid_mask + (1 - valid_mask) * img
        image = output_img.astype(np.uint8)

        self.scene.remove_node(mesh_node)
        self.scene.remove_node(cam_node)

        return image