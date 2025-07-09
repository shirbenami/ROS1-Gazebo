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

# Create workspace
RUN mkdir -p /root/catkin_ws/src
WORKDIR /root/catkin_ws/src

# Clone Hector packages
RUN git clone https://github.com/tu-darmstadt-ros-pkg/hector_quadrotor.git \
 && git clone https://github.com/tu-darmstadt-ros-pkg/hector_gazebo.git \
 && git clone https://github.com/tu-darmstadt-ros-pkg/hector_models.git \
 && git clone https://github.com/tu-darmstadt-ros-pkg/hector_localization.git \
 && git clone https://github.com/tu-darmstadt-ros-pkg/hector_components_description.git \
 && git clone https://github.com/tu-darmstadt-ros-pkg/hector_slam.git

WORKDIR /root/catkin_ws

# Install dependencies
RUN rosdep init && rosdep update && \
    rosdep install --from-paths src --ignore-src -r -y

# Build
RUN bash -c "source /opt/ros/melodic/setup.bash && catkin_make"

# Source workspaces by default
RUN echo 'source /opt/ros/melodic/setup.bash' >> ~/.bashrc && \
    echo 'source /root/catkin_ws/devel/setup.bash' >> ~/.bashrc

ENV DISPLAY=:0

CMD ["bash"]
