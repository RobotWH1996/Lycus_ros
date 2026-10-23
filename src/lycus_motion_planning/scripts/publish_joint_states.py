#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


class CustomJointStatePublisher(Node):
    def __init__(self):
        super().__init__("custom_joint_state_publisher")
        self.publisher_ = self.create_publisher(JointState, "joint_states", 10)
        self.timer = self.create_timer(0.02, self.timer_callback)
        self.joint_names = (
            [f"AR5-5_08L-W4C1C5-ZY2_joint_{i}" for i in range(1, 8)]
            + [f"AR5-5_08R-W4C1C5-ZY2_joint_{i}" for i in range(1, 8)]
            + [
                "Calf_joint",
                "Thigh_joint",
                "Waist_joint",
                "Chest_joint",
                "Neck_joint",
                "Head_joint",
                "Wheel1_joint",
                "Wheel2_joint",
                "Wheel3_joint",
                "Wheel4_joint",
                "left_gripper",
                "right_gripper",
            ]
        )
        self.joint_positions = [0.0] * len(self.joint_names)
        self.get_logger().info(f"Publishing joint_states for {len(self.joint_names)} joints")

    def timer_callback(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        msg.position = self.joint_positions
        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = CustomJointStatePublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
