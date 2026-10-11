from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry
from std_srvs.srv import Trigger
from ardupilot_msgs.msg import Status
from ardupilot_msgs.srv import ArmMotors, ModeSwitch, Takeoff

from .flight_state import FlightState
from .handlers import HANDLERS


class FlightTestNode(Node):
    GUIDED_MODE = 4
    LAND_MODE = 9
    TAKEOFF_ALTITUDE = 5.0
    HOVER_DURATION = 8.0

    # --- Варіант 34: dx = 4.0, dy = 1.1 ---
    # x_target = x0 - dx, y_target = y0 - dy
    TARGET_SIGN = -1.0        # -1 за формулою лаби; +1 лише для тесту
    TARGET_DX = 4.0
    TARGET_DY = 1.1
    TARGET_TOLERANCE = 0.25   # м
    MAX_SPEED = 1.0           # м/с
    MIN_SPEED = 0.15          # м/с
    SPEED_GAIN = 0.6          # v = SPEED_GAIN * відстань
    NAV_TIMEOUT = 60.0        # с
    CMD_FRAME_ID = "map"     # див. примітку в інструкції

    def __init__(self):
        super().__init__("flight_test")
        self.state = FlightState.WAITING_FOR_SYSTEM
        self.request_in_progress = False
        self.status = None
        self.odometry = None
        self.hover_started_at = None
        self.start_position = None
        self.target = None
        self.nav_started_at = None
        self._handlers = HANDLERS

        self.create_subscription(Status, "/ap/v1/status", self.status_callback, 10)
        self.create_subscription(Odometry, "/odometry", self.odometry_callback, 10)
        self.cmd_vel_publisher = self.create_publisher(
            TwistStamped, "/ap/v1/cmd_vel", 10
        )

        self.prearm_client = self.create_client(Trigger, "/ap/v1/prearm_check")
        self.mode_client = self.create_client(ModeSwitch, "/ap/v1/mode_switch")
        self.arm_client = self.create_client(ArmMotors, "/ap/v1/arm_motors")
        self.takeoff_client = self.create_client(
            Takeoff, "/ap/v1/experimental/takeoff"
        )

        self.timer = self.create_timer(0.2, self.control_loop)
        self.get_logger().info("Flight test node started")
        self.get_logger().info("Waiting for ArduPilot and ROS services...")

    def status_callback(self, message):
        self.status = message

    def odometry_callback(self, message):
        self.odometry = message
        if self.start_position is None:
            p = message.pose.pose.position
            self.start_position = (p.x, p.y)
            self.target = (p.x + self.TARGET_SIGN * self.TARGET_DX, p.y + self.TARGET_SIGN * self.TARGET_DY)
            self.get_logger().info(
                f"Start: ({p.x:.2f}, {p.y:.2f}); "
                f"target: ({self.target[0]:.2f}, {self.target[1]:.2f})"
            )

    def send_velocity(self, vx, vy):
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.CMD_FRAME_ID
        msg.twist.linear.x = float(vx)
        msg.twist.linear.y = float(vy)
        msg.twist.linear.z = 0.0
        self.cmd_vel_publisher.publish(msg)

    def services_ready(self):
        return (
            self.prearm_client.service_is_ready()
            and self.mode_client.service_is_ready()
            and self.arm_client.service_is_ready()
            and self.takeoff_client.service_is_ready()
        )

    def control_loop(self):
        handler = self._handlers.get(self.state)
        if handler is not None:
            handler.handle(self)

    def call_mode_switch(self, mode, callback):
        self.request_in_progress = True
        request = ModeSwitch.Request()
        request.mode = mode
        future = self.mode_client.call_async(request)
        future.add_done_callback(callback)
        self.get_logger().info(f"Requesting flight mode {mode}")

    def fail(self, message):
        self.get_logger().error(message)
        self.state = FlightState.ERROR
