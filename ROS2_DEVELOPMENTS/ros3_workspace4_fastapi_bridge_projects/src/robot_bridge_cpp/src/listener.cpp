#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

// Include the constants file
#include "constants.hpp"

class MinimalSubscriber : public rclcpp::Node {
public:
  MinimalSubscriber()
  : Node(robot_bridge_cpp::constants::SUBSCRIBER_NODE_NAME) {
    
    // Create subscription using constants
    subscription_ = this->create_subscription<std_msgs::msg::String>(
      robot_bridge_cpp::constants::CHATTER_TOPIC,
      robot_bridge_cpp::constants::QUEUE_SIZE,
      std::bind(&MinimalSubscriber::topic_callback, this, std::placeholders::_1)
    );
    
    RCLCPP_INFO(this->get_logger(), "🤖 C++ Subscriber Node Started");
  }

private:
  void topic_callback(const std_msgs::msg::String::SharedPtr msg) const {
    RCLCPP_INFO(this->get_logger(), "I heard: '%s'", msg->data.c_str());
  }

  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_;
};

int main(int argc, char * argv[]) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<MinimalSubscriber>());
  rclcpp::shutdown();
  return 0;
}
