FROM ros:melodic

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654 \
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
