import time
import colorsys
from interbotix_xs_modules.arm import InterbotixManipulatorXS
from interbotix_perception_modules.armtag import InterbotixArmTagInterface
from interbotix_perception_modules.pointcloud import InterbotixPointCloudInterface

from transformers import BertTokenizer, BertForMultipleChoice
import torch

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = BertForMultipleChoice.from_pretrained("bert-base-uncased")

# This script uses a color/depth camera to get the arm to find blocks, and point to them 
# depending on the user's command in natural language. The user can either input a color literal
# i.e. "red" or "green", or a word or phrase to be parsed into a color using BERT.
#
# For this demo, the arm is placed to the right of the camera facing outward. When the
# end-effector is located at x=0, y=0.3, z=0.2 w.r.t. the 'rx200/base_link' frame, the AR
# tag should be clearly visible to the camera.
#
# To get started, open a terminal and type 'roslaunch interbotix_xsarm_perception xsarm_perception.launch robot_model:=wx200'
# Then change to this directory and type 'python color_sorter.py'

def main():
    # Initialize the arm module along with the pointcloud and armtag modules
    bot = InterbotixManipulatorXS("rx200", moving_time=1.5, accel_time=0.75)
    pcl = InterbotixPointCloudInterface()
    armtag = InterbotixArmTagInterface()

    # set initial arm and gripper pose
    bot.dxl.robot_set_motor_registers("single", "shoulder", "Position_P_Gain", 1500)
    bot.dxl.robot_set_motor_registers("single", "elbow", "Position_P_Gain", 1500)
    bot.arm.set_ee_pose_components(x=0.3, z=0.2)
    bot.gripper.open()

    # Run until "quit" command is entered
    while True:
        prompt = input('Give me an input! ')

        if prompt.lower() == "exit" or prompt.lower() == "q" or prompt.lower() == "quit":
            bot.arm.set_ee_pose_components(x=0.3, z=0.2)
            bot.arm.go_to_sleep_pose()
            exit()
        elif prompt.lower() == "armtag":
            # get the ArmTag pose for camera calibration to the robot's position
            bot.arm.set_ee_pose_components(y=0.3, z=0.2)
            time.sleep(0.5)
            armtag.find_ref_to_arm_base_transform()
            bot.arm.set_ee_pose_components(x=0.3, z=0.2)
            continue

        target_color = ""

        if "red" in prompt.lower():
            target_color = "red"
        elif "orange" in prompt.lower():
            target_color = "orange"
        elif "yellow" in prompt.lower():
            target_color = "yellow"
        elif "green" in prompt.lower():
            target_color = "green"
        elif "blue" in prompt.lower():
            target_color = "blue"
        elif "purple" in prompt.lower():
            target_color = "purple"
        else:
            # Use BERT for multiple choice to determine what color the user inputted
            r = "red"
            o = "orange"
            y = "yellow"
            g = "green"
            b = "blue"
            v = "purple"
            labels = torch.tensor(0).unsqueeze(0)
            # We don't use all the colors since this drastically lowers the accuracy
            # of the BERT model, using up to 3 seems to work decently well
            choices = [r, b] # [r, o, y, g, b, v]
            prompts = [prompt] * len(choices)

            encoding = tokenizer(prompts, choices, return_tensors="pt", padding=True)
            outputs = model(**{k: v.unsqueeze(0) for k, v in encoding.items()}, labels=labels)  # batch size is 1
            logits = outputs.logits
            target_color = choices[logits.argmax().item()]
            print(target_color)

        # Identify all clusters using camera
        success, clusters = pcl.get_cluster_positions(ref_frame="rx200/base_link", sort_axis="y", reverse=True)

        # Search through all the clusters and see if any match specified color
        found_color = False
        for cluster in clusters:
            clr = color_compare(cluster["color"])

            # If the cluster's color is correct
            if (clr == target_color):
                print("Found target cluster!")
                x, y, z = cluster["position"]
                bot.arm.set_ee_pose_components(x=x, y=y, z=0.15, pitch=0)
                bot.arm.set_ee_pose_components(x=x, y=y, z=0.1, pitch=0.5)

                time.sleep(2)
                found_color = True

                bot.arm.set_ee_pose_components(x=x, y=y, z=0.15, pitch=0)

        if found_color == False:
            print("I didnt find the color :( now im sad")

            # Robot "shakes its head"
            bot.arm.set_ee_pose_components(x=0.3, y=-0.15, z=0.15, pitch=0.1)
            bot.arm.set_ee_pose_components(x=0.3, y=0.15, z=0.15, pitch=0.1)
            bot.arm.set_ee_pose_components(x=0.3, y=-0.15, z=0.15, pitch=0.1)
            bot.arm.set_ee_pose_components(x=0.3, y=0.15, z=0.15, pitch=0.1)

        # Reset to "default" position
        bot.arm.set_ee_pose_components(x=0.3, z=0.2)

# Determines the color of each object using the Hue value in the HSV color space
def color_compare(rgb):
    r,g,b = [x/255.0 for x in rgb]
    h,s,v = colorsys.rgb_to_hsv(r,g,b)

    if h < 0.019: color = "red"
    elif 0.019 < h <= 0.075: color = "orange"
    elif 0.075 < h <= 0.2: color = "yellow"
    elif 0.2 < h <= 0.5: color = "green"
    elif 0.5 < h <= 0.7: color = "blue"
    elif 0.7 < h <= 0.9: color = "purple"
    elif h > 0.9: color = "red"
    else: color = "unknown"

    # print(color, h)

    return color

if __name__=='__main__':
    main()
