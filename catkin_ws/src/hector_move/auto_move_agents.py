#!/usr/bin/env python

import rospy
import sys
from geometry_msgs.msg import Twist

def move(namespace):
    rospy.init_node('hector_auto_move_' + namespace.replace('/', ''), anonymous=True)
    pub = rospy.Publisher('/{}/cmd_vel'.format(namespace), Twist, queue_size=10)
    rate = rospy.Rate(10)  # 10 Hz

    twist = Twist()
    twist.linear.x = 0.1
    twist.angular.z = 0.05

    rospy.loginfo("[{}] Publishing motion command...".format(namespace))
    while not rospy.is_shutdown():
        pub.publish(twist)
        rate.sleep()

if __name__ == '__main__':
    try:
        if len(sys.argv) < 2:
            print("Usage: rosrun hector_move auto_move_agents.py <namespace>")
        else:
            move(sys.argv[1])
    except rospy.ROSInterruptException:
        pass
