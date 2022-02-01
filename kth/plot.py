import h5py
from matplotlib import pyplot as plt
import numpy as np
import os
import os.path as osp

def load_data_by_name(data_names, path):
    hf = h5py.File(path, 'r')
    data = {}
    for i in range(len(data_names)):
        d = np.array(hf.get(data_names[i]))
        data[data_names[i]] = d
    hf.close()

    return data

data_path = 'data/store'
all_data_files = os.listdir(data_path)
all_data_files = sorted(all_data_files)
load_names = ['cloth_vertices', 'first_torque_force', 'second_torque_force']

cloth_vertex_0_pos = []
first_force_x = []
second_torque_y = []
for d in all_data_files:
    data = load_data_by_name(load_names, osp.join(data_path, d))
    cloth_vertex_0_pos.append(data['cloth_vertices'][0])
    first_force_x.append(data['first_torque_force'][0])
    second_torque_y.append(data['second_torque_force'][-2])

fig = plt.figure(figsize=(10, 3))
cloth_ax = fig.add_subplot(1, 3, 1, projection='3d')
first_force_ax = fig.add_subplot(1, 3, 2)
second_torque_ax = fig.add_subplot(1, 3, 3)

cloth_vertex_0_pos = np.asarray(cloth_vertex_0_pos)
cloth_ax.scatter(cloth_vertex_0_pos[:, 0], cloth_vertex_0_pos[:, 1], cloth_vertex_0_pos[:, 2])
cloth_ax.set_title("trajectory of the first vertex of cloth")
cloth_ax.set_xlabel("X")
cloth_ax.set_ylabel("Y")
cloth_ax.set_zlabel("Z")

first_force_ax.plot(range(len(first_force_x)), first_force_x)
first_force_ax.set_title("first robot's force along x axis")

second_torque_ax.plot(range(len(second_torque_y)), second_torque_y)
second_torque_ax.set_title("second robot's torque along y axis")

plt.tight_layout()
plt.show()