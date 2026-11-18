import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image

from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2


class ImagePublisher(Node):

    def __init__(self):
        super().__init__('image_publisher')                 # create a node called image_publisher
        self.publisher_ = self.create_publisher(Image, 'video_frames', 10) # publish the image in topic video_frame
        timer_period = 0.1                                  # seconds - every 0.1sec read the camera
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.cap = cv2.VideoCapture(0)                      # open the webcam
        self.br = CvBridge()

    def timer_callback(self):
        ret, frame = self.cap.read()
        if ret == True:                                     # if read the image then
            self.publisher_.publish(self.br.cv2_to_imgmsg(frame))    # define image as Ros2 topic


def main(args=None):
    rclpy.init(args=args)

    image_publisher = ImagePublisher()

    rclpy.spin(image_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    image_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
