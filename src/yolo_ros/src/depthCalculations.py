#!/usr/bin/env python3
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from yolo_ros.msg import BoxArray #ilki 0sa şişe 1se tokmak
class cameraStuff:
    def __init__(self):
        rospy.Subscriber("/detections", BoxArray, self.bounding_box_callback)
        self.focalLength = 1.88 #milimetre cinsinden(kameraya göre)
        self.width = 1920 #pixel cinsinden(kameraya göre)
        self.height = 1080 #pixel cinsinden(kameraya göre)
        rospy.spin()
    def bounding_box_callback(self, msg):
        for box in msg.data:
            box=box.data
            if box[0] == 0:
                print("ben sise.")
                self.sise_x = box[1]
                self.sise_y = box[2]
                self.sise_widht = box[3]
                self.sise_height = box[4]
                self.sise_depth = box[5]
                self.sisereelx = self.sise_x + (self.sise_widht / 2)
                self.sisereely = self.sise_y + (self.sise_depth / 2)
            elif box[0] == 1:
                print("ben tokmak.")
                self.tokmak_x = box[1]
                self.tokmak_y = box[2]
                self.tokmak_widht = box[3]
                self.tokmak_height = box[4]
                self.tokmak_depth = box[5]
                self.tokmakreelx = self.tokmak_x + (self.tokmak_widht / 2)
                self.tokmakreely = self.tokmak_y+ (self.tokmak_height/ 2)
        try:
            self.sisepositionx = self.sise_depth / self.focalLength *(self.sisereelx - (self.sise_widht/2)) *1000
            self.sisepositiony = self.sise_depth / self.focalLength *(self.sisereely - (self.sise_depth/2)) *1000
            self.sisepositionz = self.sise_depth *1000
            print(f"SİSE Xİ {self.sisepositionx}") # mm olarak
            print(f"SİSE Yİ {self.sisepositiony}") # mm olarak
            print(f"SİSE Zİ {self.sisepositionz}") # mm olarak
        except:
            pass


if __name__ == "__main__":
    rospy.init_node("approach")
    cameraStuff() 