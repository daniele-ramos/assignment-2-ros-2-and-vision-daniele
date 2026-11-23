import rclpy                          # ROS 2 client library for Python
from rclpy.node import Node           # Base class for every ROS 2 node
from sensor_msgs.msg import Image     # Standard ROS 2 message type for images
from cv_bridge import CvBridge        # Converts between ROS 2 Image messages and OpenCV images
import cv2                            # OpenCV: used here for color conversion
import mediapipe as mp                # Google MediaPipe: machine-learning hand detection
mp_hands = mp.solutions.hands         # Shortcut to MediaPipe's hand-tracking module

from aisd_msgs.msg import Hand        # Custom message with the x positions of the index finger and pinky


class Hands(Node):
    """Node that receives camera images, detects a hand with MediaPipe,
    and publishes the index finger and pinky positions as Hand messages."""

    def __init__(self):
        # Initialize the parent Node class and name this node 'hands'
        super().__init__('hands')

        # Subscribe to the 'video_frames' topic (published by image_publisher).
        # Every Image received calls listener_callback. 10 is the queue size.
        self.subscription = self.create_subscription(
            Image,
            'video_frames',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

        # A converter between ROS and OpenCV images
        self.br = CvBridge()

        # Publisher of Hand messages on the 'cmd_hand' topic (the move node subscribes to it)
        self.hand_publisher = self.create_publisher(Hand, 'cmd_hand', 10)

    def listener_callback(self, msg):
        # Called automatically every time an Image arrives on 'video_frames'.

        # Convert the ROS 2 Image message into an OpenCV image (numpy array, BGR colors)
        image = self.br.imgmsg_to_cv2(msg)

        # MediaPipe detects 21 landmarks per hand (numbered 0-20):
        # 20 is the tip of the pinky, 8 is the tip of the index finger
        PINKY_FINGER_TIP = 20
        INDEX_FINGER_TIP = 8

        # Analyse the image for hands.
        # Create a MediaPipe hand detector; 'with' releases its resources when the block ends.
        with mp_hands.Hands(
            model_complexity=0,               # 0 = lightest/fastest model (1 is more accurate but slower)
            min_detection_confidence=0.5,     # minimum 50% confidence to consider something a hand
            min_tracking_confidence=0.5) as myhands:  # minimum 50% confidence to keep tracking the hand

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference (MediaPipe does not need to copy it).
            image.flags.writeable = False

            # OpenCV uses BGR color order, but MediaPipe expects RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Run the hand detection; results holds the landmarks of any hands found
            results = myhands.process(image)

            # multi_hand_landmarks is None when no hand is in the image
            if results.multi_hand_landmarks:
                # Publish the hand position in terms of index finger and pinky
                msg = Hand()

                # [0] = first detected hand; .landmark[N] = landmark N; .x = horizontal
                # position normalized from 0.0 (left edge) to 1.0 (right edge of the image)
                msg.xpinky = results.multi_hand_landmarks[0].landmark[PINKY_FINGER_TIP].x
                msg.xindex = results.multi_hand_landmarks[0].landmark[INDEX_FINGER_TIP].x

                # Only publish if some node (move) is subscribed to 'cmd_hand'
                if self.hand_publisher.get_subscription_count() > 0:
                    self.hand_publisher.publish(msg)
                else:
                    # Nobody is listening yet: log a message instead of publishing
                    self.get_logger().info('waiting for subcriber')


def main(args=None):
    # Initialize the ROS 2 communication layer
    rclpy.init(args=args)

    # Create the Hands node
    hands = Hands()

    # Keep the node running and processing incoming images until Ctrl+C
    rclpy.spin(hands)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    hands.destroy_node()

    # Shut down the ROS 2 communication layer
    rclpy.shutdown()


if __name__ == '__main__':
    # Run main() only when this file is executed directly
    main()