#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import numpy as np

class UAV0AvoidWalls:
    def __init__(self):
        rospy.init_node("uav0_obstacle_avoidance")  # Initialize the node

        self.bridge = CvBridge()
        self.depth_sub = rospy.Subscriber("/uav0/camera/depth/image_raw", Image, self.depth_callback)
        self.cmd_pub = rospy.Publisher("/uav0/cmd_vel", Twist, queue_size=1)

        self.min_safe_distance = 1.0  # Distance in meters to start avoiding wall

    def depth_callback(self, msg):
        # Convert ROS depth image to NumPy array
        depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
        depth_array = np.array(depth_image, dtype=np.float32)

        # Get the shape of the depth image
        height, width = depth_array.shape

        # Take a small square in the center of the image (looking forward)
        center_region = depth_array[height//2 - 10:height//2 + 10, width//2 - 10:width//2 + 10]

        # Find the minimum (closest) distance in that center region
        min_distance = np.nanmin(center_region)

        # Create a velocity message
        twist = Twist()

        if np.isnan(min_distance):
            # No valid depth data (all values are NaN)
            rospy.logwarn("No valid depth data!")
            twist.linear.x = 0.0  # Stop
        elif min_distance < self.min_safe_distance:
            # Obstacle is too close - rotate to avoid it
            rospy.loginfo("Obstacle ahead at {:.2f} m - turning...".format(min_distance))
            twist.linear.x = 0.1
            twist.angular.z = 0.5  # Rotate in place
        else:
            # No obstacle - move forward
            rospy.loginfo("Clear path ({:.2f} m) - moving forward.".format(min_distance))
            twist.linear.x = 0.2  # Move forward
            twist.angular.z = 0.15

        # Publish the velocity command
        self.cmd_pub.publish(twist)

if __name__ == '__main__':
    try:
        UAV0AvoidWalls()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
