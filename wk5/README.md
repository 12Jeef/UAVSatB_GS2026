# ROS 2

> Not an actual operating system (OS)

## What is it?

Multiple languages, same communication protocol. Each program is independent (start/crash/stop/etc) and declared as a "node."
- Nodes are *small* since smaller means easier to diagnose and debug.
- Information is exchanged via messages communicated between nodes.
- Nodes discover other nodes via DDS (ePromisa Fast DDS) which runs over network P2P.
  - ROS 1 used a master node which had catastrophic consequences when it failed.

## How to talk?

### Topics
> A stream of data

Publishers dump. Subscribers read. No ack, no response, no checking. Each topic has a name (EX `/camera/image`) and a type (EX `sensor_msgs/Image` or a `.msg` file).

**Usage**:
```py
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32

class NumberPubSub(Node):
  def __init__(self):
    super().__init__("number_pub_sub")

    self.pub = self.create_publisher(Float32, "number_outgoing", 10)
    self.timer = self.create_timer(0.1, self.write)

    self.create_subscription(Float32, "/number_incoming", self.read, 10)

  def write(self):
    self.pub.publish(Float32(data=12.5))
  
  def read(self, msg):
    self.get_logger().info(f"number_incoming: {msg.value}")

def main():
  rclpy.init()
  rclpy.spin(NumberPubSub())
  rclpy.shutdown()
```

**Message Attributes**:
- Reliability:
  - Reliable: resend until ack of arrival (TCP)
  - Best effort: send and ignore loss (UDP)
- History:
  - Keep last N: see `10` from above
- Durability:
  - Volatile: information as soon as you subscribe
  - Transient local: get previous N as well
> Requires matching attributes to properly pub-sub connect!

### Service
> A question

Clients ask. Servers respond. Must be *quick* (synchronous). Each service a name (EX `/arm`) and a type (EX `std_srvs/srv/SetBool` or a `.srv` file).

**Usage**:

```
# .srv file

float32 data   # req
---
bool success   # res
string message
```

```py
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32

class NumberService(Node):
  def __init__(self):
    super().__init__("number_service")

    self.number = 0
    self.srv = self.create_service(SetFloat32, "number", self.on_number)

def on_number(self, request, response):
    self.number = request.data
    response.success = True
    response.message = f"number={self.number}"
    return response

def main():
  rclpy.init()
  rclpy.spin(NumberService())
  rclpy.shutdown()
```

### Action
> A task

Clients trigger. Servers report progress and result. Slower, can be canceled (asynchronous). As an example, below is a `fly_to` action.

```
# .action file

geometry_msgs/Point target  # goal
---
bool success                # result
---
float32 distance_remaining  # feedback/progress
```
