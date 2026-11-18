import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import mediapipe as mp
mp_hands = mp.solutions.hands

from aisd_msgs.msg import Hand


class Hands(Node):

    def __init__(self):
        super().__init__('hands')                       # create a node called hands
        self.subscription = self.create_subscription(
            Image,
            'video_frames',                             # subscription in a topic 'video_frames'
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

        # A converter between ROS and OpenCV images
        self.br = CvBridge()
        self.hand_publisher = self.create_publisher(Hand, 'cmd_hand', 10)   # publish Hand messages to the topic cmd_hand


    def listener_callback(self, msg):
        self.get_logger().info('I heard: "%s"' % msg.data)

    def listener_callback(self, msg):       # function called automactally every image read in topic video_fram
        image = self.br.imgmsg_to_cv2(msg)  # convert image from ros format to OpenCV

        PINKY_FINGER_TIP = 20
        INDEX_FINGER_TIP = 8
        # Analyse the image for hands
        with mp_hands.Hands(
            model_complexity=0,
            min_detection_confidence=0.5,   # min 50% of confidence to consider as a hand
            min_tracking_confidence=0.5) as myhands:    # 50% of confidence to continue reading the hand

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # convert OpenCV color system to MediaPipe RGB
            results = myhands.process(image)                # detect the hand
            if results.multi_hand_landmarks:
                #publish the hand position in terms of index finger and pinky
                msg = Hand()
                msg.xpinky = results.multi_hand_landmarks[0].landmark[PINKY_FINGER_TIP].x   # get the x position of pink
                msg.xindex = results.multi_hand_landmarks[0].landmark[INDEX_FINGER_TIP].x   # get the x position of index
                if self.hand_publisher.get_subscription_count() > 0:           # verify if anyone is reading the topic cmd_hand
                    self.hand_publisher.publish(msg)
                else:
                    self.get_logger().info('waiting for subcriber')            # if not, show a message


def main(args=None):
    rclpy.init(args=args)

    hands = Hands()

    rclpy.spin(hands)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    hands.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
