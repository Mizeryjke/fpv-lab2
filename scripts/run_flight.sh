#!/usr/bin/env bash
# Run the flight node (takeoff -> hover -> fly to target -> land); log saved to logs/
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/ardu_env.sh"
source "$HOME/fpv_labs/install/setup.bash"

if ! ros2 topic list 2>/dev/null | grep -q "/ap/v1/status"; then
  echo "Simulation is not running. Start it first: scripts/start_sim.sh"
  exit 1
fi

mkdir -p "$HOME/fpv_labs/logs"
LOG="$HOME/fpv_labs/logs/flight_$(date +%Y%m%d_%H%M%S).log"
ros2 run fpv_lab2 flight_test 2>&1 | tee "$LOG"
echo "Log saved: $LOG"
