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

# 🐳 ROS1 Noetic + Gazebo 11 Docker Setup Guide

This guide walks you through creating a Docker-based development environment with:

✅ ROS1 Noetic  
✅ Gazebo 11  
✅ `gazebo_ros_pkgs` for ROS-Gazebo integration  
✅ GUI support (launch Gazebo with full display)  
✅ 🐢 TurtleBot3 full simulation and teleoperation  

---

## 📁 Step 1: Create Project Folder and Dockerfile

First, create a working directory and a `Dockerfile`:

```bash
mkdir -p ~/ros1_gazebo_docker && cd ~/ros1_gazebo_docker
touch Dockerfile

  GNU nano 7.2                   Dockerfile                             
FROM ros:melodic

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key >
 && apt update && apt install -y \
    git wget nano curl lsb-release gnupg2 \
    python-rosdep python-catkin-tools \
    ros-melodic-desktop-full \
    ros-melodic-gazebo-ros-pkgs \
    ros-melodic-gazebo-ros-control \
 && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /root/catkin_ws/src
WORKDIR /root/catkin_ws

RUN bash -c 'source /opt/ros/melodic/setup.bash && catkin_make'

RUN echo "source /opt/ros/melodic/setup.bash" >> ~/.bashrc && \
    echo "source /root/catkin_ws/devel/setup.bash" >> ~/.bashrc

ENV DISPLAY=:0

```

## 🧱 Step 2: Build the Docker Image

From the project directory, build the Docker image:

```bash
docker build -t ros1-gazebo .
```

## 🖥️ Step 3: Run the Container with GUI Support
If you're running on a local Ubuntu machine:

```bash
xhost +local:docker
```

Then run the container:
```bash
docker run -it \
  --name ros1-gazebo-container \
  --env="DISPLAY=$DISPLAY" \
  --env="QT_X11_NO_MITSHM=1" \
  --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
  --privileged \
  ros1-gazebo
```

## 🧪 Step 4: Test the Setup
Inside the container:
```bash
roslaunch gazebo_ros empty_world.launch
```

## 🤖 Step 5: Add TurtleBot3 Simulation
To automatically install and run the TurtleBot3 simulation, use the following script.

🧾 File: setup_turtlebot3.sh
Inside the container, create the script:

```bash
nano setup_turtlebot3.sh
Paste the following content:
```
```bash
#!/bin/bash

  GNU nano 2.9.3  setup_turtlebot3_melodic.sh             

mkdir -p ~/catkin_ws/src
cd ~/catkin_ws/src

git clone -b noetic-devel https://github.com/ROBOTIS-GIT/turtlebot3.git
git clone -b noetic-devel https://github.com/ROBOTIS-GIT/turtlebot3_simulations.git

cd ~/catkin_ws
rosdep update
rosdep install --from-paths src --ignore-src -r -y

catkin_make

echo "export TURTLEBOT3_MODEL=waffle" >> ~/.bashrc
export TURTLEBOT3_MODEL=waffle

source /opt/ros/melodic/setup.bash
source devel/setup.bash

roslaunch turtlebot3_gazebo turtlebot3_world.launch

```

Make it executable and run:
```bash
chmod +x setup_turtlebot3.sh
./setup_turtlebot3.sh
```
