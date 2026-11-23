import rclpy                          # ROS 2 client library for Python
from rclpy.node import Node           # Base class for every ROS 2 node
from sensor_msgs.msg import Image     # Standard ROS 2 message type for images

from std_msgs.msg import String       # String message type (from the template; listed in the assignment, not used here)
from cv_bridge import CvBridge        # Converts between OpenCV images and ROS 2 Image messages
import cv2                            # OpenCV: used to read frames from the camera

class ImagePublisher(Node):
    """Node that reads frames from the webcam and publishes them
    as ROS 2 Image messages on the 'video_frames' topic."""

    def __init__(self):
        # Initialize the parent Node class and name this node 'image_publisher'
        super().__init__('image_publisher')

        # Publisher of Image messages on the 'video_frames' topic. 10 is the queue size.
        self.publisher_ = self.create_publisher(Image, 'video_frames', 10)

        timer_period = 0.1  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

        # Open the default camera (index 0 -> /dev/video0)
        self.cap = cv2.VideoCapture(0)

        # Converter between OpenCV images (numpy arrays) and ROS 2 Image messages
        self.br = CvBridge()

    def timer_callback(self):
        # Called by the timer every 0.1 s.
        # Read one frame from the camera:
        # ret is True if the frame was captured, frame is the image (OpenCV/numpy format)
        ret, frame = self.cap.read()

        if ret == True:
            # Frame captured successfully:
            # convert it from OpenCV format to a ROS 2 Image message and publish it on 'video_frames'
            self.publisher_.publish(self.br.cv2_to_imgmsg(frame))


def main(args=None):
    # Initialize the ROS 2 communication layer
    rclpy.init(args=args)

    # Create the ImagePublisher node
    image_publisher = ImagePublisher()

    # Keep the node running (the timer keeps firing) until Ctrl+C
    rclpy.spin(image_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    image_publisher.destroy_node()

    # Shut down the ROS 2 communication layer
    rclpy.shutdown()


if __name__ == '__main__':
    # Run main() only when this file is executed directly
    main()
