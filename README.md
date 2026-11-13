# Lycus ROS 2

## 包

| 包 | 作用 |
|---|---|
| `lycus_description` | URDF 与 mesh |
| `lycus_moveit_config` | MoveIt 2、ros2_control 控制器 |
| `lycus_motion_planning` | `/plan_joint_goal` `/plan_pose_goal` `/compute_ik` `/play_rosbag` |

规划组：`left_arm`、`right_arm`、`both_arms`、`torso`、`head`。规划服务目前只接前三个。末端：`left_arm_ee_link` / `right_arm_ee_link`。参考系：`base_link`。

单臂 7 关节，顺序 `joint_1` … `joint_7`。`both_arms` 共 14 个数：左臂 7 个 + 右臂 7 个。默认 home 约为 `[0, 1.57, 0, 1.57, 0, 0, 0]`。

## 编译

```bash
source /opt/ros/humble/setup.zsh
cd /home/ai/wh/Lycus_ros
colcon build --symlink-install
source install/setup.zsh
```

## 启动

先起 MoveIt + mock 控制器：

```bash
ros2 launch lycus_moveit_config demo.launch.py
```

不需要 RViz：

```bash
ros2 launch lycus_moveit_config demo.launch.py use_rviz:=false
```

再起规划节点：

```bash
ros2 launch lycus_motion_planning lycus_motion_planning.launch.py
```

只看模型、拖关节滑条（不要和 demo 一起开）：

```bash
ros2 launch lycus_description display.launch.py
```

## 只显示真实机器人状态

```bash
ros2 launch lycus_description view.launch.py
```

只启动 `robot_state_publisher` 和 RViz，订阅真实 `/joint_states`，显示模型、TF 和网格；不启动关节状态发布器、mock 硬件、控制器或 MoveIt，不发布关节角及运动指令。没有驱动反馈时不会生成假关节角，活动连杆的 TF 可能不完整。RViz 使用 `base_link` 为固定坐标系。

如果 cuRobo deploy 或其他节点已经发布机器人 TF，使用：

```bash
ros2 launch lycus_description view.launch.py publish_robot_tf:=false
```

这时只启动 RViz，从本包安装的 URDF 文件加载模型，使用已有 `/tf`、`/tf_static`；不读取规划器 `/robot_description` 中的相对网格路径。已有 TF 发布者须使用相同机器人几何与关节名称。可用 `joint_states_topic:=/other/joint_states` 更换订阅 Topic；`use_rviz:=false` 只启动 TF 发布节点。更换模型可传 `robot_urdf:=/absolute/path/robot.urdf`。

## 服务调用

另开一个已经 `source install/setup.zsh` 的终端。

### 关节空间规划

相对 home 稍微抬一点肩/肘，左臂：

```bash
ros2 service call /plan_joint_goal lycus_motion_planning/srv/PlanJointGoal "{group_name: 'left_arm', joint_angles: [0.0, 1.2, 0.0, 0.0, 0.0, 0.0, 0.0]}"
```

右臂：

```bash
ros2 service call /plan_joint_goal lycus_motion_planning/srv/PlanJointGoal "{group_name: 'right_arm', joint_angles: [0.0, 1.2, 0.0, 1.57, 0.0, 0.0, 0.0]}"
```

双臂：

```bash
ros2 service call /plan_joint_goal lycus_motion_planning/srv/PlanJointGoal "{group_name: 'both_arms', joint_angles: [0.0, 1.2, 0.0, 1.57, 0.0, 0.0, 0.0, 0.0, 1.2, 0.0, 1.57, 0.0, 0.0, 0.0]}"
```

### 笛卡尔规划

`ee_link` 可留空（用该组默认末端）。把下面的位姿换成当前可达目标：

```bash
ros2 service call /plan_pose_goal lycus_motion_planning/srv/PlanPoseGoal "{group_name: 'left_arm', ee_link: 'left_arm_ee_link', pose: {header: {frame_id: 'base_link'}, pose: {position: {x: 0.3, y: 0.25, z: 0.8}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}}}"
```

### 逆解

```bash
ros2 service call /compute_ik lycus_motion_planning/srv/ComputeIK "{group_name: 'left_arm', pose: {header: {frame_id: 'base_link'}, pose: {position: {x: 0.3, y: 0.25, z: 0.8}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}}}"
```

### 回放 bag

```bash
ros2 service call /play_rosbag lycus_motion_planning/srv/PlayRosbag "{group_name: 'left_arm', file_path: '/path/to/your.db3', enable_time_parameterization: true}"
```

## 与 cuRobo / 实机统一的关节接口

本工程模拟本体与夹爪 SDK 的运动和反馈，不需要夹爪厂商协议。
cuRobo 只从 `/joint_states` 刷新本体与夹爪状态。完整任务轨迹包含手臂关节和
`left_gripper`、`right_gripper` 的位置；cuRobo debug 模式按阶段下发对应通用控制器，deploy 模式交给实机适配脚本。
不要把命令发布到 `/joint_states`：该话题只承载状态反馈。

### 无 MoveIt / RViz 的 SDK 仿真

```bash
source /opt/ros/humble/setup.bash
source /home/ai/wh/Lycus_ros/install/setup.bash
ros2 launch lycus_moveit_config sdk_sim.launch.py
```

该启动文件只启动 mock ros2_control、控制器和 robot_state_publisher，
不会启动 move_group 或 RViz。只需要关节反馈、无需 TF 时：

```bash
ros2 launch lycus_moveit_config sdk_sim.launch.py publish_tf:=false
```

与 curobo_ros_python 的 deploy 启动文件一起使用时，只保留一份模型 TF 发布：
可保留本入口的 TF，并给 deploy 传 publish_robot_tf:=false；
或将本入口设为 publish_tf:=false，让 deploy 发布模型 TF。

需要 MoveIt / RViz 时仍使用原来的 `demo.launch.py`；两种启动方式选一个，
它们使用同一套硬件描述、控制器配置和关节状态来源。实机不启动这两种 mock 启动文件，
由实机转接脚本输出同样的 `/joint_states` 即可。

### 命令接口与关节单位

| 对象 | Action | 类型 |
|---|---|---|
| 左臂 | `/left_arm_controller/follow_joint_trajectory` | `control_msgs/action/FollowJointTrajectory` |
| 右臂 | `/right_arm_controller/follow_joint_trajectory` | `control_msgs/action/FollowJointTrajectory` |
| 双臂 | `/both_arms_controller/follow_joint_trajectory` | `control_msgs/action/FollowJointTrajectory` |
| 左夹爪 | `/left_gripper_controller/follow_joint_trajectory` | `control_msgs/action/FollowJointTrajectory` |
| 右夹爪 | `/right_gripper_controller/follow_joint_trajectory` | `control_msgs/action/FollowJointTrajectory` |

双臂控制器默认 inactive，因为它与两个单臂控制器使用相同的关节。
沿用现有控制器切换方式，经 `/controller_manager/switch_controller` 切换后再执行。
夹爪使用独立控制器，不占用手臂控制器，也不增加手臂规划组的自由度。

夹爪位置是 URDF 滑动关节的米单位：`0.0` 全开、`-0.042` 全闭，范围 `[-0.042, 0]`。
FollowJointTrajectory 按 time_from_start 插补夹爪位置；这里不是归一化行程值。
mock position 硬件不模拟夹持力、物体接触或实机夹持检测。夹爪控制器只包含自己的实际关节，
不接收 mimic 关节，也不占用手臂控制器。

```bash
# 左夹爪闭合
ros2 action send_goal /left_gripper_controller/follow_joint_trajectory control_msgs/action/FollowJointTrajectory \
  "{trajectory: {joint_names: [left_gripper], points: [{positions: [-0.042], time_from_start: {sec: 1}}]}}"

# 右夹爪张开
ros2 action send_goal /right_gripper_controller/follow_joint_trajectory control_msgs/action/FollowJointTrajectory \
  "{trajectory: {joint_names: [right_gripper], points: [{positions: [0.0], time_from_start: {sec: 1}}]}}"
```

### 状态刷新与显示

`mock_components/GenericSystem` 接收位置命令并更新硬件状态，
`joint_state_broadcaster` 统一以控制器更新频率（当前 100 Hz）发布 `/joint_states`，
其中包括 24 个本体关节和两个实际夹爪关节。该仿真链路只有这一份状态发布者。
cuRobo 订阅同一份反馈刷新关节状态；需要显示时，
`/joint_states → robot_state_publisher → TF → RViz` 就会显示开合。

`left_gripper_mimic`、`right_gripper_mimic` 由 URDF mimic 关系计算，
不单独命令，也不重复发布到 `/joint_states`。不能同时启动关节滑条、另一份 mock 控制器，
或其他向同一个 `/joint_states` 写入这些关节的节点。
