#ifndef ROBOT_BRIDGE_CPP__CONSTANTS_HPP_
#define ROBOT_BRIDGE_CPP__CONSTANTS_HPP_

#include <string>

namespace robot_bridge_cpp {
namespace constants {

// Topic and QoS
const std::string CHATTER_TOPIC = "chatter";
const int QUEUE_SIZE = 10;

// Node settings
const double TIMER_PERIOD_SEC = 1.0;
const std::string PUBLISHER_NODE_NAME = "minimal_publisher";
const std::string SUBSCRIBER_NODE_NAME = "minimal_subscriber";

} // namespace constants
} // namespace robot_bridge_cpp

#endif // ROBOT_BRIDGE_CPP__CONSTANTS_HPP_
