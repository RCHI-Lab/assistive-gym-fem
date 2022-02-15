
# Panda Grasping Cloth based on Assistive Gym 
## Install
We encourage installing the repo with a conda environment.
```bash
conda create -n assistive-gym python=3.6
git clone -b yufei_branch https://github.com/RCHI-Lab/assistive-gym-fem.git
cd assistive-gym
conda activate assistive-gym
pip install -e .
```

## Collect data
To run the two panda gripper pure stretching outwards, run
```bash
python panda_cloth/run_context.py --urdf_file_path None
``` 
To run the two panda gripper stretching and then pulling downwards, run
 ```bash
python panda_cloth/run_task.py 
``` 
Please refer to `panda_cloth/run_context.py` and ``panda_cloth/run_task.py`` for the available arguments for changing the cloth parameteres and loading different objects.

The main file that implements the simulation environment is `assistive_gym/envs/panda_cloth_env.py`.
Please refer to the comments in that file to see how the simulation environment is built.

Data will be automatically stored as a trajectory of h5py file when running `panda_cloth/run_context.py` or `panda_cloth/run_task.py`. The stored location is determined by the argument `data_save_path`.

`panda_cloth/plot.py` can be used to visualize the collected cloth vertex trajectory and force-torque readings. 