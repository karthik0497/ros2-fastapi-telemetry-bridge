from std_msgs.msg import String

# Message Type Class (No hardcoded class name in nodes)
MESSAGE_TYPE = String

# Node Names
PUBLISHER_NODE_NAME = 'minimal_publisher'
SUBSCRIBER_NODE_NAME = 'minimal_subscriber'

# Topic Names
CHATTER_TOPIC = 'chatter'

# ROS2 Quality of Service (QoS) Queue Size 
# Keep Last (Depth = 10): ROS 2 buffers the last 10 messages. If message #11 arrives, the oldest one is thrown away. (This is what QUEUE_SIZE = 10 sets).
# Reliable (Default): Ensures messages are delivered even if the network is temporarily unavailable.
QUEUE_SIZE = 10

# Timer Periods (in seconds)
TIMER_PERIOD = 1.0

# Logging & Payload Formats
PAYLOAD_FORMAT = 'Hello World from Python: {}'
LOG_PUBLISH_FORMAT = 'Publishing: "{}"'
LOG_HEARD_FORMAT = 'I heard: "{}"'
