# carla-image-gen
Basic starter code for generating images from Carla with different camera configurations (e.g., monocular, stereo and multi-view stereo.)

# Dependencies
The scripts work on Windows 10. The following dependencies are needed:

- [Carla Simulator](https://carla.readthedocs.io/en/latest/build_windows/)
- [NumPy](https://numpy.org/install/)
- glob
- os
- sys

# File System Organization
The script uses relative directories to find the Carla egg file. Construct your filesystem as seen below or update the path to the Carla egg file on your system.

```
cd {your Carla path}\PythonAPI\examples\
mkdir research && cd research
```

# Usage
The scripts rely on parameters outlined in ```param.py``` to generate the images. Below is an outline of the params dictionary that needs to be updated and parameter descriptions. Note: The preset configurations (mono_forward, mono_downward, stereo, mvs) and default settings are based on the Tesla Model 3 vehicle in Carla. If you change the vehicle model (vehicle_name), other parameters will need to be adjusted. 

```
params = {'carala_egg_path': ,
          'vehicle_name': ,
          'local_dir': ,
          'ground_truth_filename': ,
          'fps': ,
          'save_images': ,
          'maps': ,
          'start_poses': ,
          'num_cams': ,
          'cam_names': ,
          'cam_rotations': ,
          'cam_translations': ,
          'cam_config': }

```

| Parameter      | Parameter Type  | Data Type | Description                                            | Default                                | Options |
|:--------------:|:---------------:|:---------:|:------------------------------------------------------:|:--------------------------------------:|:-------:|
| carla_egg_path | File Management | string    | Path to Carla egg file (adjusted for script directory) | '../../carla/dist/carla-*%d.%d-%s.egg' | Any local path to the ../carla/dist/ directory |
| vehicle_name | File Management | string | Name of Carla vehicle model | 'model3' | [Vehicle Model List](vehicle_models.txt) |
| local_dir | File Management | string | Local directory to save data | 'Data/' | Any desired path for the generated data |
| ground_truth_filename | File Management | string | Root name of the ground truth data | 'gt' | Any desired name for the ground truth data |
| fps | Simulation | double,float,int | Desired frames per second | 10 | Any fps sustainable by your hardware |
| save_images | Simulation | bool | Flag to save your data or not | True | True, False |
| maps | Simulation | list | List of maps to load for your experiment | 'Town01' | 'Town01','Town02','Town03','Town04','Town04','Town05','Town06','Town07', ... |
| start_poses | Simulation | carla.Transform(carla.Location) | Spawn location of the ego vehicle | Random (From possible spawn points on the map) | Any feasible spawn point from the chosen map. See [world.get_map().get_spawn_points()](https://carla.readthedocs.io/en/latest/python_api/#carla.Map.get_waypoint) |
| num_cams | Sensors | int | Number of cameras to spawn | 1 | Number of cameras limited by computer hardware |
| cam_names | Sensors | list | List of names for each camera | 'cam' | Any interpretable string by your filesystem and python |
| cam_rotations | Sensors | 2D list | List of camera rotations | [[0,0,0]] | Any angle in degrees |
| cam_translations | Sensors | 2D list | List of camera positions relative to the vehicle [[x,y,z],...] | [[4,0,1.4]] | Any desired camera position relative to the vehicle |
| cam_config | Sensors | string | Preset configuration for the ego vehicle's camera system | 'mono_forward' | 'mono_forward','mono_downward','stereo','mvs' |

# References
- https://carla.org/

# Future Work
Currently towns are limited to one map at a time. The code needs to be updated to pause data collection and reload another map. Also, the first several samples tend to have incorrect camera positions relative to the vehicle (potential GPU throttling.) A 'warmup' period might be necessary to limit this problem. Other sensor modalities can be added to this code in a similar manner to the camera actors.
