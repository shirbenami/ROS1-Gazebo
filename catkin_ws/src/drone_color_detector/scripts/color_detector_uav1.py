#!/usr/bin/env python
import rospy
from sensor_msgs.msg import Image
from std_msgs.msg import Float32
import cv2
from cv_bridge import CvBridge

class ColorDetector:
    def __init__(self, color):
        self.bridge = CvBridge()
        self.color = color  # 'red'
        self.pub = rospy.Publisher('/uav1/detected_drone_azimuth', Float32, queue_size=10)
        rospy.Subscriber('/uav1/front_cam/camera/image', Image, self.image_callback)

    def image_callback(self, msg):
        rospy.loginfo("Received image")
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)

        lower1 = (0, 120, 70)
        upper1 = (10, 255, 255)
        lower2 = (170, 120, 70)
        upper2 = (180, 255, 255)
        mask1 = cv2.inRange(hsv, lower1, upper1)
        mask2 = cv2.inRange(hsv, lower2, upper2)
        mask = mask1 + mask2
        #cv2.imshow("Mask", mask)
        #cv2.waitKey(1)

        _, contours, _  = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        rospy.loginfo("Contours found: {}".format(len(contours)))

        if contours:
            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)
            if M["m00"] != 0:
                cx = int(M["m10"]/M["m00"])
                width = cv_image.shape[1]
                azimuth = (cx - width/2) * (90.0 / width)
                rospy.loginfo("Detected {} azimuth: {}".format(self.color, azimuth))
                self.pub.publish(azimuth)

if __name__ == '__main__':
    rospy.init_node('color_detector_uav1')
    ColorDetector('red')
    rospy.spin()