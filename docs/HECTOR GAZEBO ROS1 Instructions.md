
# HECTOR GAZEBO ROS1 Instructions

## 1. Start Docker with X11 Permissions

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

## 2. Launch the Gazebo World with Two Agents

Run:

```bash
roslaunch hector_quadrotor_demo gazebo_models_worlds_collection_2_agents.launch
```

**Location:** `~/catkin_ws/src/hector_quadrotor/hector_quadrotor_demo/launch/`

## 3. Takeoff Action for Each UAV

Use the following commands to trigger the takeoff:

```bash
rosrun actionlib axclient.py /uav0/action/takeoff
rosrun actionlib axclient.py /uav1/action/takeoff
```

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
```

```bash
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

## 5. Motion Command Script for Each Agent

**File:** `auto_move_agents.py`  
**Location:** `/catkin_ws/src/hector_quadrotor/hector_move/scripts/`

Run for both agents:

```bash
rosrun hector_move auto_move_agents.py uav0
rosrun hector_move auto_move_agents.py uav1
```
