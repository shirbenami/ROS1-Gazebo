#!/usr/bin/env python
import rospy
from sensor_msgs.msg import Image
from std_msgs.msg import Float32
import cv2
from cv_bridge import CvBridge

class ColorDetector:
    def __init__(self, color):
        self.bridge = CvBridge()
        self.color = color  # 'blue' or 'red'
        self.pub = rospy.Publisher('detected_drone_azimuth', Float32, queue_size=10)
        rospy.Subscriber('/front_cam/camera/image', Image, self.image_callback)

    def image_callback(self, msg):
        # Convert ROS Image to OpenCV
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)

        if self.color == 'blue':
            lower = (100, 150, 0)
            upper = (140, 255, 255)
        elif self.color == 'red':
            lower1 = (0, 120, 70)
            upper1 = (10, 255, 255)
            lower2 = (170, 120, 70)
            upper2 = (180, 255, 255)

        if self.color == 'red':
            mask1 = cv2.inRange(hsv, lower1, upper1)
            mask2 = cv2.inRange(hsv, lower2, upper2)
            mask = mask1 + mask2
        else:
            mask = cv2.inRange(hsv, lower, upper)

        # Find contours
        _, contours, _  = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)
            if M["m00"] != 0:
                cx = int(M["m10"]/M["m00"])
                width = cv_image.shape[1]
                azimuth = (cx - width/2) * (90.0 / width)  # example FOV: 90 deg
                rospy.loginfo(f"Detected {self.color} azimuth: {azimuth}")
                self.pub.publish(azimuth)

if __name__ == '__main__':
    rospy.init_node('color_detector_node')
    color = rospy.get_param('~color', 'blue')
    ColorDetector(color)
    rospy.spin()