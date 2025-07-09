#!/usr/bin/env python

import time
import rospy
from geometry_msgs.msg import TwistStamped
import random

class SquarePath:
    def __init__(self):
        rospy.init_node("square_motion1")

        self.cmd_pub = rospy.Publisher("/uav1/command/twist", TwistStamped, queue_size=1)

        self.state = "forward"
        self.last_switch = time.time()

        self.forward_duration = 8.0   
        self.turn_duration = 2.0     

        self.run()

    def run(self):
        rate = rospy.Rate(10)  # 10Hz

        while not rospy.is_shutdown():
            twist_msg = TwistStamped()
            twist_msg.header.stamp = rospy.Time.now()
            twist_msg.header.frame_id = "base_stabilized"

            now = time.time()
            elapsed = now - self.last_switch

            if self.state == "forward" and elapsed > self.forward_duration:
                self.state = "turn"
                self.last_switch = now
                rospy.loginfo("Switching to TURN")

            elif self.state == "turn" and elapsed > self.turn_duration:
                self.state = "forward"
                self.last_switch = now
                rospy.loginfo("Switching to FORWARD")

            if self.state == "forward":
                twist_msg.twist.linear.x = 0.1
                twist_msg.twist.angular.z = 0.15  
                rospy.loginfo("Moving forward")

            elif self.state == "turn":
                twist_msg.twist.linear.x = 0.1
                twist_msg.twist.angular.z = 0.15 
                rospy.loginfo("Turning 90 degrees left")

            self.cmd_pub.publish(twist_msg)
            rate.sleep()

if __name__ == '__main__':
    try:
        SquarePath()
    except rospy.ROSInterruptException:
        pass
