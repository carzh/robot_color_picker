# robot_color_picker

Command-line program that uses the Interbotix Perception module and an RX200 robot arm to match words to colors and direct the robot arm to point to the corresponding colored object.

## Run instructions

First, set up the environment. The camera should be facing downwards. The robot should be on the right side of the camera, facing forward. All colored objects or blocks should be clearly visible to the camera.

```
./roslaunch_script
```
Running the above command will launch the ROS GUI program. This does not initialize the camera, which is required for the `point_to_color_nlp.py` script.

```
./roslaunch_perception_script
```
Running the above command will launch the ROS GUI program with the perception module, which will have a camera view and fine-tuning options for using a RealSense camera with the robot arm. These settings will need to be [calibrated](https://www.youtube.com/watch?v=UesfMYM4qcc) for best results.

```
python point_to_color_nlp.py
```
To run the script that points to colors, run the `roslaunch_perception_script` first, then open up in another terminal and run the `point_to_color_nlp.py` script.

First, run the `armtag` command to have the robot move its armtag into view of the camera, which will allow the camera to calibrate itself with respect to the robot's position. After calibration, the user can type anything to run the program, maing the robot point to the color that the user has inputted. Type `quit` to exit the program.

## Requirements

Install the appropriate torch version and the relevant interbotix packages (specifically, [interbotix_xs](https://github.com/Interbotix/interbotix_ros_manipulators) and [the interbotix library for perception](https://github.com/Interbotix/interbotix_ros_manipulators/tree/galactic/interbotix_ros_xsarms/interbotix_xsarm_perception)). Then, either run `pip install -r requirements.txt`, or, alternatively, install transformers. 

## Notes & troubleshooting

Use the ROS GUI program to troubleshoot before running the `point_to_color_nlp.py` script -- specifically, the camera view should be visible, the robot arm should be visible with all components, and there should be "clusters" reflecting objects within the camera view visible within the GUI.
