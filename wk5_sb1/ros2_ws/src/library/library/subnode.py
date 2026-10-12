import rclpy
from rclpy.node import Node

from std_msgs.msg import String


class BasicStringSubscriber(Node):
  def __init__(self):
    super().__init__("basic_string_subscriber")

    self.subscription = self.create_subscription(String, "topic", self.on_data, 10)

  def on_data(self, msg):
    self.get_logger().info(f"sub {msg.data}")

def main():
  rclpy.init()
  sub = BasicStringSubscriber()
  rclpy.spin(sub)
  rclpy.shutdown()

if __name__ == "__main__":
  main()
