import os
import xacro

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    # ─── Package path ───────────────────────────────────────────
    #
    # get_package_share_directory finds the installed package location.
    # This is the install/robot_description/share/robot_description/ folder.
    # We use this to build paths to our xacro and rviz files.
    #
    pkg = get_package_share_directory('robot_description')

    # ─── Process xacro file ─────────────────────────────────────
    #
    # xacro.process_file() compiles robot.xacro into plain URDF XML.
    # It returns an XML document object. .toxml() converts it to a string.
    # This string is what robot_state_publisher needs as its parameter.
    #
    # We do this at launch time, not at build time.
    # Every time you launch, the latest xacro files are compiled fresh.
    # This means edits to xacro files take effect on next launch
    # without rebuilding (because we used --symlink-install).
    #
    xacro_file = os.path.join(pkg, 'urdf', 'robot.xacro')
    robot_description = xacro.process_file(xacro_file).toxml()



    # Controls whether this launch file starts robot_state_publisher.
    # When called standalone: use_rsp=true (default) — starts RSP.
    # When called from robot.launch.py: gazebo.launch.py handles RSP.
    # So robot.launch.py passes use_rsp:=false to this file.
    use_rsp_arg = DeclareLaunchArgument(
        name='use_rsp',
        default_value='true',
        description='Start robot_state_publisher if true'
    )
    use_rsp = LaunchConfiguration('use_rsp')


    # ─── Launch argument for RViz config ────────────────────────
    #
    # DeclareLaunchArgument creates a launch argument that can be
    # overridden from the command line:
    #   ros2 launch robot_description display.launch.py use_rviz:=false
    #
    # LaunchConfiguration reads the value of that argument at runtime.
    #
    use_rviz_arg = DeclareLaunchArgument(
        name='use_rviz',
        default_value='true',
        description='Launch RViz if true'
    )
    use_rviz = LaunchConfiguration('use_rviz')

    # ─── Robot State Publisher node ─────────────────────────────
    #
    # robot_state_publisher does two things:
    # 1. Publishes /robot_description topic (the full URDF XML string)
    #    RViz reads this to know what shape to draw.
    # 2. Reads /joint_states topic (wheel angles) and publishes /tf
    #    /tf tells RViz where each link is in 3D space.
    #
    # Without robot_state_publisher:
    # - RViz cannot show the robot model
    # - No TF frames exist for any link
    # - Navigation cannot work
    #
    # parameters: robot_description is passed as a string parameter.
    # use_sim_time false here because we are not running Gazebo yet.
    # When we add Gazebo, this becomes true.
    #
    from launch.conditions import IfCondition
    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        condition=IfCondition(use_rsp),
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': False,
        }]
    )

    # ─── Joint State Publisher GUI node ─────────────────────────
    #
    # joint_state_publisher_gui opens a small window with sliders.
    # One slider per moving joint (left_wheel_joint, right_wheel_joint).
    # Moving a slider publishes to /joint_states.
    # robot_state_publisher reads /joint_states and updates /tf.
    # Result: you can rotate wheels manually in RViz to verify joints work.
    #
    # This node is only for testing. When Gazebo runs, Gazebo publishes
    # /joint_states via the JointStatePublisher plugin instead.
    # We will remove this node from the Gazebo launch file.
    #
    jsp_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen',
    )

    # ─── RViz2 node ─────────────────────────────────────────────
    #
    # rviz2 is the 3D visualizer.
    # We do not pass a config file yet — RViz opens with defaults.
    # You will add displays manually in this step to understand them.
    # In a later step we create a saved config file.
    #
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
    )

    return LaunchDescription([
        use_rsp_arg,
        use_rviz_arg,
        rsp_node,
        jsp_gui_node,
        rviz_node,
    ])
