# 🐢 ROS1 Melodic + Gazebo 9 + TurtleBot3 Simulation

This repository provides a full Docker-based simulation environment with:

- ✅ ROS1 Melodic
- ✅ Gazebo 9 with GUI support
- ✅ `gazebo_ros_pkgs` integration
- ✅ TurtleBot3 simulation + teleoperation

---

## 🚀 Quick Start

### 🐳 1. Clone this repository

```bash
git clone [https://github.com/<your-username>/<your-repo-name>](https://github.com/shirbenami/ROS1-Noetic-Gazebo-11).git
cd <your-repo-name>
```

### 🛠️ 2. Build the Docker Image
```bash
docker build -t ros1-melodic-gazebo .
```

### 🖥️ 3. Enable X11 GUI for Gazebo (on Ubuntu only)
```bash
xhost +local:docker
```

### ▶️ 4. Run the Docker Container

```bash
docker run -it \
  --name ros1-melodic-gazebo-container-new2 \
  --net=host \
  --env="DISPLAY=$DISPLAY" \
  --env="QT_X11_NO_MITSHM=1" \
  --env="ROS_MASTER_URI=http://localhost:11311" \
  --env="ROS_IP=127.0.0.1" \
  --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
  --privileged \
  ros1-melodic-gazebo-container-new2 \
  /bin/bash -c "roscore & sleep 2 && bash"
```

```bash
docker run -it \
  --name ros1-melodic-gazebo-container \
  --env="DISPLAY=$DISPLAY" \
  --env="QT_X11_NO_MITSHM=1" \
  --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
  --privileged \
  ros1-melodic-gazebo
```

### 🤖 5. Inside the Container: Setup TurtleBot3
```bash
chmod +x setup_turtlebot3.sh
./setup_turtlebot3.sh
```

This will:

* Clone TurtleBot3 + Simulations

* Install dependencies

* Compile workspace

* Launch turtlebot3_world.launch in Gazebo

### 🎮 6. Control the Robot (Teleoperation)
In another terminal:

```bash
docker exec -it ros1-gazebo-container bash
source ~/.bashrc
rosrun teleop_twist_keyboard teleop_twist_keyboard.py
```
if it isnt download
```bash
apt update
apt install ros-melodic-teleop-twist-keyboard
```
Use keys i, j, l, , to move the robot.




______________________________________________________________________________________________________________
______________________________________________________________________________________________________________
______________________________________________________________________________________________________________
______________________________________________________________________________________________________________
______________________________________________________________________________________________________________

# Hector Quadrotor Multi-Drone Simulation with ROS1 and Gazebo

## Overview

This project provides a Docker-based environment that integrates **ROS1**, **Gazebo**, and the **Hector Quadrotor** package for multi-drone simulation. The goal is to create a flexible simulation platform for collaborative SLAM and inter-drone detection tasks.

The project also connects the simulation to **ORB-SLAM3** and **COVINS** to test multi-agent SLAM scenarios. In addition, it implements visual detection methods such as template matching and color detection to enable drones to detect each other and share azimuth information.

---

## Features

✅ ROS1-based environment (Noetic or Melodic)
✅ Gazebo simulation with Hector Quadrotor
✅ Multi-drone setup (multiple UAVs in one simulation)
✅ Integration with ORB-SLAM3 and COVINS for collaborative SLAM
✅ Visual inter-drone detection (template matching, color detection)
✅ Communication of detected azimuth between drones

---

## What this project includes

* **Dockerfile** to build a consistent environment with all required dependencies
* Hector Quadrotor packages (`hector_quadrotor_description`, `hector_gazebo_plugins`, etc.)
* Custom ROS packages for:

  * Visual detection (color and template matching)
  * Publishing detection data as ROS topics
* Launch files to spin up multiple drones
* Example configuration for connecting to ORB-SLAM3 and COVINS

---

## How to use

1. **Clone this repository**

   ```bash
   git clone <repository-url>
   cd <repository>
   ```

2. **Build the Docker image**

   ```bash
   docker build -t hector-multi-drone .
   ```

3. **Run the container**

   ```bash
   docker run -it --rm --name hector-sim hector-multi-drone
   ```

4. **Launch the multi-drone simulation**

   ```bash
   source /catkin_ws/devel/setup.bash
   roslaunch <your-multi-uav-launch-file>.launch
   ```

5. **Connect to ORB-SLAM3 / COVINS**

   Make sure your SLAM back-end is running and subscribing to the image and pose topics published by the drones.

6. **Run detection scripts**

   ```bash
   rosrun drone_color_detector color_detector.py
   rosrun drone_template_matcher template_matcher.py
   ```

---

## Project structure

```
project-root/
├── Dockerfile
├── catkin_ws/
│   ├── src/
│   │   ├── hector_quadrotor
│   │   ├── drone_color_detector
│   │   ├── drone_template_matcher
│   │   └── ...
├── launch/
│   ├── multi_uav.launch
│   └── ...
└── README.md
```

---

## Future work

* Improve robustness of visual detection under different lighting conditions
* Automate map merging in COVINS for larger multi-agent scenarios
* Add additional sensors and integrate AprilTags

---

## License

This project is open-source and available under the MIT License.

Feel free to contribute, report issues, or open pull requests!

---

**Happy flying! 🚁**

