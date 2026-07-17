#include <chrono>
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

// Include the constants file
#include "constants.hpp"

using namespace std::chrono_literals;

class MinimalPublisher : public rclcpp::Node {
public:
  MinimalPublisher()
  : Node(robot_bridge_cpp::constants::PUBLISHER_NODE_NAME), count_(0) {
    
    // Create publisher using constants
    publisher_ = this->create_publisher<std_msgs::msg::String>(
      robot_bridge_cpp::constants::CHATTER_TOPIC,
      robot_bridge_cpp::constants::QUEUE_SIZE
    );
    
    // Create wall timer using constants
    timer_ = this->create_wall_timer(
      std::chrono::duration<double>(robot_bridge_cpp::constants::TIMER_PERIOD_SEC),
      std::bind(&MinimalPublisher::timer_callback, this)
    );
    
    RCLCPP_INFO(this->get_logger(), "🤖 C++ Simulated Robot Publisher Node Started");
  }

private:
  void timer_callback() {
    auto message = std_msgs::msg::String();
    message.data = "Hello World from C++: " + std::to_string(count_++);
    
    RCLCPP_INFO(this->get_logger(), "Publishing: '%s'", message.data.c_str());
    publisher_->publish(message);
  }

  rclcpp::TimerBase::SharedPtr timer_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
  size_t count_;
};

int main(int argc, char * argv[]) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<MinimalPublisher>());
  rclcpp::shutdown();
  return 0;
}
