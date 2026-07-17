import rclpy
from rclpy.node import Node

# Import all constants
from robot_bridge_py.constants import *

class MinimalSubscriber(Node):
    def __init__(self):
        # Use constant node name
        super().__init__(SUBSCRIBER_NODE_NAME)
        
        # Use constant message type, topic name, callback, and queue size
        self.subscription = self.create_subscription(
            MESSAGE_TYPE,
            CHATTER_TOPIC,
            self.listener_callback,
            QUEUE_SIZE
        )
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info(LOG_HEARD_FORMAT.format(msg.data))

def main(args=None):
    rclpy.init(args=args)
    minimal_subscriber = MinimalSubscriber()
    rclpy.spin(minimal_subscriber)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
