"""Mock SDK endpoint: body/jaw controllers plus one unified joint-state source."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder


def generate_launch_description():
    config = MoveItConfigsBuilder(
        "lycus", package_name="lycus_moveit_config"
    ).to_moveit_configs()
    return LaunchDescription([
        DeclareLaunchArgument(
            "publish_tf", default_value="true",
            description="Publish model TF from /joint_states; no RViz is started.",
        ),
        Node(
            package="controller_manager", executable="ros2_control_node",
            parameters=[config.robot_description,
                        str(config.package_path / "config/ros2_controllers.yaml")],
            output="screen",
        ),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(
            str(config.package_path / "launch/spawn_controllers.launch.py")
        )),
        Node(
            package="robot_state_publisher", executable="robot_state_publisher",
            parameters=[config.robot_description],
            condition=IfCondition(LaunchConfiguration("publish_tf")),
            output="screen",
        ),
    ])
