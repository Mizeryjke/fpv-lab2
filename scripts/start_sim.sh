#!/usr/bin/env bash
# Start Gazebo + ArduPilot SITL + ROS 2 bridge (iris in maze world)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG="$HOME/sim.log"

"$SCRIPT_DIR/stop_sim.sh" > /dev/null 2>&1
source "$SCRIPT_DIR/ardu_env.sh"

nohup ros2 launch ardupilot_gz_bringup iris_maze.launch.py > "$LOG" 2>&1 &
echo "Simulation starting (log: $LOG). Waiting for EKF/GPS (up to 2 min)..."

for i in $(seq 1 120); do
  if grep -q "is using GPS" "$LOG" 2>/dev/null; then
    sleep 5
    echo "Simulation ready"
    exit 0
  fi
  sleep 1
done
echo "Timeout: simulation did not become ready, see $LOG"
exit 1
