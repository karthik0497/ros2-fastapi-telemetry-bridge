import os
import xacro

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


def generate_launch_description():

    # ─── Package paths ───────────────────────────────────────────
    #
    # We need two package paths:
    # 1. Our robot_description package — for the xacro file
    # 2. ros_gz_sim package — for the Gazebo launch file
    #
    pkg_robot = get_package_share_directory('robot_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # ─── Compile xacro → URDF string ────────────────────────────
    #
    # Same as display.launch.py — compile robot.xacro at launch time.
    # This string is passed to robot_state_publisher AND used to
    # spawn the robot into Gazebo.
    #
    xacro_file = os.path.join(pkg_robot, 'urdf', 'robot.xacro')
    robot_description = xacro.process_file(xacro_file).toxml()

    # ─── Launch Arguments ────────────────────────────────────────
    world_arg = DeclareLaunchArgument(
        name='world',
        default_value='empty',
        description='Gazebo world name'
    )

    # ─── Robot State Publisher ───────────────────────────────────
    #
    # use_sim_time: True — CRITICAL difference from display.launch.py.
    # When Gazebo runs, it publishes its own clock to /clock topic.
    # use_sim_time=True tells ALL nodes to use Gazebo clock instead
    # of system clock. Without this, TF timestamps mismatch Gazebo
    # time and transforms go stale — robot freezes in RViz.
    #
    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True,
        }]
    )

    # ─── Gazebo Sim ──────────────────────────────────────────────
    #
    # We include the standard Gazebo launch file from ros_gz_sim.
    # This starts the Gazebo Harmonic simulator.
    #
    # gz_args:
    #   -r = run immediately (do not pause on start)
    #   -v4 = verbosity level 4 (shows plugin loading messages)
    #   empty.sdf = the world file to load (empty world with ground plane)
    #
    # We do NOT start our own gz_sim process — we use the one
    # provided by ros_gz_sim which has proper ROS2 integration.
    #
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-r -v4 empty.sdf'}.items()
    )

    # ─── Spawn robot into Gazebo ─────────────────────────────────
    #
    # ros_gz_sim provides a create node that spawns a robot into Gazebo.
    # It reads the robot description from the /robot_description topic
    # (published by robot_state_publisher above) and creates the model
    # in the running Gazebo simulation.
    #
    # Arguments:
    #   -topic /robot_description  — read URDF from this ROS2 topic
    #   -entity amr_robot          — name of the model in Gazebo
    #   -x -y -z                   — spawn position in world frame
    #   -z 0.1 means 10cm above ground — prevents robot spawning
    #   inside the ground plane which causes physics explosions
    #
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        name='spawn_robot',
        output='screen',
        arguments=[
            '-topic', '/robot_description',
            '-entity', 'amr_robot',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.1',
            '-R', '0.0',
            '-P', '0.0',
            '-Y', '0.0',
        ]
    )

    # ─── ROS GZ Bridge ───────────────────────────────────────────
    #
    # This is the most important node for ROS2 ↔ Gazebo communication.
    #
    # Gazebo and ROS2 are two separate systems with different
    # middleware (Gazebo uses gz-transport, ROS2 uses DDS).
    # They cannot talk to each other directly.
    # ros_gz_bridge is the translator between them.
    #
    # Each entry in the config list is one bridge:
    # format: gz_topic_name@ros2_msg_type[gz_msg_type
    #   [ = data flows FROM Gazebo TO ROS2
    #   ] = data flows FROM ROS2 TO Gazebo
    #   @ = bidirectional
    #
    # Bridges we need:
    # 1. /clock          — Gazebo simulation time → ROS2
    #                      All ROS2 nodes need this for use_sim_time
    # 2. /cmd_vel        — ROS2 → Gazebo
    #                      Your velocity commands drive the robot
    # 3. /odom           — Gazebo → ROS2
    #                      Odometry from diff_drive plugin
    # 4. /tf             — Gazebo → ROS2
    #                      Transforms from diff_drive plugin (odom→base_footprint)
    # 5. /joint_states   — Gazebo → ROS2
    #                      Wheel joint angles → robot_state_publisher
    #
    # Path to bridge config file
    bridge_config = os.path.join(pkg_robot, 'config', 'ros_gz_bridge.yaml')

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge',
        output='screen',
        parameters=[{
            'config_file': bridge_config,
            'use_sim_time': True,
        }]
    )

    return LaunchDescription([
        world_arg,
        rsp_node,
        gazebo,
        spawn_robot,
        bridge,
    ])
