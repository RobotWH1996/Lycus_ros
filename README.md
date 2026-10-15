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
cd /home/victor/wh/Lycus_ros
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