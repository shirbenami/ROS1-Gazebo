# ROS1 Hector Quadrotor Multi-Drone Simulation

This repository provides a **full Docker-based simulation environment** with:

✅ **ROS1 Melodic**
✅ **Gazebo 9 with GUI support**
✅ **Hector Quadrotor drones**

It is designed for simulating **Hector Quadrotor drones** in multi-drone scenarios, connecting to **ORB-SLAM3** and **COVINS**, and running visual detection tasks like **color detection** and **template matching**.

---

## 🚀 **Project Goals**

* Run indoor quadrotor simulations in Gazebo
* Use Hector SLAM for mapping and localization
* Enable multi-drone interaction
* Connect to ORB-SLAM3 / COVINS for collaborative SLAM
* Detect drones visually and exchange azimuth info

---

## 🗂️ **Repository Structure**

```plaintext

├── catkin_ws/
│   ├── hector_move/
│   ├── src/
│   │   ├── hector_quadrotor/
│   │   ├── hector_gazebo/
│   │   ├── hector_models/
│   │   ├── hector_localization/
│   │   ├── hector_components_description/
│   │   ├── hector_slam/
│   │   ├── gazebo_models_worlds_collection
│   │   ├── drone_color_detector
│   │   ├── drone_template_matcher
│   ├── build/ 
│   ├── devel/ 
├── Dockerfile
├── docs/
├── README.md
```

---

## ⚙️ **How to Build & Run**

1️⃣ **Clone the repository:**

```bash
git clone https://github.com/shirbenami/ROS1-Gazebo.git
cd ROS1-Gazebo
```

2️⃣ **Build the Docker image:**

```bash
docker build -t hector-multi-drone .
```

3️⃣ **Run the container:**

```bash
xhost +local:root

docker run -it --rm \
  --net=host \
  --env="DISPLAY=$DISPLAY" \
  --env="QT_X11_NO_MITSHM=1" \
  --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
  hector-multi-drone
```

4️⃣ **Build the workspace:**

```bash
cd /root/catkin_ws
catkin_make
source devel/setup.bash
```

5️⃣ **Launch the indoor world:**

```bash
roslaunch hector_quadrotor_demo indoor_custom.launch
```

6️⃣ **Run detection scripts:**

```bash
rosrun drone_color_detector color_detector.py
rosrun drone_template_matcher template_matcher.py
```

7️⃣ **Connect ORB-SLAM3 / COVINS:**
Ensure your SLAM node subscribes to the drone’s image topic- /uav(0/1)/front_cam/camera/image /uav(0/1)/raw_imu and so on.

---
## 🎥 **Demo Videos**

* Multi-Drone SLAM Example:Example of two Hector Quadrotor drones connected to COVINS and performing collaborative ORB-SLAM3.
  

https://github.com/user-attachments/assets/9411a788-c731-4823-bfd4-2713ea773977




* Color & Template Detection Example:Example of two drones (one red, one blue) detecting each other visually and exchanging azimuth information.
  

https://github.com/user-attachments/assets/c51ba8fc-5d64-4aa5-bbd6-d253c7d92226



## 📌 **Notes**

* If models don’t appear in Gazebo, add:

  ```bash
  export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/root/catkin_ws/src/hector_gazebo/hector_gazebo_worlds/models
  ```
* For move the hector drone:

  ```bash
  rosrun hector_move auto_move_agents_forward_rotate.py 
  ```

---


---

## 📜 **License**

MIT License — feel free to fork, use and contribute!

**Happy flying! 🚁**
