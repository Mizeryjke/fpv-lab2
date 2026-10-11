import math
import time
from typing import TYPE_CHECKING

from ..flight_state import FlightState
from .handler import FlightStateHandler

if TYPE_CHECKING:
    from ..flight_test_node import FlightTestNode


class NavigatingHandler(FlightStateHandler):
    HOLD_AT_TARGET = 10.0  # с зависання над ціллю перед посадкою

    def __init__(self):
        self._last_log = 0.0
        self._reached_at = None

    def handle(self, node: "FlightTestNode") -> None:
        if node.status is None or not node.status.armed:
            node.fail("Drone disarmed unexpectedly during navigation")
            return
        if node.odometry is None or node.target is None:
            return

        pos = node.odometry.pose.pose.position

        # Зависання над ціллю (час для скриншота)
        if self._reached_at is not None:
            node.send_velocity(0.0, 0.0)
            if time.monotonic() - self._reached_at >= self.HOLD_AT_TARGET:
                dist = math.hypot(node.target[0] - pos.x, node.target[1] - pos.y)
                node.get_logger().info(
                    f"Before landing: actual ({pos.x:.2f}, {pos.y:.2f}), "
                    f"error {dist:.3f} m. Starting landing"
                )
                node.state = FlightState.LANDING
            return

        if node.nav_started_at is None:
            node.nav_started_at = time.monotonic()
            node.get_logger().info("Navigating to target point")

        if time.monotonic() - node.nav_started_at > node.NAV_TIMEOUT:
            node.send_velocity(0.0, 0.0)
            node.fail("Navigation timeout")
            return

        dx = node.target[0] - pos.x
        dy = node.target[1] - pos.y
        dist = math.hypot(dx, dy)

        if dist <= node.TARGET_TOLERANCE:
            node.send_velocity(0.0, 0.0)
            self._reached_at = time.monotonic()
            node.get_logger().info(
                f"Target reached. Actual: ({pos.x:.2f}, {pos.y:.2f}), "
                f"target: ({node.target[0]:.2f}, {node.target[1]:.2f}), "
                f"error: {dist:.3f} m. Holding {self.HOLD_AT_TARGET:.0f} s"
            )
            return

        # плавне сповільнення біля цілі
        speed = min(node.MAX_SPEED, max(node.MIN_SPEED, node.SPEED_GAIN * dist))
        node.send_velocity(speed * dx / dist, speed * dy / dist)

        now = time.monotonic()
        if now - self._last_log >= 1.0:
            self._last_log = now
            node.get_logger().info(
                f"Position ({pos.x:.2f}, {pos.y:.2f}), distance {dist:.2f} m"
            )
