# CST8504 Assignment 2 – ROS 2 and Vision

ROS 2 Humble packages that let a turtlesim turtle (or an iRobot Create 3) follow your hand using a camera and MediaPipe.

## Packages

| Package | Node | Description |
|---|---|---|
| `aisd_msgs` | – | Custom `Hand` message (starter code) |
| `aisd_vision` | `image_publisher` | Reads camera frames and publishes them on `video_frames` |
| `aisd_vision` | `hands` | Detects the hand with MediaPipe and publishes `Hand` on `cmd_hand` |
| `aisd_motion` | `move` | Converts `Hand` messages into `Twist` commands on `cmd_vel` |

## Data flow

camera → image_publisher → /video_frames → hands → /cmd_hand → move → /cmd_vel → turtlesim / Create 3

## Build

```bash
cd ~/ros2_ws/src
git clone git@github.com:<user>/assignment-2-ros-2-and-vision-<name>.git
cd ~/ros2_ws
rosdep install -i --from-path src --rosdistro humble -y
pip install numpy==1.25.2
colcon build
```

## Run

Each command in its own terminal, after `source ~/ros2_ws/install/local_setup.bash`:

```bash
ros2 run turtlesim turtlesim_node --ros-args --remap /turtle1/cmd_vel:=cmd_vel
ros2 run aisd_vision image_publisher
ros2 run aisd_motion move
ros2 run aisd_vision hands
```

## Controls

- Index finger on the right of the image → turn right
- Index finger on the left of the image → turn left
- Index finger to the right of the pinky → move forward ("come")
- Otherwise → stop ("stay")
