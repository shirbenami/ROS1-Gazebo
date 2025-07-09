# Dual UAV Hector Quadrotor + ORB-SLAM3 + COVINS Setup

This guide walks you through the full setup for simulating **two Hector Quadrotor UAVs** in Gazebo, sending them independent motion commands, and running **ORB-SLAM3** with **COVINS** for each agent.

---

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
Location: `hector_move/scripts/`

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

### Run for both agents:

```bash
rosrun hector_move auto_move_agents.py uav0
rosrun hector_move auto_move_agents.py uav1
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

✅ **Done!** Your simulation now runs with 2 autonomous UAVs in Gazebo, each tracked with ORB-SLAM3 and feeding into COVINS for collaborative SLAM processing.
