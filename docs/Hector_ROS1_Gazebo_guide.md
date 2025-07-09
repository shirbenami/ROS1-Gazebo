
# 🚁 Hector Quadrotor Simulation on ROS1 Melodic + Gazebo 9 (Docker-Compatible)

This guide walks you through setting up the `hector_quadrotor` package for an indoor drone simulation in **ROS1 Melodic** and **Gazebo 9**. The setup works great inside Docker or on a native Ubuntu 18.04 system.

---

## 📁 Step 1: Create a Catkin Workspace

```bash
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws
catkin_make
```

---

## 🔽 Step 2: Clone Required Repositories

```bash
cd ~/catkin_ws/src

# Main quadrotor package
git clone https://github.com/tu-darmstadt-ros-pkg/hector_quadrotor.git

# Gazebo worlds and plugins
git clone https://github.com/tu-darmstadt-ros-pkg/hector_gazebo.git

# Models for sensors and parts
git clone https://github.com/tu-darmstadt-ros-pkg/hector_models.git

# Localization (EKF, odometry)
git clone https://github.com/tu-darmstadt-ros-pkg/hector_localization.git

# Extra URDF and xacro components
git clone https://github.com/tu-darmstadt-ros-pkg/hector_components_description.git

# SLAM and mapping support
git clone https://github.com/tu-darmstadt-ros-pkg/hector_slam.git
```

---

## 🧩 Step 3: Fix Geographic Msgs Dependency

If you encounter an error about `geographic_msgs`:

```bash
sudo apt update
sudo apt install -y ros-melodic-geographic-msgs
```

---

## 📦 Step 4: Install ROS Dependencies

```bash
cd ~/catkin_ws
rosdep update
rosdep install --from-paths src --ignore-src -r -y
```

If `rosdep` fails:
```bash
sudo rosdep init
rosdep update
```

---

## 🏗️ Step 5: Build the Workspace

```bash
catkin_make
```

---

## 🧠 Step 6: Source the Workspace

```bash
echo "source ~/catkin_ws/devel/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

---

## 🌍 Step 7: Custom Launch File with Indoor World

Create a new launch file at:

```
~/catkin_ws/src/hector_quadrotor/hector_quadrotor_demo/launch/indoor_custom.launch
```

Paste the following:

```xml
<?xml version="1.0"?>
<launch>

  <!-- Load indoor scenario -->
  <include file="$(find hector_gazebo_worlds)/launch/sick_robot_day_2014.world.launch"/>

  <!-- Spawn drone with LIDAR and camera -->
  <include file="$(find hector_quadrotor_gazebo)/launch/spawn_quadrotor.launch">
    <arg name="model" value="$(find hector_quadrotor_description)/urdf/quadrotor_hokuyo_utm30lx.gazebo.xacro"/>
    <arg name="controllers" value="
        controller/attitude
        controller/velocity
        controller/position
    "/>
  </include>

  <!-- Launch Hector SLAM (optional) -->
  <include file="$(find hector_mapping)/launch/mapping_default.launch">
    <arg name="odom_frame" value="world"/>
  </include>

</launch>
```

---

## 🚀 Step 8: Launch the Simulation

```bash
roslaunch hector_quadrotor_demo indoor_custom.launch
```

---

## 📦 Step 9 (Optional): Fix Missing Models

If the world appears empty or models are missing:

```bash
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:~/catkin_ws/src/hector_gazebo/hector_gazebo_worlds/models
```

To make it persistent:

```bash
echo 'export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:~/catkin_ws/src/hector_gazebo/hector_gazebo_worlds/models' >> ~/.bashrc
source ~/.bashrc
```

---

## 🕹️ Step 10 (Optional): Control the Drone via Keyboard

```bash
sudo apt install -y ros-melodic-teleop-twist-keyboard
rosrun teleop_twist_keyboard teleop_twist_keyboard.py
```

Ensure the published topic is `/cmd_vel`.

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

```

## ✅ Result

You now have a working indoor quadrotor simulation with:
- LIDAR, IMU, and camera
- SLAM via `hector_mapping`
- Indoor Gazebo environment
- Optional keyboard control

---

## 🧠 Next Steps

- Integrate `ORB-SLAM2` or `ORB-SLAM3` on the camera feed
- Replace LIDAR SLAM with Visual SLAM
- Train reinforcement learning agents using this environment
