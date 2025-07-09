# Dual UAV Hector Quadrotor + ORB-SLAM3 + COVINS Setup

This guide walks you through the full setup for simulating **two Hector Quadrotor UAVs** in Gazebo, sending them independent motion commands, and running **ORB-SLAM3** with **COVINS** for each agent.

---

## if you running the docker image:
```bash

xhost +local:root

docker run -it \
  --net=host \
  --env="DISPLAY=$DISPLAY" \
  --env="QT_X11_NO_MITSHM=1" \
  --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
  --volume="$(pwd):/app" \
  ros1-gazebo-hector-container-with-template_matching \
  bash


## 1. Launch File to Spawn Two UAVs in Gazebo

File: `gazebo_models_worlds_collection_2_agent.launch`
Location: `~/catkin_ws/src/hector_quadrotor/hector_quadrotor_demo/launch/`

```xml
<?xml version="1.0"?>
<launch>

  <!-- Load Gazebo with custom office world -->
  <include file="$(find gazebo_ros)/launch/empty_world.launch">
    <arg name="world_name" value="$(find gazebo_models_worlds_collection)/worlds/office_cpr.world"/>
    <arg name="use_sim_time" value="true"/>
    <arg name="gui" value="true"/>
    <arg name="paused" value="false"/>
  </include>

  <!-- Spawn first UAV (Agent 0) -->
  <group ns="uav0">
    <param name="tf_prefix" value="uav0_tf"/>
    <include file="$(find hector_quadrotor_gazebo)/launch/spawn_quadrotor.launch">
      <arg name="model" value="$(find hector_quadrotor_description)/urdf/quadrotor_hokuyo_utm30lx.gazebo.xacro"/>
      <arg name="name" value="uav0"/>
      <arg name="x" value="0"/>
      <arg name="y" value="0"/>
      <arg name="z" value="0.3"/>
      <arg name="controllers" value="controller/attitude controller/velocity controller/position"/>
    </include>
  </group>

  <!-- Spawn second UAV (Agent 1) -->
  <group ns="uav1">
    <param name="tf_prefix" value="uav1_tf"/>
    <include file="$(find hector_quadrotor_gazebo)/launch/spawn_quadrotor.launch">
      <arg name="model" value="$(find hector_quadrotor_description)/urdf/quadrotor_hokuyo_utm30lx.gazebo.xacro"/>
      <arg name="name" value="uav1"/>
      <arg name="x" value="1"/>
      <arg name="y" value="1"/>
      <arg name="z" value="0.3"/>
      <arg name="controllers" value="controller/attitude controller/velocity controller/position"/>
    </include>
  </group>

</launch>
```

---

## 2. Motion Command Script for Each Agent

File: `auto_move_agents.py`
Location: `/catkin_ws/src/hector_quadrotor/hector_move/scripts/`

```python
#!/usr/bin/env python

import rospy
import sys
from geometry_msgs.msg import Twist

def move(namespace):
    rospy.init_node('hector_auto_move_' + namespace.replace('/', ''), anonymous=True)
    pub = rospy.Publisher('/{}/cmd_vel'.format(namespace), Twist, queue_size=10)
    rate = rospy.Rate(10)  # 10 Hz

    twist = Twist()
    twist.linear.x = 0.5
    twist.angular.z = 0.15

    rospy.loginfo("[{}] Publishing motion command...".format(namespace))
    while not rospy.is_shutdown():
        pub.publish(twist)
        rate.sleep()

if __name__ == '__main__':
    try:
        if len(sys.argv) < 2:
            print("Usage: rosrun hector_move auto_move_agents.py <namespace>")
        else:
            move(sys.argv[1])
    except rospy.ROSInterruptException:
        pass
```

```
cd ~/catkin_ws
catkin_make
source ~/catkin_ws/devel/setup.bash
```

### Run for both agents:

```bash
rosrun hector_move auto_move_agents.py uav0
rosrun hector_move auto_move_agents.py uav1
```
✅ MONO IMU   -auto_move_agents_walls_mono_imu.py:

 /root/catkin_ws/src/hector_move/scripts/auto_move_agents_walls_mono_imu.py

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
from sensor_msgs.msg import Image, Imu
from geometry_msgs.msg import TwistStamped
from cv_bridge import CvBridge
import numpy as np
import cv2

class MonoCameraAvoidance:
    def __init__(self):
        rospy.init_node("mono_obstacle_avoidance")

        self.bridge = CvBridge()

        # Subscribe to camera and IMU
        self.image_sub = rospy.Subscriber("/uav0/front_cam/camera/image", Image, self.image_callback)
        self.imu_sub = rospy.Subscriber("/uav0/raw_imu", Imu, self.imu_callback)

        # Publish velocity commands
        self.cmd_pub = rospy.Publisher("/uav0/command/twist", TwistStamped, queue_size=1)

        self.forward_accel = 0.0
        self.obstacle_detected = False

    def imu_callback(self, msg):
        # Read forward acceleration (assuming x is forward)
        self.forward_accel = msg.linear_acceleration.x

    def image_callback(self, msg):
        # Convert the image to grayscale (mono)
        gray_img = self.bridge.imgmsg_to_cv2(msg, desired_encoding="mono8")

        # Crop a center region
        h, w = gray_img.shape
        center = gray_img[h//2 - 20:h//2 + 20, w//2 - 20:w//2 + 20]

        # Compute the variance in the center of the image
        variance = np.var(center)

        # Low variance = possibly flat wall surface
        if variance < 50:
            self.obstacle_detected = True
            rospy.loginfo("Low texture detected - possible wall.")
        else:
            self.obstacle_detected = False

        # Build velocity command
        twist_msg = TwistStamped()
        twist_msg.header.stamp = rospy.Time.now()
        twist_msg.header.frame_id = "base_stabilized"


        if self.obstacle_detected or self.forward_accel > 1.5:
            twist_msg.twist.linear.x = 0.05
            twist_msg.twist.angular.z = 0.4  # Rotate in place
            rospy.loginfo("Obstacle detected - turning")
        else:
            twist_msg.twist.linear.x = 0.3
            twist_msg.twist.angular.z = 0.1
            rospy.loginfo("Path is clear - moving forward")

        self.cmd_pub.publish(twist_msg)

if __name__ == '__main__':
    try:
        MonoCameraAvoidance()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
```


✅ RGBD -auto_move_agents_walls.py:
```
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import numpy as np

class UAV0AvoidWalls:
    def __init__(self):
        rospy.init_node("uav0_obstacle_avoidance")  # Initialize the node

        self.bridge = CvBridge()
        self.depth_sub = rospy.Subscriber("/uav0/camera/depth/image_raw", Image, self.depth_callback)
        self.cmd_pub = rospy.Publisher("/uav0/cmd_vel", Twist, queue_size=1)

        self.min_safe_distance = 1.0  # Distance in meters to start avoiding wall

    def depth_callback(self, msg):
        # Convert ROS depth image to NumPy array
        depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
        depth_array = np.array(depth_image, dtype=np.float32)

        # Get the shape of the depth image
        height, width = depth_array.shape

        # Take a small square in the center of the image (looking forward)
        center_region = depth_array[height//2 - 10:height//2 + 10, width//2 - 10:width//2 + 10]

        # Find the minimum (closest) distance in that center region
        min_distance = np.nanmin(center_region)

        # Create a velocity message
        twist = Twist()

        if np.isnan(min_distance):
            # No valid depth data (all values are NaN)
            rospy.logwarn("No valid depth data!")
            twist.linear.x = 0.0  # Stop
        elif min_distance < self.min_safe_distance:
            # Obstacle is too close - rotate to avoid it
            rospy.loginfo("Obstacle ahead at {:.2f} m - turning...".format(min_distance))
            twist.linear.x = 0.0
            twist.angular.z = 0.5  # Rotate in place
        else:
            # No obstacle - move forward
            rospy.loginfo("Clear path ({:.2f} m) - moving forward.".format(min_distance))
            twist.linear.x = 0.3  # Move forward
            twist.angular.z = 0.0

        # Publish the velocity command
        self.cmd_pub.publish(twist)

if __name__ == '__main__':
    try:
        UAV0AvoidWalls()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
```

---

## 3. Takeoff Action for Each UAV

Use the following commands to trigger the takeoff:

```bash
rosrun actionlib axclient.py /uav0/action/takeoff
rosrun actionlib axclient.py /uav1/action/takeoff
```

---

## 4. Command UAVs to Move Upward

Send altitude target (e.g., Z = 2.0 meters):

```bash
rostopic pub /uav0/command/pose geometry_msgs/PoseStamped '
header:
  frame_id: "world"
pose:
  position:
    x: 0.0
    y: 0.0
    z: 2.0
  orientation:
    x: 0.0
    y: 0.0
    z: 0.0
    w: 1.0
'

rostopic pub /uav1/command/pose geometry_msgs/PoseStamped '
header:
  frame_id: "world"
pose:
  position:
    x: 0.0
    y: 0.0
    z: 2.25
  orientation:
    x: 0.0
    y: 0.0
    z: 0.0
    w: 1.0
'
```

---

## 5. ORB-SLAM3 Launch Files per Agent

### Agent 0

```xml
<launch>
  <param name="use_sim_time" value="true"/>

  <arg name="ag_n" default="0" />
  <arg name="voc" default="/root/covins_ws/src/covins/orb_slam3/Vocabulary/ORBvoc.txt" />
  <arg name="cam" default="/root/covins_ws/src/covins/orb_slam3/Examples/real_camera_hector.yaml" />

  <node pkg="ORB_SLAM3" type="Mono_Inertial" name="ORB_SLAM3_monoi$(arg ag_n)" args="$(arg voc) $(arg cam)" output="screen">
    <remap from="/camera/image_raw" to="/uav0/front_cam/camera/image"/>
    <remap from="/imu" to="/uav0/raw_imu"/>
  </node>
</launch>
```

### Agent 1

```xml
<launch>
  <param name="use_sim_time" value="true"/>

  <arg name="ag_n" default="1" />
  <arg name="voc" default="/root/covins_ws/src/covins/orb_slam3/Vocabulary/ORBvoc.txt" />
  <arg name="cam" default="/root/covins_ws/src/covins/orb_slam3/Examples/real_camera_hector.yaml" />

  <node pkg="ORB_SLAM3" type="Mono_Inertial" name="ORB_SLAM3_monoi$(arg ag_n)" args="$(arg voc) $(arg cam)" output="screen">
    <remap from="/camera/image_raw" to="/uav1/front_cam/camera/image"/>
    <remap from="/imu" to="/uav1/raw_imu"/>
  </node>
</launch>
```

### Run both:

```bash
roslaunch ORB_SLAM3 launch_agent0.launch
roslaunch ORB_SLAM3 launch_agent1.launch
```


### real_camera_hector.yaml:
```
nano /root/covins_ws/src/covins/orb_slam3/Examples/real_camera_hector.yaml
```

```
---

%YAML:1.0

#--------------------------------------------------------------------------------------------
# Camera Parameters. Adjust them!
#--------------------------------------------------------------------------------------------
Camera.type: "PinHole"

# Camera calibration and distortion parameters (OpenCV) 
Camera.fx: 159.99941228826285
Camera.fy: 159.99941228826285
Camera.cx: 160.5
Camera.cy: 120.5

Camera.k1: 0.0
Camera.k2: 0.0
Camera.p1: 0.0
Camera.p2: 0.0

# Camera resolution
Camera.width: 320
Camera.height: 240

# Camera frames per second 
Camera.fps: 25.0

# Color order of the images (0: BGR, 1: RGB. It is ignored if images are grayscale)
Camera.RGB: 1

# Transformation from camera to body-frame (imu)
Tbc: !!opencv-matrix
   rows: 4
   cols: 4
   dt: f
   data: [  0,  0, 1,  0.050,
            -1, 0,  0,  0.000,
             0, -1,  0, 0.060,
             0, 0,  0,  1.0 ]

# IMU noise
IMU.NoiseGyro: 0.001
IMU.NoiseAcc: 0.01
IMU.GyroWalk: 0.0001
IMU.AccWalk: 0.001
IMU.Frequency: 100

#--------------------------------------------------------------------------------------------
# ORB Parameters
#--------------------------------------------------------------------------------------------

# ORB Extractor: Number of features per image
ORBextractor.nFeatures: 1200 # 1000

# ORB Extractor: Scale factor between levels in the scale pyramid 	
ORBextractor.scaleFactor: 1.2

# ORB Extractor: Number of levels in the scale pyramid	
ORBextractor.nLevels: 8

# ORB Extractor: Fast threshold
# Image is divided in a grid. At each cell FAST are extracted imposing a minimum response.
# Firstly we impose iniThFAST. If no corners are detected we impose a lower value minThFAST
# You can lower these values if your images have low contrast			
ORBextractor.iniThFAST: 10
ORBextractor.minThFAST: 5

#--------------------------------------------------------------------------------------------
# Viewer Parameters
#--------------------------------------------------------------------------------------------
Viewer.KeyFrameSize: 0.05
Viewer.KeyFrameLineWidth: 1
Viewer.GraphLineWidth: 0.9
Viewer.PointSize:2
Viewer.CameraSize: 0.08
Viewer.CameraLineWidth: 3
Viewer.ViewpointX: 0
Viewer.ViewpointY: -0.7
Viewer.ViewpointZ: -3.5 # -1.8
Viewer.ViewpointF: 500
```

real_camera_hector_rgbd.yaml:
```
%YAML:1.0

#--------------------------------------------------------------------------------------------
# Camera Parameters. Adjust them!
#--------------------------------------------------------------------------------------------
Camera.type: "PinHole"

# Camera calibration and distortion parameters (OpenCV) 
Camera.fx: 554.2547
Camera.fy: 554.2547
Camera.cx: 320.0
Camera.cy: 240.0

Camera.k1: 0.0
Camera.k2: 0.0
Camera.p1: 0.0
Camera.p2: 0.0

# Camera resolution
Camera.width: 640
Camera.height: 480

# Camera frames per second 
Camera.fps: 25.0

# Color order of the images (0: BGR, 1: RGB. It is ignored if images are grayscale)
Camera.RGB: 1

# Transformation from camera to body-frame (imu)
Tbc: !!opencv-matrix
   rows: 4
   cols: 4
   dt: f
   data: [1, 0, 0, 0.05,
          0, 1, 0, 0.0,
          0, 0, 1, -0.06,
          0, 0, 0, 1.0]


# Depth Threshold (in meters)
ThDepth: 40.0

# RGBD Depth map factor. Usually 5000 for mm to meters conversion in TUM dataset.
DepthMapFactor: 1.0
#--------------------------------------------------------------------------------------------
# ORB Parameters
#--------------------------------------------------------------------------------------------

# ORB Extractor: Number of features per image
ORBextractor.nFeatures: 1200 # 1000

# ORB Extractor: Scale factor between levels in the scale pyramid 	
ORBextractor.scaleFactor: 1.2

# ORB Extractor: Number of levels in the scale pyramid	
ORBextractor.nLevels: 8

# ORB Extractor: Fast threshold
# Image is divided in a grid. At each cell FAST are extracted imposing a minimum response.
# Firstly we impose iniThFAST. If no corners are detected we impose a lower value minThFAST
# You can lower these values if your images have low contrast			
ORBextractor.iniThFAST: 10
ORBextractor.minThFAST: 5

#--------------------------------------------------------------------------------------------
# Viewer Parameters
#--------------------------------------------------------------------------------------------
Viewer.KeyFrameSize: 0.05
Viewer.KeyFrameLineWidth: 1
Viewer.GraphLineWidth: 0.9
Viewer.PointSize:2
Viewer.CameraSize: 0.08
Viewer.CameraLineWidth: 3
Viewer.ViewpointX: 0
Viewer.ViewpointY: -0.7
Viewer.ViewpointZ: -3.5 # -1.8
Viewer.ViewpointF: 500
```


### Use new world 
^Croot@LP-Boston-12214:~/catkin_ws# echo $GAZEBO_MOD_PATH
:/root/catkin_ws/src/gazebo_models_worlds_collection/models

export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/root/catkin_ws/src/gazebo_models_worlds_collection/models

✅ **Done!** Your simulation now runs with 2 autonomous UAVs in Gazebo, each tracked with ORB-SLAM3 and feeding into COVINS for collaborative SLAM processing.
