import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/karthik/Documents/ROS2_DEVELOPMENTS/ros3_workspace4_fastapi_bridge_projects/install/robot_bridge_py'
