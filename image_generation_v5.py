'''

Carla Image Data Generation

Author: Danny Walton
Creation Date: Wednesday, ‎May ‎12, ‎2021
Last Updated: Saturday, September 17th, 2022

'''
import glob
import os
import sys

from param import par

try:
    sys.path.append(glob.glob(par.carla_egg_path % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
import numpy as np
import cv2
import time
from queue import Queue
from queue import Empty

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

'''
		Generates Carla Image Data for (Offline) Algorithm Development
'''

class VehicleEnv():
	def __init__(self, vehicle_name=par.vehicle_name, fps=par.fps):
		# fps constrained by hardware

		# Initializations
		self.actors = []
		self.delta_seconds = 1/fps
		self.sensor_queue = Queue()

		#self.frame = None
		#self.frame_down = None
		self.frame = None

		# Start Carla client
		self.client = carla.Client("localhost", 2000)
		self.client.set_timeout(5.0)

		# Get World and Blueprints
		self.world = self.client.get_world()
		self.blueprint_library = self.world.get_blueprint_library()

		# List of Vehicle Blueprints
		'''blueprints = [bp for bp in self.blueprint_library.filter('*')]
								for blueprint in blueprints:
									print(blueprint.id)
									for attr in blueprint:
										print('  - {}'.format(attr))'''

		# Get Vehicle Blueprint, Start Position, Waypoints, and Spawn Actor
		self.vehicle_bp = np.random.choice(self.blueprint_library.filter(vehicle_name))
		#self.start_pose = np.random.choice(self.world.get_map().get_spawn_points())
		#print(self.start_pose)
		#print("Type: " + str(type(self.start_pose)))
		self.start_pose = par.start_poses
		self.waypoint = self.world.get_map().get_waypoint(self.start_pose.location)
		self.vehicle = self.world.spawn_actor(self.vehicle_bp, self.start_pose)
		self.vehicle.set_simulate_physics(False)
		self.actors.append(self.vehicle)

		# Setting Up Cameras
		self.camera_bp = self.blueprint_library.find('sensor.camera.rgb')

		# Add Cameras
		#self.camera_t_down = carla.Transform(carla.Location(x=4, y=-0.2, z=1.4),carla.Rotation(pitch=-90,yaw=0,roll=0))
		self.cam_actors = []
		for j in range(par.num_cams):
			self.camera = carla.Transform(carla.Location(x=par.cam_translations[j][0], 
														 y=par.cam_translations[j][1], 
														 z=par.cam_translations[j][2]),
										  carla.Rotation(pitch=par.cam_rotations[j][0],
										  				 yaw=par.cam_rotations[j][1],
										  				 roll=par.cam_rotations[j][2]))
			self.mono_camera = self.world.spawn_actor(self.camera_bp, self.camera, attach_to=self.vehicle)
			self.actors.append(self.mono_camera)
			self.cam_actors.append(self.mono_camera)

		# Add Cameras
		#self.mono_camera_down = self.world.spawn_actor(self.camera_bp, self.camera_t_down, attach_to=self.vehicle)
		#self.actors.append(self.mono_camera_down)

		#self.mono_camera_up = self.world.spawn_actor(self.camera_bp, self.camera_t_up, attach_to=self.vehicle)
		#self.actors.append(self.mono_camera_up)

		'''
		# Get Image Attributes (Image Height, Width, Field of View)
		self.image_w = self.camera_bp.get_attribute("image_size_x").as_int()
		self.image_h = self.camera_bp.get_attribute("image_size_y").as_int()
		self.fov = self.camera_bp.get_attribute("fov").as_float()

		# Calculate focal length
		self.focal = self.image_w / (2.0 * np.tan(self.fov * np.pi / 360.0))

		# Assigning values to calibration matrix, K
		self.K = np.identity(3)
		self.K[0, 0] = self.K[1, 1] = self.focal
		self.K[0, 2] = self.image_w / 2.0
		self.K[1, 2] = self.image_h / 2.0
		'''

		# Camera Callback
		#self.mono_camera.listen(lambda data: self._capture_frame(data, "mono_cam_"))
		#self.mono_camera_down.listen(lambda data: self._capture_frame(data, "mono_cam_down"))
		#self.mono_camera_up.listen(lambda data: self._capture_frame(data, "mono_cam_up"))
		for k in range(par.num_cams):
			self.cam_actors[k].listen(lambda data: self._capture_frame(data, par.cam_names[k]))

		self.original_settings = self.world.get_settings()
		self.world.apply_settings(carla.WorldSettings(no_rendering_mode=False, synchronous_mode=True, fixed_delta_seconds=self.delta_seconds))
		self.world_frame = self.world.get_snapshot().frame

	def _capture_frame(self, sensor_data, sensor_name):
		frame = sensor_data
		self.sensor_queue.put((frame, sensor_name))

	def _update_world(self):
		self.world.tick()
		self.world_frame = self.world.get_snapshot().frame
		print(f'world frame: {self.world_frame}')
		self.waypoint = np.random.choice(self.waypoint.next(1))
		self.vehicle.set_transform(self.waypoint.transform)

		self.frames = Queue()
		for _ in range(par.num_cams):
			s_frame = self.sensor_queue.get(True, 1.0)
			self.frames.put(s_frame)
			'''if s_frame[1] == 'mono_cam_down':
													self.frame_down = s_frame[0]
												elif s_frame[1] == 'mono_cam_up':
													self.frame_up = s_frame[0]'''

	def _save_images(self, folders, gts):
		i = 0
		#up_t = []
		#down_t = []

		while True:
			self._update_world()
			'''
			# Downward Camera
			image_down = self.frame_down
			image_down.save_to_disk("{0:s}{1:s}".format(folder1,str(i)))

			#Camera (Downward) trajectory
			loc_down = self.mono_camera_down.get_location()
			traj_down = np.array([loc_down.x, loc_down.y, loc_down.z]).reshape((1,3))
			traj_down = np.array2string(traj_down, separator =',')
			#Write to .csv file
			file1 = open(csv1,'a')
			#text = file1.read()
			traj_down = traj_down.replace("[","")
			traj_down = traj_down.replace("]","")
			file1.write(traj_down)
			file1.write('\n')
			file1.close()'''

			for m in range(par.num_cams):
				# Upward Camera
				image = self.frames.get(True,1.0)
				image[0].save_to_disk("{0:s}{1:s}".format(folders[m],str(i)))

				#Camera (Upward) trajectory
				#loc = self.mono_camera.get_location()
				loc = self.cam_actors[m].get_location()
				traj = np.array([loc.x, loc.y, loc.z]).reshape((1,3))
				traj = np.array2string(traj, separator = ',')
				#Write to .csv file
				file = open(gts[m],'a')
				traj = traj.replace("[","")
				traj = traj.replace("]","")
				file.write(traj)
				file.write('\n')
				file.close()

			#print("Image {0:d} saved.".format(i))
			print("Image(s) {0:d} saved.".format(i))
			i = i + 1

	def _get_velocity(self):
		# Currently unused/tested. Velocity is likely only meaningful for certain scenarios.
		velocity = self.vehicle.get_velocity()
		#mag_vel = np.sqrt(velocity[0]**2 + velocity[1]**2 + velocity[2]**2)
		#mag_vel = velocity.length() # Carla function
		vel = np.array([velocity.x, velocity.y, velocity.z]).reshape((1,3))
		vel = np.array2string(vel, separator = ',')
		# Write to csv file
		file_ = open(par.local_dir+'velocity.csv','a')
		vel = vel.replace("[","")
		vel = vel.replace("]","")
		file_.write(vel)
		file_.write('\n')
		file_.close()
		#print("Velocity: " + str(velocity))
		#print("Velocity Magnitude: " + str(mag_vel))



if __name__ == "__main__":
    myEnv = VehicleEnv()
    # Old values:
    # folder1: _out_down30_2/
    # csv1: 'trajectory_down_cam30_2.csv'
    # folder2: _out_up30_2/
    # csv2: 'trajectory_up_cam30_2.csv'

    # Made changes so that only the town name needs to be changed to collect data from that town.

    #town = par.maps[0] #'Town05'
    #folder1 = par.local_dir + town + '/Down_' + town + '/'
    #csv1 = par.local_dir + town + '/' + 'trajectory_down_' + town + '.csv'
    #folder2 = par.local_dir + town + '/Up_' + town + '/'
    #csv2 = par.local_dir + town + '/' + 'trajectory_up_' + town + '.csv'

    for town in par.maps:
	    folders = []
	    gts = []
	    for i in range(par.num_cams):
	    	folders.append(par.local_dir + town + '/' + par.cam_names[i] + '/')
	    	gts.append(par.local_dir + town + '/' + par.ground_truth_filename + '_' + str(i) + '.csv')

	    if par.save_images == True:
	    	myEnv._save_images(folders,gts)

'''
TODO:
1. Check all parameters work.
2. Test multiple towns. Can you change town from script?
3. Write Github documentation.
'''
    

