import rclpy
from rclpy.node import Node

from example_interfaces.srv import AddTwoInts


class BasicAdditionService(Node):
  def __init__(self):
    super().__init__("basic_addition_service")

    self.srv = self.create_service(AddTwoInts, "addition", self.on_addition)

  def on_addition(self, req, res):
    res.sum = req.a + req.b
    self.get_logger().info(f"srv req={req.a}+{req.b} res={res.sum}")
    return res


def main():
  rclpy.init()
  srv = BasicAdditionService()
  rclpy.spin(srv)
  rclpy.shutdown()

if __name__ == "__main__":
  main()