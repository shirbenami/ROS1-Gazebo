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



