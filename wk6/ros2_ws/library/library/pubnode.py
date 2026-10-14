import rclpy
from rclpy.node import Node

from std_msgs.msg import String


class BasicStringPublisher(Node):
  def __init__(self):
    super().__init__("basic_string_publisher")

    self.pub = self.create_publisher(String, "topic", 10)

    self.i = 0

    self.timer = self.create_timer(0.5, self.periodic)

  def periodic(self):
    msg = String()
    msg.data = f"i={self.i}"

    self.i += 1

    self.pub.publish(msg)
    self.get_logger().info(f"pub {msg.data}")


def main():
  rclpy.init()
  pub = BasicStringPublisher()
  rclpy.spin(pub)
  rclpy.shutdown()

if __name__ == "__main__":
  main()
