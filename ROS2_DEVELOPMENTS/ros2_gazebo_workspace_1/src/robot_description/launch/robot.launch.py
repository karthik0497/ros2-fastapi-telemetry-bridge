import os
import xacro

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():

    # ─── Package path ────────────────────────────────────────────
    pkg = get_package_share_directory('robot_description')

    # ─── Include display.launch.py ───────────────────────────────
    #
    # Instead of rewriting robot_state_publisher and RViz nodes,
    # we include the launch file we already wrote.
    # IncludeLaunchDescription pulls another launch file in.
    # This is the ROS2 way of reusing launch files — like calling
    # a function instead of copying code.
    #
    display_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg, 'launch', 'display.launch.py')
        ),
        launch_arguments={
            'use_rsp': 'false',
        }.items()
    )

    # ─── Include gazebo.launch.py ────────────────────────────────
    #
    # This starts Gazebo, spawns the robot, and starts the bridge.
    # We wrap it in a TimerAction with a small delay.
    #
    # WHY the delay?
    # robot_state_publisher must publish /robot_description BEFORE
    # the spawn node tries to read it. If both start at exactly the
    # same time, spawn_robot sometimes starts before /robot_description
    # is available and fails silently — robot never appears in Gazebo.
    # A 2 second delay gives robot_state_publisher time to start up.
    #
    gazebo_launch = TimerAction(
        period=2.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(pkg, 'launch', 'gazebo.launch.py')
                )
            )
        ]
    )

    return LaunchDescription([
        display_launch,
        gazebo_launch,
    ])
