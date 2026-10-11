#!/usr/bin/env bash
# Stop all simulation processes (Gazebo, SITL, micro-ROS agent, RViz, bridges)
for p in "ros2 launch ardupilot_gz_bringup" "gz sim" "arducopter" "micro_ros_agent" \
         "rviz2" "robot_state_publisher" "parameter_bridge" "mavproxy" "fpv_lab2"; do
  pkill -f "$p" 2>/dev/null
done
sleep 2
echo "Simulation stopped"
