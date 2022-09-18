'''

Carla Image Data Generation

Author: Danny Walton
Creation Date: Wednesday, ‎May ‎12, ‎2021
Last Updated: Saturday, September 18th, 2022

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

		self.frame = None

		# Start Carla client
		self.client = carla.Client("localhost", 2000)
		self.client.set_timeout(5.0)

		# Get World and Blueprints
		self.world = self.client.get_world()
		self.blueprint_library = self.world.get_blueprint_library()

		# Get Vehicle Blueprint, Start Position, Waypoints, and Spawn Actor
		self.vehicle_bp = np.random.choice(self.blueprint_library.filter(vehicle_name))

		self.start_pose = par.start_poses
		self.waypoint = self.world.get_map().get_waypoint(self.start_pose.location)
		self.vehicle = self.world.spawn_actor(self.vehicle_bp, self.start_pose)
		self.vehicle.set_simulate_physics(False)
		self.actors.append(self.vehicle)

		# Setting Up Cameras
		self.camera_bp = self.blueprint_library.find('sensor.camera.rgb')

		# Add Cameras
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

	def _save_images(self, folders, gts):
		
		i = 0
		while True:
			self._update_world()

			for m in range(par.num_cams):
				# Upward Camera
				image = self.frames.get(True,1.0)
				image[0].save_to_disk("{0:s}{1:s}".format(folders[m],str(i)))

				#Camera trajectory
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

			print("Image(s) {0:d} saved.".format(i))
			i = i + 1

	def _get_velocity(self):

		velocity = self.vehicle.get_velocity()
		vel = np.array([velocity.x, velocity.y, velocity.z]).reshape((1,3))
		vel = np.array2string(vel, separator = ',')
		# Write to csv file
		file_ = open(par.local_dir+'velocity.csv','a')
		vel = vel.replace("[","")
		vel = vel.replace("]","")
		file_.write(vel)
		file_.write('\n')
		file_.close()


if __name__ == "__main__":
    
    myEnv = VehicleEnv()

    for town in par.maps:
	    folders = []
	    gts = []
	    for i in range(par.num_cams):
	    	folders.append(par.local_dir + town + '/' + par.cam_names[i] + '/')
	    	gts.append(par.local_dir + town + '/' + par.ground_truth_filename + '_' + str(i) + '.csv')

	    if par.save_images == True:
	    	myEnv._save_images(folders,gts)
    

