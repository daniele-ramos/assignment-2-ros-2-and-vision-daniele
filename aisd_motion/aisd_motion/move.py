import rclpy                              # ROS 2 client library for Python
from rclpy.node import Node               # Base class for every ROS 2 node
from aisd_msgs.msg import Hand            # Custom message with the x positions of the index finger and pinky
from geometry_msgs.msg import Twist       # Standard velocity message (linear + angular)


class Move(Node):
    """Node that receives Hand messages and converts them into velocity
    commands (Twist) for the turtlesim or the Create 3."""

    def __init__(self):
        # Initialize the parent Node class and name this node 'move'
        super().__init__('move')

        # Subscribe to the 'cmd_hand' topic (published by the hands node).
        # Every Hand message received calls listener_callback.
        # 10 is the queue size (QoS history depth).
        self.subscription = self.create_subscription(
            Hand,
            'cmd_hand',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

        # Publisher of Twist messages on the 'cmd_vel' topic,
        # which the turtlesim (remapped) and the Create 3 listen to.
        # 10 is the maximum queue size.
        self.vel_publisher = self.create_publisher(Twist, 'cmd_vel', 10)

    def listener_callback(self, msg):
        # Called every time a Hand message arrives on 'cmd_hand'.
        # msg.xindex and msg.xpinky are normalized x positions (0.0 = left edge, 1.0 = right edge of the image).

        angle = 0.0    # angular velocity (rad/s): positive turns left, negative turns right
        linear = 0.0   # linear velocity (m/s): positive moves forward

        # --- Rotation: based on where the index finger is in the image ---
        if msg.xindex > 0.65:
            # Index finger on the right side of the image -> turn right
            self.get_logger().info('right')
            angle = -1.0
            linear = 0.0   # turn in place
        elif msg.xindex < 0.35:
            # Index finger on the left side of the image -> turn left
            self.get_logger().info('left')
            angle = 1.0
            linear = 0.0  # turn in place
        else:
            # Index finger near the center (0.35 to 0.65) -> no rotation (dead zone)
            angle = 0.0
            # --- Forward motion: based on the index finger vs. pinky position ---
            if msg.xindex > msg.xpinky:
                # Index finger to the right of the pinky (hand facing one way) -> move forward
                self.get_logger().info('come')
                linear = 1.0
            
            else:
                # Otherwise (hand turned the other way) -> stop
                self.get_logger().info('stay')
                linear = 0.0

        # Build the velocity message
        twist = Twist()
        twist.linear.x = linear    # forward/backward speed along the robot's x axis
        twist.angular.z = angle    # rotation speed around the vertical z axis

        # Only publish if some node (turtlesim / Create 3) is subscribed to 'cmd_vel'
        if self.vel_publisher.get_subscription_count() > 0:
            self.vel_publisher.publish(twist)
        else:
            self.get_logger().info('waiting for subcriber')


def main(args=None):
    # Initialize the ROS 2 communication layer
    rclpy.init(args=args)

    # Create the Move node
    move = Move()

    # Keep the node running and processing callbacks until Ctrl+C
    rclpy.spin(move)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    move.destroy_node()

    # Shut down the ROS 2 communication layer
    rclpy.shutdown()


if __name__ == '__main__':
    # Run main() only when this file is executed directly
    main()