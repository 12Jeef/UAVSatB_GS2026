import rclpy
from rclpy.node import Node

from example_interfaces.srv import AddTwoInts


class BasicAdditionClient(Node):
  def __init__(self):
    super().__init__("basic_addition_client")

    self.cli = self.create_client(AddTwoInts, "addition")
    self.req = AddTwoInts.Request()

    while not self.cli.wait_for_service(timeout_sec=1):
      self.get_logger().info("cli: srv unavailable, retry 1s")

  def send_req(self, a, b):
    self.req.a = a
    self.req.b = b
    return self.cli.call_async(self.req)


def main():
  rclpy.init()

  cli = BasicAdditionClient()
  future = cli.send_request(12, 6)
  rclpy.spin_until_future_complete(cli, future)
  res = future.result()
  cli.get_logger().info(f"12 + 6 = {res.sum}")

  rclpy.shutdown()

if __name__ == "__main__":
  main()
