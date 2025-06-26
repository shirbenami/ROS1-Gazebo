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

✅ auto_move_agents_walls.py:
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
        rospy.init_node("uav0_obstacle_avoidance")  # Initialize ROS node

        self.bridge = CvBridge()
        
        # Subscribe to depth image and set up publisher for velocity commands
        self.depth_sub = rospy.Subscriber("/uav0/camera/depth/image_raw", Image, self.depth_callback)
        self.cmd_pub = rospy.Publisher("/uav0/cmd_vel", Twist, queue_size=1)

        # Minimum distance to wall before taking avoidance action
        self.min_safe_distance = 1.0  # in meters

    def depth_callback(self, msg):
        # Convert the depth image from ROS to OpenCV format
        depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
        depth_array = np.array(depth_image, dtype=np.float32)

        # Get image dimensions
        height, width = depth_array.shape

        # Define a small central region to check forward distance
        center_region = depth_array[height//2 - 10:height//2 + 10, width//2 - 10:width//2 + 10]

        # Get the minimum distance in the center region
        min_distance = np.nanmin(center_region)

        # Create a Twist message for movement
        twist = Twist()

        if np.isnan(min_distance):
            rospy.logwarn("No valid depth data!")
            twist.linear.x = 0.0  # Stop
        elif min_distance < self.min_safe_distance:
            rospy.loginfo("Obstacle ahead at {:.2f} m - turning...".format(min_distance))
            twist.linear.x = 0.0
            twist.angular.z = 0.5  # Rotate to avoid wall
        else:
            rospy.loginfo("Clear path ({:.2f} m) - moving forward.".format(min_distance))
            twist.linear.x = 0.3  # Move forward
            twist.angular.z = 0.0

        # Send command to drone
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

---

### Use new world 
^Croot@LP-Boston-12214:~/catkin_ws# echo $GAZEBO_MOD_PATH
:/root/catkin_ws/src/gazebo_models_worlds_collection/models

export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/root/catkin_ws/src/gazebo_models_worlds_collection/models

✅ **Done!** Your simulation now runs with 2 autonomous UAVs in Gazebo, each tracked with ORB-SLAM3 and feeding into COVINS for collaborative SLAM processing.
