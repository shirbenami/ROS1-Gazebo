#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import rospy
from geometry_msgs.msg import TwistStamped
import numpy as np
import random

class LissajousFigureEight:
    def __init__(self):
        rospy.init_node("lissajous_figure_eight")

        self.cmd_pub = rospy.Publisher("/uav0/command/twist", TwistStamped, queue_size=1)

        self.radius = 1.0 
        self.omega = 0.1    
        self.start_time = time.time()

        self.start_duration = 5.0  
        self.init_roll = 25.0        
        self.init_pitch = 45.0       
        self.init_z = 65.0     
        self.init_x= 85.0
        self.init_y = 105.0    
        self.init_all = 125.0


       # self.start_duration = 5.0  
       # self.init_roll = 10.0        
       # self.init_pitch = 15.0       
       # self.init_z = 20.0     
       # self.init_x= 25.0
       # self.init_y = 30.0    
        #self.init_all = 35.0

        self.run()

    def run(self):
        rate = rospy.Rate(20)

        while not rospy.is_shutdown():
            t = time.time() - self.start_time

            twist_msg = TwistStamped()
            twist_msg.header.stamp = rospy.Time.now()
            twist_msg.header.frame_id = "base_stabilized"

            if t < self.start_duration:
                twist_msg.twist.linear.x = 0.00
                twist_msg.twist.linear.y = 0.00
                twist_msg.twist.linear.z = 0.0
                twist_msg.twist.angular.x = 0.0
                twist_msg.twist.angular.y = 0.0
                twist_msg.twist.angular.z = 0.00
                rospy.loginfo("Phase: STOP (first 10 sec)")

            elif t < self.init_roll:
                twist_msg.twist.linear.x =  0.0
                twist_msg.twist.linear.y = 2.0 * np.sin(5.0 * t)
                twist_msg.twist.linear.z = 0.01
                twist_msg.twist.angular.x = 1.4 * np.sin(8.0 * t)
                twist_msg.twist.angular.y = 0.0
                twist_msg.twist.angular.z = 0.0
                rospy.loginfo("Phase: ROLL | angular.x={:.2f}".format(twist_msg.twist.angular.x))

            elif t < self.init_pitch:
                twist_msg.twist.linear.x = 2.0 * np.sin(4.0 * t)
                twist_msg.twist.linear.y =  0.0
                twist_msg.twist.linear.z = 0.0
                twist_msg.twist.angular.x = 0.0
                twist_msg.twist.angular.y =  1.4 * np.sin(9.0 * t)
                twist_msg.twist.angular.z =  0.0
                rospy.loginfo("Phase: PITCH | angular.y={:.2f}".format(twist_msg.twist.angular.y))

            elif t < self.init_z:
                twist_msg.twist.linear.x = 0.0
                twist_msg.twist.linear.y = 0.0
                twist_msg.twist.linear.z = 1.4 * np.sin(4.0 * t)
                twist_msg.twist.angular.x = 0.0
                twist_msg.twist.angular.y = 0.0
                twist_msg.twist.angular.z = 0.0
                rospy.loginfo("Phase: Z | linear.z={:.2f}".format(twist_msg.twist.linear.z))

            elif t < self.init_x:
                twist_msg.twist.linear.x = 0.6 * np.sin(1.9 * t)
                twist_msg.twist.linear.y = 0.0
                twist_msg.twist.linear.z = 0.0
                twist_msg.twist.angular.x = 0.0
                twist_msg.twist.angular.y = 0.0
                twist_msg.twist.angular.z = 0.0
                rospy.loginfo("Phase: x | linear.X={:.2f}".format(twist_msg.twist.linear.x))
            
            elif t < self.init_y:
                twist_msg.twist.linear.x =0.0
                twist_msg.twist.linear.y = 0.7 * np.sin(1.5 * t)
                twist_msg.twist.linear.z = 0.0
                twist_msg.twist.angular.x = 0.0
                twist_msg.twist.angular.y = 0.0
                twist_msg.twist.angular.z = 0.0
                rospy.loginfo("Phase: y | linear.y={:.2f}".format(twist_msg.twist.linear.y))


            elif t < self.init_all:
                twist_msg.twist.linear.x = 0.5 * np.sin(5.0 * t)
                twist_msg.twist.linear.y =  0.5 * np.sin(5.0 * t)
                twist_msg.twist.linear.z = 0.5 * np.sin(5.0 * t)
                twist_msg.twist.angular.x =  2.0 * np.sin(5.0 * t)
                twist_msg.twist.angular.y =  2.0 * np.sin(5.0 * t)
                twist_msg.twist.angular.z = 0.5 * np.sin(5.0 * t)
                rospy.loginfo("Phase: all ")

            else:
                t_adj = t - self.init_z

                dx = self.radius * self.omega * np.cos(self.omega * t_adj)
                dy = 4 * self.radius * self.omega * np.cos(2 * self.omega * t_adj)

                speed = np.hypot(dx, dy) + random.gauss(-0.04, 0.04)
                desired_heading = np.arctan2(dy, dx)

                twist_msg.twist.linear.x = speed  
                twist_msg.twist.linear.y = 0.0 
                twist_msg.twist.linear.z = 0.0

                twist_msg.twist.angular.x = 0.0
                twist_msg.twist.angular.y = 0.0
                twist_msg.twist.angular.z = 0.5 * np.sin(2 * self.omega * t_adj)

                rospy.loginfo("Phase: 8-Loop | speed={:.2f} heading={:.1f}".format(
                    speed, np.degrees(desired_heading)))

            self.cmd_pub.publish(twist_msg)
            rate.sleep()

if __name__ == '__main__':
    try:
        LissajousFigureEight()
    except rospy.ROSInterruptException:
        pass