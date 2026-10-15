#include <rclcpp/rclcpp.hpp>
#include "lycus_motion_planning/lycus_motion_planning.hpp"

int main(int argc, char** argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<lycus_motion_planning::LycusMotionPlanningNode>();
    
    if (node->initialize()) {
        rclcpp::executors::MultiThreadedExecutor executor;
        executor.add_node(node);
        executor.spin();
    }
    
    rclcpp::shutdown();
    return 0;
}
