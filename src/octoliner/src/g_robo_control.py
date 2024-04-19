#!/usr/bin/env python3

# Import necessary libraries
import time
import rospy
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
from std_msgs.msg import String
from std_msgs.msg import Float32
from nav_msgs.msg import Odometry
from turtlebot3_msgs.msg import Sound
from turtlebot3_msgs.msg import SensorState
from octoliner import Octoliner
import math

# Define a class for controlling the robot
class RobotController:
    def __init__(self):
        # Initialize ROS node
        rospy.init_node('rotate_robot')
        
        # Publishers for controlling the robot
        self.pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)
        self.pub_color = rospy.Publisher('/color', String, queue_size=10)
        self.pub_servo = rospy.Publisher('/servo_angle', Float32, queue_size=10)
        self.pub_sound = rospy.Publisher('/sound', Sound, queue_size=10)
        
        # Subscriber for reading encoder values
        self.sub_encoders = rospy.Subscriber('/sensor_state', SensorState, self.callback_encoders)
        self.sub_plant = rospy.Subscriber("/plant_result", String, self.callback_plant)
        self.sub_aruco = rospy.Subscriber("/last_aruco", String, self.callback_aruco)

        self.plant_result = "None"
        self.aruco_result = "None"

        self.left_encoder = 0
        self.right_encoder = 0
        
        # Initialize Octoliner for line tracking
        self.octoliner = Octoliner()
        self.octoliner.set_sensitivity(0.8)
        
        # Initialize Twist command
        self.command = Twist()

    # Callback function for encoder values
    def callback_encoders(self, msg):
        self.left_encoder = msg.left_encoder
        self.right_encoder = msg.right_encoder

    # Callback function for encoder values
    def callback_plant(self, msg):
        self.plant_result = msg.data

    def callback_aruco(self, msg):

        self.aruco_result = msg.data
        print(self.aruco_result)

    # Line tracking function using Octoliner
    def octoliner_line_tracking(self):
        values = [self.octoliner.analog_read(i) for i in range(8)]
        k_right = values[0] * 0.6 + values[1] * 0.48 + values[2] * 0.3 + values[3] * 0.12
        k_left = values[7] * 0.6 + values[6] * 0.48 + values[5] * 0.3 + values[4] * 0.12
        k_rotate = k_right - k_left
        return k_rotate

    # Function to move the robot by a specified number of degrees
    def move_degrees(self, degrees):
        start_left_encoder = self.left_encoder
        start_right_encoder = self.right_encoder
        self.pub_color.publish("0")

        while ((self.left_encoder - start_left_encoder) < degrees and (self.right_encoder - start_right_encoder) < degrees):
            # Move the robot forward
            self.command.angular.z = 0.0
            self.command.linear.x = 0.02
            self.pub.publish(self.command)
            time.sleep(0.01)
        
        # Stop the robot after reaching the desired rotation
        self.command.angular.z = 0.0
        self.command.linear.x = 0.0
        self.pub.publish(self.command)
        self.pub_color.publish("l")
        time.sleep(2)

    # Main function to control the robot's behavior
    def run(self):
        r = rospy.Rate(10)

        while not rospy.is_shutdown():
            self.pub_color.publish(self.aruco_result)
            # while not self.aruco_result == '10':

            # Calculate the total value of the line detected by Octoliner
            value_line = sum(self.octoliner.analog_read(i) for i in range(7, -1, -1))
            print(value_line)
            if value_line >= 4.7:
                # If the line is detected, stop the robot and perform specific actions
                self.command.angular.z = 0.0
                self.command.linear.x = 0.00
                self.pub.publish(self.command)

                # self.pub_color.publish("5")
                time.sleep(2)
                self.pub_color.publish("l")

                # Move the robot by a specified number of degrees
                self.move_degrees(800)
                print("WAIT")
                time.sleep(4)

                print(self.plant_result)
                if self.plant_result == "Tomato":
                    print("ITS TOMATO!!!!!!!!!!!!!!!!!!!!")
                    self.pub_servo.publish(0)
                    time.sleep(4)
                    self.pub_servo.publish(180)
                    time.sleep(2)
                    self.pub_servo.publish(180)
                    

            else:
                # If no line is detected, continue line tracking
                self.pub_color.publish("l")
                self.command.linear.x = 0.15
                self.command.angular.z = 1.07 * self.octoliner_line_tracking()

            self.pub.publish(self.command)
            r.sleep()
        
        print("ITS TIME TO STOP")

        self.command.angular.z = 0.0
        self.command.linear.x = 0.00
        self.pub.publish(self.command)

        self.pub_color.publish("g")            

        time.sleep(60)

# Entry point of the program
if __name__ == '__main__':
    controller = RobotController()
    # controller.run()

    print('- ')

    while not rospy.is_shutdown():
        controller.pub_color.publish("0")

        # controller.pub_servo.publish(0)
        # time.sleep(1)
        # controller.pub_color.publish("b")
        # controller.pub_servo.publish(180)
        # time.sleep(1)
