import glob
import sys
import os

try:
    sys.path.append(glob.glob('../../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

'''
		Parameter List:

		File Management ----------------------------------------------------------------------------------------------------------------------------------

		carla_egg_path: 		(string) Path to Carla egg file (adjusted for script directory). 
								Default: '../../carla/dist/carla-*%d.%d-%s.egg'
								Options: (Any local path to the ../carla/dist/ directory.)

		vehicle_name:   		(string) Name of Carla vehicle model.
					    		Default: 'model3'
					    		Options: 'model3','mustang','mkz2017','etron','t2','cybertruck',
					    		 		 'century','omafiets','crossbike','ninja','yzf','prius',
					    		 		 'patrol','cooperst','coupe','wrangler_rubicon','police',
					    		      	 'c3','impala','carlacola','isetta','grandtourer','low_rider',
					    		 		 'tt','a2','micra'

		local_dir:				(string) Local directory to save data.
								Default: 'Current_Data/'
								Options: (Any desired local path for the generated data.)

		ground_truth_filename:	(string) Root name of the ground truth data
								Default: 'gt'
								Options: (Any desired name for the ground truth data.)
		
		Simulation ----------------------------------------------------------------------------------------------------------------------------------

		fps:					(double,float,int) Desired frames per second. (Limited by hardware.)
								Default: 30
								Options: (Any fps sustainable by your hardware.)

		save_images:			(bool) Flag to save your data or not.
								Default: True
								Options: True, False

		maps:					(list) List of maps to load for your experiment.
								Default: 'Town01'
								Options: 'Town01','Town02','Town03','Town04','Town04','Town05','Town06','Town07', ...

		start_poses:			(carla.Transform(Location())) carla.Transform of the initial vehicle pose
								Default: Random (From possible spawn points on the map.)
								Options: (Any feasible spawn point from the map. See world.get_map().get_spawn_points())
		
		Sensors ----------------------------------------------------------------------------------------------------------------------------------

		num_cams:				(int) Number of cameras to spawn.
								Default: 1
								Options: (Number of cameras limited by hardware.)

		cam_names:				(list) List of names for each camera. (num_cams must = len(cam_names))
								Default: 'cam'
								Options: (Any readable string that's interpretable by your filesystem and python.)

		cam_rotations:			(list) List of camera orientations. (pitch,yaw,roll) ((len(cam_poses) == len(num_cams))
								Default: (0,0,0)
								Options: (Any angle in degrees.)
		
		cam_translations:		(list) List of camera positions relative to the vehicle. (x,y,z)
								Default: (4,0,1.4) (For model3)
								Options: (Any desired camera pose relative to the vehicle.)

		cam_config: 			(string) Preset configurations for the vehicle camera system. (Create dictionaries with Class parameters)
								Default: 'mono_forward'
								Options: 'mono_forward','mono_downward','stereo','mvs'

		----------------------------------------------------------------------------------------------------------------------------------
'''

params = {'carala_egg_path': '../../carla/dist/carla-*%d.%d-%s.egg',
		  'vehicle_name': 'model3',
		  'local_dir': 'Data/',
		  'ground_truth_filename': 'gt',
		  'fps': 1,
		  'save_images': True,
		  'maps': ['Town01'],
		  'start_poses': carla.Transform(carla.Location(x=229.973785, y=67.599396, z=0.450000), 
		  						   		 carla.Rotation(pitch=0.167927, yaw=91.393204, roll=0.000000)),
		  'num_cams': 0,
		  'cam_names': [],
		  'cam_rotations': [],
		  'cam_translations': [],
		  'cam_config': 'mono_forward'}

class Params():
	def __init__(self, parameters=params):
		# parameters: dictionary of parameters

		'''
		Format:
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
							   'cam_config': 'mono_forward'}
		'''

		# 		  (don't need 'num_cams' through 'cam_translations' if using a preset, set them to default values)

		self.params = params
		self.mode = self.params['cam_config']

		# Filesystem
		self.carla_egg_path = self.params['carala_egg_path']
		self.vehicle_name = self.params['vehicle_name']
		self.local_dir = self.params['local_dir']
		self.ground_truth_filename = self.params['ground_truth_filename']

		# Simulation
		self.fps = self.params['fps']
		self.save_images = self.params['save_images']
		self.maps = self.params['maps']
		self.start_poses = self.params['start_poses']

		if self.mode == 'custom':	

			# Sensors
			self.num_cams = self.params['num_cams']
			self.cam_names = self.params['cam_names']
			self.cam_rotations = self.params['cam_rotations']
			self.cam_translations = self.params['cam_translations']
			self.cam_config = self.params['cam_config']

		else:

			if self.mode == 'mono_forward':

				# Sensors
				self.num_cams = 1
				self.cam_names = ['camera_up']
				self.cam_rotations = [[0,0,0]]
				self.cam_translations = [[4,0,1.4]]
				self.cam_config = 'mono_forward'

			elif self.mode == 'mono_downward':

				# Sensors
				self.num_cams = 1
				self.cam_names = ['camera_down']
				self.cam_rotations = [[-90,0,0]]
				self.cam_translations = [[4,0,1.4]]
				self.cam_config = 'mono_downward'

			elif self.mode == 'stereo':

				# Sensors
				self.num_cams = 2
				self.cam_names = ['cam1','cam2']
				self.cam_rotations = [[0,0,0],[0,0,0]]
				self.cam_translations = [[4,-0.2,1.4],[4,0.2,1.4]]
				self.cam_config = 'stereo'
				
			elif self.mode == 'mvs':

				# Sensors
				self.num_cams = 5
				self.cam_names = ['cam1','cam2','cam3','cam4','cam5']
				self.cam_rotations = [[0,0,0],[0,0,0],[0,-90,0],[0,90,0],[0,180,0]]
				self.cam_translations = [[4,-0.2,1.4],[4,0.2,1.4],[0,-1,1.4],[0,1,1.4],[-2,0,1.4]]
				self.cam_config = 'mvs'
				
			else:

				print("Please use: ")
				print("'mono_forward' for a monocular, forward facing camera.")
				print("'mono_downward' for a monocular, downward facing camera.")
				print("'stereo' for forward facing, stereo cameras.")
				print("'mvs' for multi-view stereo.")
				print("'custom' for a custom camera configuration.")


par=Params(params)