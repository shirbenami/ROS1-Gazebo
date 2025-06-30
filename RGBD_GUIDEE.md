
# Instructions for Running ORB_SLAM3 RGBD Node with Docker

This guide explains step-by-step how to enable and run the **RGBD** node in the **ORB_SLAM3** package with Docker.

---

## ✅ 1️⃣ Unhide the RGBD Node in `CMakeLists.txt`

1. Open the `CMakeLists.txt` file:

   ```bash
   nano /home/user1/ws/covins_ws/src/covins/orb_slam3/Examples/ROS/ORB_SLAM3/CMakeLists.txt
   ```

2. Find the lines for the **RGBD** executable. Remove the `#` signs if they exist, so they look like this:

   ```cmake
   ## Node for RGB-D camera
   rosbuild_add_executable(RGBD
     src/ros_rgbd.cc
   )

   target_link_libraries(RGBD
     ${LIBS}
   )
   ```

3. Save and close the file (`Ctrl+O`, `Enter`, `Ctrl+X`).

---

## ✅ 2️⃣ Rebuild the Workspace

Go to your workspace and rebuild:

```bash
cd ~/covins_ws
catkin build
```

**OR** (if you use `catkin_make`):

```bash
rm -rf build devel
catkin_make
```

---

## ✅ 3️⃣ Update `run.sh`

In your `run_rgbd.sh` script, update the **ROS_CLIENT** block to launch the **RGBD** node and enable X11 forwarding.
/home/shirb/ws/covins_ws/src/covins/docker/run_rgbd.sh

**Example:**

```
elif [ $ROS_CLIENT -eq 1 ]; then
        CONFIG_FILE_COMM=$(absPath ${*: -2:1})
        LAUNCH_FILE=$(absPath ${*: -1})
        docker run \
        -it \
        --rm \
        --net=host \
        -env="DISPLAY"  \
        --env="QT_X11_NO_MITSHM=1" \
        --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
        --volume "${CONFIG_FILE_COMM}:${CATKIN_WS}/src/covins/covins_comm/config/config_comm.yaml" \
        --volume "${LAUNCH_FILE}:${CATKIN_WS}/src/covins/orb_slam3/Examples/ROS/ORB_SLAM3/launch/launch_docker_ros_gazebo_agent0_rgbd.launch" \
        --volume "/home/shirb/ws/covins_ws/src/covins/orb_slam3/Examples/real_camera_hector_rgbd.yaml:${CATKIN_WS}/src/covins/orb_slam3/Examples/real_camera_hector_rgbd.yaml" \
        covins \
        /bin/bash \
       # /bin/bash -c \
       #         "cd ${CATKIN_WS}; \
        #         source devel/setup.bash; \
         #        roslaunch ORB_SLAM3 launch_docker_ros_gazebo_agent0_rgbd.launch"
```

---

## ✅ 4️⃣ Allow X11 Access

On your host machine (outside Docker), run:

```bash
xhost +local:root
```

This gives your container permission to open graphical windows.

---

## ✅ 5️⃣ Verify the `launch` File

Check that your **RGBD launch file** is correct, with the right **remaps**:

\`\`\`xml
<?xml version="1.0"?>
<launch>

<param name="use_sim_time" value="true"/>

<arg name="ag_n" default="0" />
<arg name="voc" default="/root/covins_ws/src/covins/orb_slam3/Vocabulary/ORBvoc.txt" />
<arg name="cam" default="/root/covins_ws/src/covins/orb_slam3/Examples/real_camera_hector_rgbd.yaml" />

<node pkg="ORB_SLAM3" type="RGBD" name="ORB_SLAM3_rgbd_$(arg ag_n)" args="$(arg voc) $(arg cam)" output="screen"> 

    <remap from="/camera/rgb/image_raw" to="/uav0/camera/rgb/image_raw"/>
    <remap from="/camera/depth_registered/image_raw" to="/uav0/camera/depth/image_raw"/>

</node>

</launch>
\`\`\`

---

## ✅ 6️⃣ Run the System

Finally, launch the RGBD node:

```bash
source devel/setup.bash
roslaunch ORB_SLAM3 launch_docker_ros_gazebo_hector_rgbd.launch
```

**Or run the script:**

```bash
./run.sh
```

---

## ✅ 7️⃣ Verify

After starting, check `rqt_graph` to ensure:
- The RGBD node is running.
- The topics are connected to `/uav0/camera/rgb/image_raw` and `/uav0/camera/depth/image_raw`.

---

## ✅ Summary Checklist

✔️ Unhide the RGBD node in `CMakeLists.txt`  
✔️ Rebuild the workspace  
✔️ Update `run.sh` with the correct launch file and X11 settings  
✔️ Run `xhost +local:root` on the host  
✔️ Check the `launch` file remaps  
✔️ Launch and verify in `rqt_graph`

---

Good luck! 🚀✨
