import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from std_msgs.msg import Float32

import random


class RobotPublisher(Node):

    def __init__(self):
        super().__init__('robot_publisher')
        # Publisher for robot status
        self.status_pub = self.create_publisher(String, '/robot/status', 10)
        # Publisher for robot battery
        self.battery_pub = self.create_publisher(Float32, '/robot/battery', 10)
        # Publisher for robot speed
        self.speed_pub = self.create_publisher(Float32, '/robot/speed', 10)
        # Publisher for robot position
        self.position_pub = self.create_publisher(String, '/robot/position', 10)
        # Subscription for commands sent from FastAPI
        self.command_sub = self.create_subscription(
            String,
            '/robot/command',
            self.command_callback,
            10
        )
        # Timer -> runs every 1 second
        self.timer = self.create_timer(1.0, self.publish_robot_data)
        self.get_logger().info('Robot Publisher Started')

    def publish_robot_data(self):

        # -----------------------------
        # Fake Robot Data
        # -----------------------------

        battery = round(random.uniform(40.0, 100.0), 2)
        speed = round(random.uniform(0.0, 2.0), 2)
        x = round(random.uniform(0.0, 10.0), 2)
        y = round(random.uniform(0.0, 10.0), 2)
        status_options = ['IDLE','MOVING','CHARGING']
        status = random.choice(status_options)

        # -----------------------------
        # Create ROS Messages
        # -----------------------------

        battery_msg = Float32()
        battery_msg.data = battery
        speed_msg = Float32()
        speed_msg.data = speed
        status_msg = String()
        status_msg.data = status
        position_msg = String()
        position_msg.data = f'x:{x}, y:{y}'

        # -----------------------------
        # Publish Messages
        # -----------------------------

        self.battery_pub.publish(battery_msg)
        self.speed_pub.publish(speed_msg)
        self.status_pub.publish(status_msg)
        self.position_pub.publish(position_msg)

        # -----------------------------
        # Console Logs
        # -----------------------------
        self.get_logger().info(f'Battery: {battery}%,Speed: {speed} m/s,Status: {status},Position: x={x}, y={y}')

    def command_callback(self, msg):
        self.get_logger().info(f"🤖 RECEIVED COMMAND FROM FASTAPI: '{msg.data}'")
        


def main(args=None):
    rclpy.init(args=args)
    node = RobotPublisher()

    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()