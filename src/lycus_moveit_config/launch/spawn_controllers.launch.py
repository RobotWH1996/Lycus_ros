from launch import LaunchDescription
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder

# Claims the same joints as left_arm + right_arm. Load it inactive;
# lycus_motion_planning switches it on only when planning both_arms.
INACTIVE_CONTROLLERS = {"both_arms_controller"}


def generate_launch_description():
    moveit_config = MoveItConfigsBuilder("lycus", package_name="lycus_moveit_config").to_moveit_configs()
    controller_names = moveit_config.trajectory_execution.get(
        "moveit_simple_controller_manager", {}
    ).get("controller_names", [])
    ld = LaunchDescription()
    for controller in controller_names + ["joint_state_broadcaster"]:
        arguments = [controller]
        if controller in INACTIVE_CONTROLLERS:
            arguments.append("--inactive")
        ld.add_action(
            Node(
                package="controller_manager",
                executable="spawner",
                arguments=arguments,
                output="screen",
            )
        )
    return ld
