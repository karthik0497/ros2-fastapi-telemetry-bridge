mkdir -p src && cd src
ros2 pkg create --build-type ament_python robot_bridge_py --dependencies rclpy std_msgs
ros2 pkg create --build-type ament_cmake robot_bridge_cpp --dependencies rclcpp std_msgs


cd ~/Documents/ROS2_DEVELOPMENTS/ros3_workspace4_fastapi_bridge_projects
colcon build --packages-select robot_bridge_py
colcon build --packages-select robot_bridge_cpp


 source install/setup.bash





 cd ~/Documents/ROS2_DEVELOPMENTS/ros3_workspace4_fastapi_bridge_projects
colcon build --packages-select robot_bridge_cpp