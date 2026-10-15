from launch import LaunchDescription
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder


def generate_launch_description():
    moveit_config = MoveItConfigsBuilder(
        robot_name="lycus",
        package_name="lycus_moveit_config",
    ).to_moveit_configs()
    return LaunchDescription(
        [
            Node(
                package="lycus_motion_planning",
                executable="lycus_motion_planning_node",
                name="lycus_motion_planning_node",
                output="screen",
                parameters=[
                    moveit_config.robot_description,
                    moveit_config.robot_description_semantic,
                    moveit_config.robot_description_kinematics,
                    moveit_config.joint_limits,
                ],
            )
        ]
    )
