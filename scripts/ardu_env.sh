export GZ_VERSION=garden
source /opt/ros/humble/setup.bash
source $HOME/ardu_ws/install/setup.bash
export SDF_PATH=$SDF_PATH:$HOME/ardu_ws/install/ardupilot_gazebo/share:$HOME/ardu_ws/install/ardupilot_gz_description/share
export GZ_SIM_RESOURCE_PATH=$GZ_SIM_RESOURCE_PATH:$HOME/ardu_ws/install/ardupilot_gazebo/share:$HOME/ardu_ws/install/ardupilot_gz_description/share
