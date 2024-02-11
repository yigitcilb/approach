#!/usr/bin/env python3
from ultralytics import YOLO
import numpy as np
import rospy
import cv2
import pyrealsense2 as rs
import rospkg

from std_msgs.msg import Float32MultiArray
from yolo_ros.msg import BoxArray
from sensor_msgs.msg import CompressedImage
from vision_msgs.msg import BoundingBox2D
from cv_bridge import CvBridge, CvBridgeError

class YOLOPublisher:
    def __init__(self):
        rospy.init_node('yolo', anonymous=True)
        self.detectionPos=rospy.Publisher("/detections",BoxArray,queue_size=10)
        self.imgPub=rospy.Publisher("/detectedImage/compressed",CompressedImage,queue_size=10)
        
        #Start Realsense Camera
        self.pipeline = rs.pipeline()
        config = rs.config()
        # Get device product line for setting a supporting resolution
        pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        pipeline_profile = config.resolve(pipeline_wrapper)

        device = pipeline_profile.get_device()
        device_product_line = str(device.get_info(rs.camera_info.product_line))

        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

        # Start streaming
        self.pipeline.start(config)

        align_to = rs.stream.color #align to depth
        self.align = rs.align(align_to)

        path = rospkg.RosPack().get_path("yolo_ros")+"/src/"
        self.model=YOLO(path+"bottle.pt")
        self.model.conf=0.7
        self.processed_image = CompressedImage()
        self.bridge = CvBridge()

        # rospy.Subscriber('/camera1/compressed',CompressedImage,self.compressed2cv)
        self.main()
    
    def get_frame(self):
        frames = self.pipeline.wait_for_frames()

        frames = self.pipeline.wait_for_frames()
        aligned_frames = self.align.process(frames)
        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        if not depth_frame or not color_frame:
            return False, None, None
        return True, depth_image, color_image

    def main(self):
        while not rospy.is_shutdown():
            ret, depth_frame, img = self.get_frame()
            # img=self.bridge.compressed_imgmsg_to_cv2(msg)
            frame=cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
            result= self.model(frame) # inference
            boxes_list=[]

            results=result[0].cpu()
            if results.boxes:
                for box_data in results.boxes:
                    # get boxes values
                    arr=[]
                    box = box_data.xywh[0]
                    class_label = box_data.cls
                    arr.append(class_label)
                    arr.append(float(box[0]))
                    arr.append(float(box[1]))
                    arr.append(float(box[2]))
                    arr.append(float(box[3]))
                    # rospy.loginfo([int(box[0])+int(box[2])//2,int(box[1])+int(box[3])//2])
                    arr.append(depth_frame[int(box[1])+int(box[3]/2)-1,int(box[0])+int(box[2]/2)-1])
                    # append msg
                    boxes_list.append(Float32MultiArray(data=arr))

            output = result[0].plot()

            self.detectionPos.publish(data=boxes_list)

            output=cv2.cvtColor(output,cv2.COLOR_BGR2RGB)
            self.processed_image: CompressedImage = self.bridge.cv2_to_compressed_imgmsg(output)
            self.processed_image.header.frame_id = "camera_frame"
            # # Publish new image
            self.imgPub.publish(self.processed_image)     

if __name__ == '__main__':
    try:
        YOLOPublisher()
    except rospy.ROSInterruptException:
        pass
