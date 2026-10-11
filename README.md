# Lab 2: ArduPilot SITL + Gazebo + ROS 2, variant 34

Flight to target (x0 - 4.0, y0 - 1.1) and automatic landing.

- `src/fpv_lab2` - ROS 2 Python package (`ros2 run fpv_lab2 flight_test`)
- `scripts/ardu_env.sh` - environment variables (SDF_PATH, GZ_SIM_RESOURCE_PATH)
- `tools/maze_check.py` - checks free path / walls in maze.sdf
- `logs/` - flight logs

Run: `source scripts/ardu_env.sh && source install/setup.bash && ros2 run fpv_lab2 flight_test`

## Quick start (scripts)

scripts/start_sim.sh # Gazebo + ArduPilot SITL + ROS 2 (waits until ready)
scripts/run_flight.sh # takeoff, hover, flight to target, landing; log in logs/
scripts/stop_sim.sh # stop all simulation processes


## Quick start (scripts)

scripts/start_sim.sh # Gazebo + ArduPilot SITL + ROS 2 (waits until ready)
scripts/run_flight.sh # takeoff, hover, flight to target, landing; log in logs/
scripts/stop_sim.sh # stop all simulation processes

