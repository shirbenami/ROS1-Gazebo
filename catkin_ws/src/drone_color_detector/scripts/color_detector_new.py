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

class DroneColorDetector:
    def __init__(self, camera_topic, color):
        self.bridge = CvBridge()
        self.FOV = 90  # degrees
        self.color = color  # 'red' or 'blue'

        self.current_yaw = None

        self.image_sub = rospy.Subscriber(camera_topic, Image, self.image_callback)
        drone_name = camera_topic.split('/')[1]

        pub_topic = drone_name + '/detected_drone_azimuth'
        self.azimuth_pub = rospy.Publisher('/' + pub_topic, Float32, queue_size=1)

        abs_pub_topic = drone_name + '/detected_drone_absolute_azimuth'
        self.absolute_azimuth_pub = rospy.Publisher('/' + abs_pub_topic, Float32, queue_size=1)

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
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        img_w = cv_image.shape[1]

        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)

        if self.color == 'red':
            lower1 = (0, 150, 120)
            upper1 = (10, 255, 255)
            lower2 = (170, 150, 120)
            upper2 = (180, 255, 255)
            mask1 = cv2.inRange(hsv, lower1, upper1)
            mask2 = cv2.inRange(hsv, lower2, upper2)
            mask = mask1 + mask2
        elif self.color == 'blue':
            lower = (100, 150, 0)
            upper = (140, 255, 255)
            mask = cv2.inRange(hsv, lower, upper)
        else:
            rospy.logerr("Unsupported color: {}".format(self.color))
            return

        cv2.imshow("Mask", mask)
        cv2.waitKey(1)

        _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)
            area = cv2.contourArea(c)
            #rospy.loginfo("contour area: {}".format(area))

            x,y,w,h = cv2.boundingRect(c)
            cv2.rectangle(cv_image, (x,y), (x+w, y+h), (0,255,0), 2)

            if M["m00"] != 0:
                x,y,w,h = cv2.boundingRect(c)
                cx = float(x + w/2.0)
                center_x = float(img_w) / 2.0
                #rospy.loginfo("===================")
                #rospy.loginfo("cx: {:.2f}".format(cx))
                #rospy.loginfo("center_x: {:.2f}".format(center_x))
                #rospy.loginfo("===================")

                x_norm = (cx - center_x) / center_x

                azimuth = x_norm * (self.FOV / 2)

                #rospy.loginfo("===================")
                #rospy.loginfo("x_norm: {:.2f}".format(x_norm))
                #rospy.loginfo("azimuth: {:.2f}".format(azimuth))
                rospy.loginfo("===================")

                self.azimuth_pub.publish(azimuth)

                if self.current_yaw is not None:
                    #rospy.loginfo("YAW: {:.2f} ".format(self.current_yaw))

                    absolute_azimuth = abs((self.current_yaw + azimuth +180 ) % 360 - 180)
                    rospy.loginfo("Absolute Azimuth: {:.2f} deg".format(absolute_azimuth))
                    self.absolute_azimuth_pub.publish(absolute_azimuth)
                else:
                    rospy.logwarn("Yaw not available yet!")

                # Draw detected blob
                cv2.circle(cv_image, (int(cx), int(cv_image.shape[0] / 2)), 5, (0, 255, 0), -1)
                cv2.imshow("Detected Blob", cv_image)
                cv2.waitKey(1)
            else:
                rospy.logwarn("Contour found but zero area!")
        else:
            rospy.logwarn("No contours detected.")

if __name__ == '__main__':
    rospy.init_node('color_detector_azimuth', anonymous=True)
    camera_topic = rospy.get_param('~camera_topic', '/uav1/front_cam/camera/image')
    color = rospy.get_param('~color', 'red')
    DroneColorDetector(camera_topic, color)
    rospy.spin()
