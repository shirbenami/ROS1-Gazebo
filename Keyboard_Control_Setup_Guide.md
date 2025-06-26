# 🚁 Hector Quadrotor - Keyboard Control Setup Guide

This guide explains how to control a simulated quadrotor using your keyboard inside the Hector Quadrotor Gazebo simulation (ROS Melodic).
It walks through installing dependencies, setting up the keyboard bridge, enabling motors, and successfully flying the drone using keys.

---

## 🧩 Prerequisites

* ROS Melodic installed (tested on Ubuntu 18.04)
* `hector_quadrotor` stack cloned into `~/catkin_ws/src`
* Workspace built and sourced:

```bash
cd ~/catkin_ws
catkin_make
source devel/setup.bash
```

---

# 🕹️ Hector Quadrotor Keyboard Control Setup with Bridge

This guide explains how to control the Hector Quadrotor in Gazebo using your **keyboard**. It sets up a **ROS bridge node** to convert `cmd_vel` messages into position control commands, and connects that to the quadrotor simulation.

---

## ✅ Prerequisites

Make sure you have the following:

* ROS (tested on Melodic)
* `hector_quadrotor` packages installed
* `teleop_twist_keyboard` installed
* `keyboard_teleop_bridge` custom bridge (see below)

---

## 📁 Folder Structure

```
~/catkin_ws/src/
├── hector_quadrotor/...
├── keyboard_teleop_bridge/
│   └── scripts/
│       └── cmdvel_bridge.py
```

---

## 1️⃣ Run the Hector Quadrotor Simulation

```bash
roslaunch hector_quadrotor_demo indoor_slam_gazebo.launch
```

Wait until Gazebo is fully loaded.

---

## 2️⃣ Create the Keyboard Bridge Script

Inside your ROS workspace:

```bash
cd ~/catkin_ws/src
catkin_create_pkg keyboard_teleop_bridge rospy geometry_msgs
mkdir -p keyboard_teleop_bridge/scripts
```

Then create the bridge script:

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
from geometry_msgs.msg import Twist, PoseStamped

def callback(msg):
    pose = PoseStamped()
    pose.header.stamp = rospy.Time.now()
    pose.header.frame_id = "world"

    pose.pose.position.x = 0.0
    pose.pose.position.y = 0.0
    pose.pose.position.z = 1.0 + msg.linear.x * 1.0  # תרגום תנועה קדימה לגובה

    pose.pose.orientation.x = 0.0
    pose.pose.orientation.y = 0.0
    pose.pose.orientation.z = 0.0
    pose.pose.orientation.w = 1.0

    pub.publish(pose)

rospy.init_node('cmdvel_to_pose_bridge')
pub = rospy.Publisher('/command/pose', PoseStamped, queue_size=10)
rospy.Subscriber('/cmd_vel', Twist, callback)
rospy.spin()
```

```bash
cd keyboard_teleop_bridge/scripts
nano cmdvel_bridge.py
```

Paste the following Python code:

```python
#!/usr/bin/env python
import rospy
from geometry_msgs.msg import Twist, PoseStamped

pub = None

def callback(msg):
    pose = PoseStamped()
    pose.header.stamp = rospy.Time.now()
    pose.header.frame_id = "world"
    pose.pose.position.x = 0
    pose.pose.position.y = 0
    pose.pose.position.z = 2.0  # Constant height
    pose.pose.orientation.w = 1.0
    pub.publish(pose)

def main():
    global pub
    rospy.init_node('cmdvel_to_pose_bridge')
    pub = rospy.Publisher('/command/pose', PoseStamped, queue_size=1)
    rospy.Subscriber('/cmd_vel', Twist, callback)
    rospy.spin()

if __name__ == '__main__':
    main()
```

Make it executable:

```bash
chmod +x cmdvel_bridge.py
```

---

## 3️⃣ Build the workspace

```bash
cd ~/catkin_ws
catkin_make
source devel/setup.bash
```

---

## 4️⃣ Run everything

In **Terminal 1**:

```bash
roslaunch hector_quadrotor_demo indoor_slam_gazebo.launch
```

In **Terminal 2**:

```bash
rosrun keyboard_teleop_bridge cmdvel_bridge.py
```

In **Terminal 3**:

```bash
rosrun teleop_twist_keyboard teleop_twist_keyboard.py
```

Use the keyboard (WASD keys) to control the quadrotor!

---

## ✅ Notes

* The bridge converts `cmd_vel` messages from the keyboard into `PoseStamped` messages that are published to `/command/pose`.
* You must **make sure** no other node (like `/pose_action`) is publishing to `/command/pose`.
* You can disable conflicting nodes using:

```bash
rosnode kill /pose_action
```

### 5. Enable Motors - Takeoff Action

The motors are disabled by default. To activate them, run:

```bash
rostopic pub /command/takeoff std_msgs/Empty "{}"
```

> 🛑 You **must** take off before trying to control the drone with keyboard!

---

### 6. Fly Using Keyboard

Use the keyboard to move the drone:

* Arrow keys or ASWD for translation
* Space, Shift, or other keys as configured to adjust thrust or yaw

📌 Check `key_teleop` documentation to configure specific key bindings if needed.

---

## ✅ Tips

* Use `rqt_graph` to debug connections between nodes
* Always check `/command/takeoff` was triggered if drone isn't moving
* Run `rostopic echo /command/twist` to verify messages are being published
* use 'rosservice call /gazebo/reset_simulation' to reset map

---

## 📦 Related Packages

* `hector_quadrotor_teleop`
* `teleop_tools` (contains `key_teleop`)
* `geometry_msgs/TwistStamped`

---

## 🧪 Optional Debug Commands

Check active nodes:

```bash
rosnode list
```

Check topic info:

```bash
rostopic info /command/twist
```

Kill stuck nodes:

```bash
rosnode kill /pose_action
```

🚫 Pause Gazebo Physics (Freeze the World)

To stop all physics simulation (everything will freeze in place):

```bash
rosservice call /gazebo/pause_physics
```
To continue the simulation after pausing:

```
rosservice call /gazebo/unpause_physics
```
🎥 Record Sensor Data with rosbag
```
rosbag record /front_cam/camera/image /raw_imu -O test.bag

rosbag record /uav0/front_cam/camera/image /uav0/raw_imu /uav0/ground_truth_to_tf/pose \
```
🔁 Replay the Bag File
```
rosbag play test.bag --clock
```
## 🥳 That's It!

You now have full control of the simulated Hector Quadrotor using your keyboard.


OR create a command file:
```
nano ~/catkin_ws/src/hector_move/scripts/auto_move.py
```

```
#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist

def move():
    rospy.init_node('hector_auto_move')
    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
    rate = rospy.Rate(10)  # 10 Hz

    twist = Twist()
    twist.linear.x = 0.5
    twist.angular.z = 0.15

    rospy.loginfo("Publishing motion command...")
    while not rospy.is_shutdown():
        pub.publish(twist)
        rate.sleep()

if __name__ == '__main__':
    try:
        move()
    except rospy.ROSInterruptException:
        pass

```
םר 
