"""Passive robot viewer: consume measured joint states, publish robot TF only."""
from pathlib import Path
import tempfile

import yaml

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction, RegisterEventHandler
from launch.conditions import IfCondition
from launch.event_handlers import OnShutdown
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def _setup(context):
    urdf_path = Path(LaunchConfiguration('robot_urdf').perform(context)).expanduser().resolve()
    description = urdf_path.read_text()
    # Read geometry from this viewer's URDF. The planning description topic may
    # contain cuRobo-relative mesh paths that RViz cannot resolve.
    config = yaml.safe_load(Path(LaunchConfiguration('rviz_config').perform(context)).read_text())
    for display in config['Visualization Manager']['Displays']:
        if display.get('Class') == 'rviz_default_plugins/RobotModel':
            display['Description Source'] = 'File'
            display['Description File'] = str(urdf_path)
            display.pop('Description Topic', None)
    temporary = tempfile.TemporaryDirectory(prefix='lycus-view-')
    rviz_path = Path(temporary.name)/'view.rviz'
    rviz_path.write_text(yaml.safe_dump(config, sort_keys=False))

    def cleanup(context, *args, **kwargs):
        temporary.cleanup()
        return []

    return [
        RegisterEventHandler(OnShutdown(on_shutdown=[OpaqueFunction(function=cleanup)])),
        Node(
            package='robot_state_publisher', executable='robot_state_publisher',
            name='robot_state_publisher', output='screen',
            condition=IfCondition(LaunchConfiguration('publish_robot_tf')),
            parameters=[{'robot_description': ParameterValue(description, value_type=str),
                         'use_sim_time': ParameterValue(LaunchConfiguration('use_sim_time'), value_type=bool)}],
            remappings=[('joint_states', LaunchConfiguration('joint_states_topic'))],
        ),
        Node(
            package='rviz2', executable='rviz2', name='rviz2', output='screen',
            condition=IfCondition(LaunchConfiguration('use_rviz')),
            arguments=['-d', str(rviz_path)],
            parameters=[{'use_sim_time': ParameterValue(LaunchConfiguration('use_sim_time'), value_type=bool)}],
        ),
    ]


def generate_launch_description():
    share = Path(get_package_share_directory('lycus_description'))
    return LaunchDescription([
        DeclareLaunchArgument('joint_states_topic', default_value='/joint_states',
                              description='Measured joint states from the robot driver'),
        DeclareLaunchArgument('publish_robot_tf', default_value='true',
                              description='Disable if another robot_state_publisher already publishes robot TF'),
        DeclareLaunchArgument('use_rviz', default_value='true'),
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument('robot_urdf', default_value=str(share/'urdf/lycus.urdf')),
        DeclareLaunchArgument('rviz_config', default_value=str(share/'rviz/view.rviz')),
        OpaqueFunction(function=_setup),
    ])
