# robot_color_picker

Command-line program that uses the Interbotix Perception module and an RX200 robot arm to match words to colors and direct the robot arm to point to the corresponding colored object.

## Run instructions

```
./roslaunch_script
```
Running the above command will launch the ROS GUI program.

```
./roslaunch_perception_script
```
Running the above command will launch the ROS GUI program with the perception module, which will have a camera view and fine-tuning options for using a RealSense camera with the robot arm.

```
python point_to_color_nlp.py
```
To run the script that points to colors, run the `roslaunch_perception_script` first, then open up in another terminal and run the `point_to_color_nlp.py` script.
