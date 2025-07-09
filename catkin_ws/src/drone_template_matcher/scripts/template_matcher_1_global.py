#!/usr/bin/env python


import rospy
import cv2
import numpy as np
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from std_msgs.msg import Float32
from geometry_msgs.msg import PoseStamped
import tf.transformations as tf
import math

class DroneTemplateMatcher:
    def __init__(self, camera_topic):
        rospy.init_node('template_matching_azimuth', anonymous=True)

        self.image_sub = rospy.Subscriber(camera_topic, Image, self.image_callback)
        drone_name = camera_topic.split('/')[1]

        pub_topic = drone_name + '/detected_drone_azimuth'
        self.azimuth_pub = rospy.Publisher('/' + pub_topic, Float32, queue_size=1)

        abs_pub_topic = drone_name + '/detected_drone_absolute_azimuth'
        self.absolute_azimuth_pub = rospy.Publisher('/' + abs_pub_topic, Float32, queue_size=1)

        self.template = cv2.imread('/root/catkin_ws/src/drone_template_matcher/images/image.png', 0) 
        scale = 0.3  
        self.template_small = cv2.resize(self.template, (0,0), fx=scale, fy=scale)
        print("Template size:", self.template_small.shape)
        self.w, self.h = self.template_small.shape[::-1]

        self.bridge = CvBridge()
        self.FOV = 90 


        self.current_yaw = None

        self.pose_sub = rospy.Subscriber(
            '/' + drone_name + '/ground_truth_to_tf/pose',
            PoseStamped,
            self.pose_callback
        )
    
    def pose_callback(self, msg):
        quat = [
            msg.pose.orientation.x,
            msg.pose.orientation.y,
            msg.pose.orientation.z,
            msg.pose.orientation.w
        ]
        euler = tf.euler_from_quaternion(quat)
        self.current_yaw = math.degrees(euler[2])

    def image_callback(self, msg):
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='mono8')
        img_w = cv_image.shape[1]
        print("Camera frame size:", cv_image.shape)

        # Template Matching
        res = cv2.matchTemplate(cv_image, self.template_small, cv2.TM_CCOEFF_NORMED)
        _, _, _, max_loc = cv2.minMaxLoc(res)

        top_left = max_loc
        x_center = top_left[0] + self.w / 2

        x_norm = (x_center - img_w/2) / (img_w/2)
        azimuth = x_norm * (self.FOV / 2)


        rospy.loginfo("Azimuth: {:.2f} deg".format(azimuth))
        self.azimuth_pub.publish(azimuth)

        if self.current_yaw is not None:
            absolute_azimuth = self.current_yaw + azimuth
            absolute_azimuth = (absolute_azimuth + 180) % 360 - 180
            self.absolute_azimuth_pub.publish(absolute_azimuth)
            rospy.loginfo("Absolute Azimuth: {:.2f} deg".format(absolute_azimuth))
        else:
            rospy.logwarn("Yaw not available yet!")

        bottom_right = (top_left[0] + self.w, top_left[1] + self.h)
        color_image = cv2.cvtColor(cv_image, cv2.COLOR_GRAY2BGR)
        cv2.rectangle(color_image, top_left, bottom_right, (0, 0, 255), 2)
        cv2.imshow('Template Match', color_image)
        cv2.waitKey(1)

        print("x_center =", x_center)
        print("x_norm =", x_norm)
        print("azimuth =", azimuth)

if __name__ == '__main__':
    camera_topic = rospy.get_param('~camera_topic','/uav1/front_cam/camera/image')
    DroneTemplateMatcher(camera_topic)
    rospy.spin()
