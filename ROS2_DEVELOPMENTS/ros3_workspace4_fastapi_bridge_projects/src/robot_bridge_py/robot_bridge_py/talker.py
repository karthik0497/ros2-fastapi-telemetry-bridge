import rclpy
from rclpy.node import Node

# Import all constants (including MESSAGE_TYPE)
from robot_bridge_py.constants import *

class MinimalPublisher(Node):
    def __init__(self):
        # Use constant node name
        super().__init__(PUBLISHER_NODE_NAME)
        
        # Use constant message type, topic name, and queue size
        self.publisher_ = self.create_publisher(MESSAGE_TYPE, CHATTER_TOPIC, QUEUE_SIZE)
        self.timer = self.create_timer(TIMER_PERIOD, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        # Create message instance of the imported MESSAGE_TYPE class
        msg = MESSAGE_TYPE()
        msg.data = PAYLOAD_FORMAT.format(self.i)
        
        self.publisher_.publish(msg)
        self.get_logger().info(LOG_PUBLISH_FORMAT.format(msg.data))
        self.i += 1

def main(args=None):
    rclpy.init(args=args)
    minimal_publisher = MinimalPublisher()
    rclpy.spin(minimal_publisher)
    minimal_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
