cmake_minimum_required(VERSION 3.8)
project(robot_description)

find_package(ament_cmake REQUIRED)

# Install all resource folders so ROS2 can find them after build
install(
  DIRECTORY urdf launch rviz worlds config
  DESTINATION share/${PROJECT_NAME}
)

ament_package()