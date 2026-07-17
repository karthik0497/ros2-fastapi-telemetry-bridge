#!/usr/bin/env python3
"""
AMR Interactive Control Menu
ROS2 Jazzy + Gazebo Harmonic
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time
import math
import sys


class AMRController(Node):

    def __init__(self):
        super().__init__('amr_menu_controller')

        # Publisher to /cmd_vel
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)

        # Default speeds — user can change via menu
        self.linear_speed  = 0.30   # m/s
        self.angular_speed = 0.50   # rad/s

        self.get_logger().info('AMR Controller ready')

    # ─── Core velocity publisher ─────────────────────────────────

    def publish_velocity(self, linear_x, angular_z, duration):
        """
        Publish velocity for a fixed duration at 10Hz.
        linear_x  : forward(+) or backward(-) in m/s
        angular_z : left(+) or right(-) in rad/s
        duration  : seconds to run
        """
        msg      = Twist()
        msg.linear.x  = linear_x
        msg.angular.z = angular_z

        rate      = 10
        interval  = 1.0 / rate
        steps     = int(duration * rate)

        for _ in range(steps):
            self.publisher.publish(msg)
            time.sleep(interval)

    def stop(self, duration=0.5):
        """Send zero velocity to stop robot."""
        msg = Twist()
        self.publisher.publish(msg)
        time.sleep(duration)

    # ─── Motion functions ────────────────────────────────────────

    def move_forward(self, distance):
        """Drive forward a given distance in metres."""
        duration = distance / self.linear_speed
        print(f'\n  Moving forward {distance}m at {self.linear_speed}m/s...')
        self.publish_velocity(self.linear_speed, 0.0, duration)
        self.stop()
        print('  Done.')

    def move_backward(self, distance):
        """Drive backward a given distance in metres."""
        duration = distance / self.linear_speed
        print(f'\n  Moving backward {distance}m at {self.linear_speed}m/s...')
        self.publish_velocity(-self.linear_speed, 0.0, duration)
        self.stop()
        print('  Done.')

    def rotate(self, degrees, direction):
        """
        Rotate by given degrees.
        direction: +1 = left (counter-clockwise)
                   -1 = right (clockwise)
        """
        radians  = math.radians(degrees)
        duration = radians / self.angular_speed
        label    = 'Left' if direction == 1 else 'Right'
        print(f'\n  Turning {label} {degrees}° at {self.angular_speed}rad/s...')
        self.publish_velocity(0.0, direction * self.angular_speed, duration)
        self.stop(1.0)
        print('  Done.')

    def rotate_left(self, degrees=90):
        self.rotate(degrees, direction=1)

    def rotate_right(self, degrees=90):
        self.rotate(degrees, direction=-1)

    # ─── Speed setters ───────────────────────────────────────────

    def set_linear_speed(self, speed):
        self.linear_speed = speed
        print(f'\n  Linear speed updated to {speed} m/s')

    def set_angular_speed(self, speed):
        self.angular_speed = speed
        print(f'\n  Angular speed updated to {speed} rad/s')


# ─── Helper — safe float input ───────────────────────────────────

def get_float(prompt, min_val=0.01, max_val=100.0):
    """Ask user for a float value with basic validation."""
    while True:
        try:
            val = float(input(f'  {prompt}: '))
            if val < min_val or val > max_val:
                print(f'  Enter a value between {min_val} and {max_val}')
                continue
            return val
        except ValueError:
            print('  Invalid input. Enter a number.')


# ─── Menu ────────────────────────────────────────────────────────

def print_menu(controller):
    print()
    print('  ===============================')
    print('          AMR CONTROL MENU       ')
    print('  ===============================')
    print(f'  Linear Speed  : {controller.linear_speed:.2f} m/s')
    print(f'  Angular Speed : {controller.angular_speed:.2f} rad/s')
    print('  ───────────────────────────────')
    print('  1. Move Forward')
    print('  2. Move Backward')
    print('  3. Turn Left  90°')
    print('  4. Turn Right 90°')
    print('  5. Turn 180°')
    print('  6. Turn 360°')
    print('  7. Change Linear Speed')
    print('  8. Change Angular Speed')
    print('  9. Stop Robot')
    print('  0. Exit')
    print('  ───────────────────────────────')


def menu(controller):
    print('\n  AMR Menu started. Make sure Gazebo is running.')

    while True:
        print_menu(controller)

        choice = input('  Select option: ').strip()

        if choice == '1':
            dist = get_float('Enter distance (metres)', 0.1, 50.0)
            controller.move_forward(dist)

        elif choice == '2':
            dist = get_float('Enter distance (metres)', 0.1, 50.0)
            controller.move_backward(dist)

        elif choice == '3':
            controller.rotate_left(90)

        elif choice == '4':
            controller.rotate_right(90)

        elif choice == '5':
            controller.rotate(180, direction=1)

        elif choice == '6':
            controller.rotate(360, direction=1)

        elif choice == '7':
            print(f'  Current linear speed : {controller.linear_speed:.2f} m/s')
            speed = get_float('Enter new linear speed (m/s)', 0.01, 2.0)
            controller.set_linear_speed(speed)

        elif choice == '8':
            print(f'  Current angular speed: {controller.angular_speed:.2f} rad/s')
            speed = get_float('Enter new angular speed (rad/s)', 0.01, 3.0)
            controller.set_angular_speed(speed)

        elif choice == '9':
            print('\n  Stopping robot...')
            controller.stop(1.0)
            print('  Stopped.')

        elif choice == '0':
            print('\n  Stopping robot and exiting...')
            controller.stop(1.0)
            print('  Goodbye.')
            break

        else:
            print('\n  Invalid option. Choose 0-9.')


# ─── Main ────────────────────────────────────────────────────────

def main():
    rclpy.init()
    controller = AMRController()

    try:
        menu(controller)
    except KeyboardInterrupt:
        print('\n  Interrupted.')
        controller.stop()
    finally:
        controller.destroy_node()
        rclpy.shutdown()
        sys.exit(0)


if __name__ == '__main__':
    main()
