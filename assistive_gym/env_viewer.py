import gym, sys, argparse
import numpy as np
from .learn import make_env
# import assistive_gym
import time
import cv2

if sys.version_info < (3, 0):
    print('Please use Python 3')
    exit()

def sample_action(env, coop):
    if coop:
        return {'robot': env.action_space_robot.sample(), 'human': env.action_space_human.sample()}
    return env.action_space.sample()

def get_action(t):
    if t < 100:
        action = np.array([-1, 0, 0, 0, 0, 0, 0])
    else:
        action = np.array([0, 1, 0, 0, 0, 0, 0])
    # action = np.array([0, 0, 0, 0, 0, 0, 0])
    return action


def viewer(env_name):
    coop = 'Human' in env_name
    env = make_env(env_name, coop=True) if coop else gym.make(env_name)

    while True:
        done = False
        env.render(width=720, height=720)
        env.setup_camera(camera_eye=[-0.3, -0.2, 1.2], camera_target=[-0.1, -0.2, 0.6])
        observation = env.reset()
        
        # if coop:
        #     print('Robot observation size:', np.shape(observation['robot']), 'Human observation size:', np.shape(observation['human']), 'Robot action size:', np.shape(action['robot']), 'Human action size:', np.shape(action['human']))
        # elif 'BeddingManipulationSphere-v1' in env_name:
        #     action = np.array([0.3, 0.5, 0, 0])
        # elif 'RemoveContactSphere-v1' in env_name:
        #     action = np.array([0.3, 0.45])
        # else:
        #     print('Observation size:', np.shape(observation), 'Action size:', np.shape(action))

        t = time.time()
        idx = 0
        for idx in range(200):
            # observation, reward, done, info = env.step(sample_action(env, coop))
            if env_name != 'ClothTableObject-v1':
                action = sample_action(env, coop)
            else:
                action = get_action(idx)
            idx += 1
            observation, reward, done, info = env.step(action)
            rgb, depth = env.get_camera_image_depth(shadow=True)
            rgb = rgb.astype(np.uint8)
            zfar = 1000.
            znear = 0.01
            depth = (zfar + znear - (2. * depth - 1.) * (zfar - znear))
            depth = (2. * znear * zfar) / depth
            # depth = far * near / (far - (far - near) * depth)
            # if idx >= 25:
            #     cv2.imshow("rgb", rgb[:, :, :3][:, :, ::-1])
            #     cv2.imshow("depth", depth)
            #     cv2.waitKey()
            print('Runtime: %.2f s, FPS: %.2f' % (time.time() - t, idx / (time.time() - t)))
            if coop:
                done = done['__all__']


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Assistive Gym Environment Viewer')
    parser.add_argument('--env', default='ScratchItchJaco-v1',
                        help='Environment to test (default: ScratchItchJaco-v1)')
    args = parser.parse_args()

    viewer(args.env)
