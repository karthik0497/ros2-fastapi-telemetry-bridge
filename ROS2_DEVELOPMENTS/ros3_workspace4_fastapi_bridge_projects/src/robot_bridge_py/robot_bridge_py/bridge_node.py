import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32
from datetime import datetime
from robot_bridge_py.robot_data import robot_data

class BridgeNode(Node):
    def __init__(self):
        super().__init__('bridge_node')
        
        # Subscriptions to telemetry topics
        self.status_sub = self.create_subscription(
            String,
            '/robot/status',
            self.status_callback,
            10
        )
        self.battery_sub = self.create_subscription(
            Float32,
            '/robot/battery',
            self.battery_callback,
            10
        )
        self.speed_sub = self.create_subscription(
            Float32,
            '/robot/speed',
            self.speed_callback,
            10
        )
        self.position_sub = self.create_subscription(
            String,
            '/robot/position',
            self.position_callback,
            10
        )
        
        # Publisher for sending commands back to the robot
        self.command_pub = self.create_publisher(
            String,
            '/robot/command',
            10
        )
        
        self.get_logger().info('🤖 ROS2 Bridge Node Started - Listening to telemetry...')

    def _update_metadata(self):
        robot_data['update_count'] += 1
        robot_data['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def status_callback(self, msg):
        robot_data['status'] = msg.data
        self._update_metadata()
        self.get_logger().debug(f"Telemetry Status: {msg.data}")

    def battery_callback(self, msg):
        robot_data['battery'] = round(msg.data, 2)
        self._update_metadata()
        self.get_logger().debug(f"Telemetry Battery: {msg.data}")

    def speed_callback(self, msg):
        robot_data['speed'] = round(msg.data, 2)
        self._update_metadata()
        self.get_logger().debug(f"Telemetry Speed: {msg.data}")

    def position_callback(self, msg):
        robot_data['position'] = msg.data
        self._update_metadata()
        self.get_logger().debug(f"Telemetry Position: {msg.data}")

    def publish_command(self, command: str):
        msg = String()
        msg.data = command
        self.command_pub.publish(msg)
        self.get_logger().info(f"📤 Published command '{command}' to /robot/command")


def main(args=None):
    rclpy.init(args=args)
    node = BridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
