# std_gamekit.py
# Corvus GameKit & 2D Physics Simulation Engine
# Provides rigid bodies, velocity integration, AABB/Circle collisions, and physics worlds.

import math
from typing import Any, List, Optional, Tuple

class PhysicsBody:
    def __init__(self, x: float, y: float, radius: float = 10.0, width: float = 20.0, height: float = 20.0, shape: str = "circle", is_static: bool = False):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.ax = 0.0
        self.ay = 0.0
        self.mass = 1.0 if not is_static else 0.0
        self.radius = float(radius)
        self.width = float(width)
        self.height = float(height)
        self.shape = shape  # "circle" or "rect"
        self.restitution = 0.7  # Bounciness (0.0 to 1.0)
        self.friction = 0.98
        self.is_static = is_static
        self.tag = ""

    def apply_force(self, fx: float, fy: float):
        if not self.is_static and self.mass > 0:
            self.ax += fx / self.mass
            self.ay += fy / self.mass

    def set_velocity(self, vx: float, vy: float):
        if not self.is_static:
            self.vx = float(vx)
            self.vy = float(vy)

    def collides_with(self, other: 'PhysicsBody') -> bool:
        if self.shape == "circle" and other.shape == "circle":
            dx = self.x - other.x
            dy = self.y - other.y
            dist_sq = dx * dx + dy * dy
            rad_sum = self.radius + other.radius
            return dist_sq <= (rad_sum * rad_sum)
        
        # AABB rect-rect collision
        left_a = self.x - self.width / 2
        right_a = self.x + self.width / 2
        top_a = self.y - self.height / 2
        bot_a = self.y + self.height / 2

        left_b = other.x - other.width / 2
        right_b = other.x + other.width / 2
        top_b = other.y - other.height / 2
        bot_b = other.y + other.height / 2

        return not (right_a < left_b or left_a > right_b or bot_a < top_b or top_a > bot_b)

    def __repr__(self):
        return f"<PhysicsBody x={self.x:.1f} y={self.y:.1f} vx={self.vx:.1f} vy={self.vy:.1f}>"


class PhysicsWorld:
    def __init__(self, gx: float = 0.0, gy: float = 9.8):
        self.gx = float(gx)
        self.gy = float(gy)
        self.bodies: List[PhysicsBody] = []
        self.bounds_w = 800
        self.bounds_h = 600

    def set_gravity(self, gx: float, gy: float):
        self.gx = float(gx)
        self.gy = float(gy)

    def create_body(self, x: float, y: float, radius: float = 10.0, is_static: bool = False) -> PhysicsBody:
        b = PhysicsBody(x=x, y=y, radius=radius, shape="circle", is_static=is_static)
        self.bodies.append(b)
        return b

    def create_box(self, x: float, y: float, width: float, height: float, is_static: bool = False) -> PhysicsBody:
        b = PhysicsBody(x=x, y=y, width=width, height=height, shape="rect", is_static=is_static)
        self.bodies.append(b)
        return b

    def step(self, dt: float = 0.016):
        """Advance physics simulation by dt seconds."""
        for b in self.bodies:
            if b.is_static:
                continue

            # Apply gravity
            b.vx += (self.gx + b.ax) * dt
            b.vy += (self.gy + b.ay) * dt

            # Apply velocity damping/friction
            b.vx *= b.friction
            b.vy *= b.friction

            # Update position
            b.x += b.vx * dt
            b.y += b.vy * dt

            # Reset frame accelerations
            b.ax = 0.0
            b.ay = 0.0

    def resolve_bounds(self, width: float, height: float):
        """Keep dynamic bodies within screen rectangle with bounce restitution."""
        for b in self.bodies:
            if b.is_static:
                continue

            r = b.radius if b.shape == "circle" else b.width / 2
            # Horizontal bounds
            if b.x - r < 0:
                b.x = r
                b.vx = -b.vx * b.restitution
            elif b.x + r > width:
                b.x = width - r
                b.vx = -b.vx * b.restitution

            # Vertical bounds
            if b.y - r < 0:
                b.y = r
                b.vy = -b.vy * b.restitution
            elif b.y + r > height:
                b.y = height - r
                b.vy = -b.vy * b.restitution

    def clear(self):
        self.bodies.clear()


def create_world(gx: float = 0.0, gy: float = 9.8) -> PhysicsWorld:
    return PhysicsWorld(gx=gx, gy=gy)
