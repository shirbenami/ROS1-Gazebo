#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
from sensor_msgs.msg import Image, Imu
from geometry_msgs.msg import TwistStamped
from cv_bridge import CvBridge
import numpy as np
import cv2

class MonoCameraAvoidance:
    def __init__(self):
        rospy.init_node("mono_obstacle_avoidance")

        self.bridge = CvBridge()

        # Subscribe to camera and IMU
        self.image_sub = rospy.Subscriber("/uav0/front_cam/camera/image", Image, self.image_callback)
        self.imu_sub = rospy.Subscriber("/uav0/raw_imu", Imu, self.imu_callback)

        # Publish velocity commands
        self.cmd_pub = rospy.Publisher("/uav0/command/twist", TwistStamped, queue_size=1)

        self.forward_accel = 0.0
        self.obstacle_detected = False

    def imu_callback(self, msg):
        # Read forward acceleration (assuming x is forward)
        self.forward_accel = msg.linear_acceleration.x

    def image_callback(self, msg):
        # Convert the image to grayscale (mono)
        gray_img = self.bridge.imgmsg_to_cv2(msg, desired_encoding="mono8")

        # Crop a center region
        h, w = gray_img.shape
        center = gray_img[h//2 - 20:h//2 + 20, w//2 - 20:w//2 + 20]

        # Compute the variance in the center of the image
        variance = np.var(center)

        # Low variance = possibly flat wall surface
        if variance < 40:
            self.obstacle_detected = True
            rospy.loginfo("Low texture detected - possible wall.")
        else:
            self.obstacle_detected = False

        # Build velocity command
        twist_msg = TwistStamped()
        twist_msg.header.stamp = rospy.Time.now()
        twist_msg.header.frame_id = "base_stabilized"


        if self.obstacle_detected or self.forward_accel > 1.5:
            twist_msg.twist.linear.x = 0.05
            twist_msg.twist.angular.z = 0.4  # Rotate in place
            rospy.loginfo("Obstacle detected - turning")
        else:
            twist_msg.twist.linear.x = 0.2
            twist_msg.twist.angular.z = 0.4
            rospy.loginfo("Path is clear - moving forward")

        self.cmd_pub.publish(twist_msg)

if __name__ == '__main__':
    try:
        MonoCameraAvoidance()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
