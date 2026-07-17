#!/usr/bin/env python3
"""
Drive pattern for AMR robot:
  Loop 2 times:
    1. Drive forward 20 metres
    2. U-turn (rotate 180 degrees)
    3. Drive backward 10 metres
    4. U-turn (rotate 180 degrees back to original heading)
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time


class DrivePattern(Node):

    def __init__(self):
        super().__init__('drive_pattern')
        
        # Publisher to /cmd_vel
        # This is the same topic the bridge forwards to Gazebo
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Robot physical values — must match your URDF
        self.linear_speed  = 0.3   # metres per second forward
        self.reverse_speed = 0.3   # metres per second backward
        self.turn_speed    = 0.5   # radians per second for U-turn

        self.get_logger().info('Drive pattern node started')

    def publish_velocity(self, linear_x, angular_z, duration_seconds):
        """
        Publish a constant velocity command for a fixed duration.
        
        linear_x  : forward speed in m/s (negative = backward)
        angular_z : turning speed in rad/s (positive = left turn)
        duration  : how long to apply this command in seconds
        """
        msg = Twist()
        msg.linear.x  = linear_x
        msg.angular.z = angular_z

        rate_hz = 10          # publish 10 times per second
        interval = 1.0 / rate_hz
        iterations = int(duration_seconds * rate_hz)

        self.get_logger().info(
            f'  linear={linear_x} angular={angular_z} '
            f'for {duration_seconds:.1f}s'
        )

        for _ in range(iterations):
            self.publisher.publish(msg)
            time.sleep(interval)

    def stop(self, duration=0.5):
        """
        Send zero velocity to stop the robot.
        Always stop between manoeuvres to prevent drift.
        """
        self.get_logger().info('  STOP')
        self.publish_velocity(0.0, 0.0, duration)

    def drive_forward(self, distance_metres):
        """
        Drive forward a given distance.
        time = distance / speed
        """
        duration = distance_metres / self.linear_speed
        self.get_logger().info(f'>>> FORWARD {distance_metres}m '
                               f'({duration:.1f}s)')
        self.publish_velocity(self.linear_speed, 0.0, duration)
        self.stop()

    def drive_backward(self, distance_metres):
        """
        Drive backward a given distance.
        linear.x is negative for reverse.
        """
        duration = distance_metres / self.reverse_speed
        self.get_logger().info(f'>>> BACKWARD {distance_metres}m '
                               f'({duration:.1f}s)')
        self.publish_velocity(-self.reverse_speed, 0.0, duration)
        self.stop()

    def uturn(self):
        """
        Rotate 180 degrees in place.
        
        180 degrees = PI radians = 3.14159 radians
        time = angle / angular_speed
             = 3.14159 / 0.5 = 6.28 seconds
        
        Positive angular.z = counter-clockwise (left turn).
        """
        import math
        angle_radians = math.pi          # 180 degrees
        duration = angle_radians / self.turn_speed
        self.get_logger().info(f'>>> U-TURN 180deg ({duration:.1f}s)')
        self.publish_velocity(0.0, self.turn_speed, duration)
        self.stop(1.0)                   # longer stop after turn to settle

    def run_pattern(self):
        """
        Execute the full drive pattern 2 times.
        """
        self.get_logger().info('=============================')
        self.get_logger().info(' Starting drive pattern')
        self.get_logger().info(' 2 loops of:')
        self.get_logger().info('   Forward 20m → U-turn')
        self.get_logger().info('   Backward 10m → U-turn')
        self.get_logger().info('=============================')

        # Wait 2 seconds at start so Gazebo is fully ready
        self.get_logger().info('Waiting 2s for Gazebo to be ready...')
        time.sleep(2.0)

        for loop in range(1, 3):        # loop 1 and loop 2
            self.get_logger().info('')
            self.get_logger().info(f'===== LOOP {loop} / 2 =====')

            # Step 1: Forward 20 metres
            self.drive_forward(20.0)

            # Step 2: U-turn (now facing original direction reversed)
            self.uturn()

            # Step 3: Backward 10 metres
            # After U-turn robot faces opposite direction.
            # Drive forward in that direction = physically going
            # back toward start. Using drive_backward keeps
            # linear.x negative which is correct here.
            self.drive_backward(10.0)

            # Step 4: U-turn back to original heading
            self.uturn()

            self.get_logger().info(f'===== LOOP {loop} COMPLETE =====')

        # Final stop
        self.stop(1.0)
        self.get_logger().info('')
        self.get_logger().info('Pattern complete.')


def main():
    rclpy.init()
    node = DrivePattern()

    try:
        node.run_pattern()
    except KeyboardInterrupt:
        node.get_logger().info('Interrupted by user')
    finally:
        # Always send stop on exit
        node.stop(0.5)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
