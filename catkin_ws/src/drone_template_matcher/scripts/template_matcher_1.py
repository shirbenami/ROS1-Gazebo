#!/usr/bin/env python

import rospy
import cv2
import numpy as np
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from std_msgs.msg import Float32

class DroneTemplateMatcher:
    def __init__(self, camera_topic):
        rospy.init_node('template_matching_azimuth', anonymous=True)

        self.image_sub = rospy.Subscriber(camera_topic, Image, self.image_callback)
        pub_topic = camera_topic.split('/')[1] + '/detected_drone_azimuth'
        self.azimuth_pub = rospy.Publisher('/' + pub_topic, Float32, queue_size=1)

        self.template = cv2.imread('/root/catkin_ws/src/drone_template_matcher/images/image.png', 0) 
        scale = 0.3  
        self.template_small = cv2.resize(self.template, (0,0), fx=scale, fy=scale)
        print("Template size:", self.template_small.shape)
        self.w, self.h = self.template_small.shape[::-1]

        self.bridge = CvBridge()
        self.FOV = 90 

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
        azimuth_deg = np.rad2deg(azimuth)


        rospy.loginfo("Azimuth: {:.2f} deg".format(azimuth))
        self.azimuth_pub.publish(azimuth)

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
