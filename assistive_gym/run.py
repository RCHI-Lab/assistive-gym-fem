import gym, argparse
import numpy as np
import time
import os
from moviepy.editor import ImageSequenceClip
import cv2
from assistive_gym.envs.panda_cloth_env import ClothObjectPandaEnv
import os.path as osp
import h5py

def save_numpy_as_gif(array, filename, fps=20, scale=1.0):
    # ensure that the file has the .gif extension
    fname, _ = os.path.splitext(filename)
    filename = fname + '.gif'

    # copy into the color dimension if the images are black and white
    if array.ndim == 3:
        array = array[..., np.newaxis] * np.ones(3)

    # make the moviepy clip
    clip = ImageSequenceClip(list(array), fps=fps).resize(scale)
    clip.write_gif(filename, fps=fps)
    return clip

def store_data_by_name(data_names, data, path):
    hf = h5py.File(path, 'w')
    for i in range(len(data_names)):
        hf.create_dataset(data_names[i], data=data[i])
    hf.close()

def load_data_by_name(data_names, path):
    hf = h5py.File(path, 'r')
    data = {}
    for i in range(len(data_names)):
        d = np.array(hf.get(data_names[i]))
        data[data_names[i]] = d
    hf.close()

    return data

def run(args):
    if not osp.exists(args.data_save_path):
        os.makedir(args.data_save_path, exists_ok=True)

    env = ClothObjectPandaEnv(render=args.render)

    rgb_arrays = []
    if args.render:
        env.render(width=720, height=720)
        env.setup_camera(camera_eye=[-1, 1, 1.5], camera_target=[-0.1, 0, 0.2])
        
    observation = env.reset(
        spring_elastic_stiffness=args.spring_elastic_stiffness,
        spring_damping_stiffness=args.spring_damping_stiffness,
        spring_bending_stiffness=args.spring_bending_stiffness,
        urdf_file_path=args.urdf_file_path,
        obj_visual_file_path=args.obj_visual_file_path,
        obj_collision_file_path=args.obj_collision_file_path,
        obj_scale=args.obj_scale,
        urdf_scale=args.urdf_scale,
        cloth_obj_file_path=args.cloth_obj_file_path,
    )
    
    save_data_names = ['cloth_vertices', 'first_torque_force', 'second_torque_force', 
        'first_eef_pos', 'first_eef_orient', 'second_eef_pos', 'second_eef_orient']

    t = time.time()
    for t_idx in range(120):
        if t_idx < 40:
            action = np.zeros_like(env.action_space.sample())
        if t_idx >= 40 and t_idx <= 20 + 40:
            # 7 action dim per robot
            # For each robot, first 3 is delta position, second 4 is delat orientation.
            # this stage is pulling the cloht outwards to stretch it
            action = np.array([0.2, 0, 0, 0, 0, 0, 0, -0.2, 0, 0, 0, 0, 0, 0])
        else:
            # this stage is pulling the cloth downwards towards the object
            action = np.array([0, 0, -0.2, 0, 0, 0, 0, 0, 0, -0.2, 0, 0, 0, 0])
            
        observation, _, _, _ = env.step(action)
        save_name = "data_{:06}".format(t_idx)
        store_data_by_name(save_data_names, observation, osp.join(args.data_save_path, save_name))
        
        if args.render:
            rgb, depth = env.get_camera_image_depth(shadow=True)
            rgb = rgb.astype(np.uint8)
            rgb_arrays.append(rgb)
        zfar = 1000.
        znear = 0.01
        depth = (zfar + znear - (2. * depth - 1.) * (zfar - znear))
        depth = (2. * znear * zfar) / depth
        # print('Runtime: %.2f s, FPS: %.2f' % (time.time() - t, t_idx / (time.time() - t)))
        # cv2.imshow("rgb", rgb)
        # cv2.waitKey()

    if args.render:
        save_numpy_as_gif(np.asarray(rgb_arrays), './tmp-3.gif')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--render', type=int, default=0, help="If True, will open a gui for rendering and dump gifs.")
    parser.add_argument('--data_save_path', type=str, default='./data/store', help="path to store the data.")
    
    parser.add_argument('--spring_elastic_stiffness', type=float, default=40, help="""
        cloth spring elastic stiffness parameter. Seems to explode over the value of 60. 
        Smaller values seem to be more elastic cloth.
        """)
    parser.add_argument('--spring_damping_stiffness', type=float, default=0.1, help="cloth spring elastic stiffness parameter. Haven't tuned much to see its effect.")
    parser.add_argument('--spring_bending_stiffness', type=float, default=0, help="cloth spring elastic stiffness parameter. Haven't tuned much to see its effect.")
    parser.add_argument('--urdf_file_path', type=str, default="dinnerware/sphere.urdf", help="path to a urdf file that represent the object the cloth is pulling downwards to. NOTE: the actual file path is assistive_gym/envs/assets/dinnerware/sphere.urdf")
    parser.add_argument('--obj_visual_file_path', type=str, default=None, help="Alternatively, you can provide a .obj file that describes the object. E.g., dinnerware/plastic_coffee_cup.obj. NOTE: the actual file path is assistive_gym/envs/assets/dinnerware/plastic_coffee_cup.obj")
    parser.add_argument('--obj_collision_file_path', type=str, default=None, help="For .obj file description of the object, need to provide both a visual file and a collision file. E.g., dinnerware/plastic_coffee_cup_vhacd.obj. NOTE: the actual file path is assistive_gym/envs/assets/dinnerware/plastic_coffee_cup.obj")
    parser.add_argument('--obj_scale', type=list, default=[0.2, 0.2, 0.2], help="the scaling of the .obj file along 3 axis")
    parser.add_argument('--urdf_scale', type=float, default=2, help="the scaling of the .urdf file")
    parser.add_argument('--cloth_obj_file_path', type=str, default='clothing/bl_cloth_25_cuts.obj', help="path to a .obj file that describes the cloth mesh.")

    args = parser.parse_args()

    run(args)
