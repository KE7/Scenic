import carla
import math
import scipy

from scenic.core.vectors import Vector, Orientation
from scenic.core.geometry import normalizeAngle


def snapToGround(world, location, blueprint):
    """Mutates @location to have the same z-coordinate as the nearest waypoint in @world."""
    waypoint = world.get_map().get_waypoint(location)
    # patch to avoid the spawn error issue with vehicles and walkers.
    z_offset = 0
    if blueprint is not None and ("vehicle" in blueprint or "walker" in blueprint):
        z_offset = 0.5

    location.z = waypoint.transform.location.z + z_offset
    return location


def scenicToCarlaVector3D(x, y, z=0.0):
    # NOTE: Used for velocity, acceleration; superclass of carla.Location
    z = 0.0 if z is None else z
    return carla.Vector3D(x, -y, z)


def scenicToCarlaLocation(pos, z=None, world=None, blueprint=None):
    if z is None:
        assert world is not None
        return snapToGround(world, carla.Location(pos.x, -pos.y, 0.0), blueprint)
    return carla.Location(pos.x, -pos.y, z)


def scenicToCarlaRotation(orientation):
    pitch, yaw, roll = orientation.r.as_euler("YZX")
    return carla.Rotation(pitch=pitch, yaw=yaw, roll=roll)

def scenicSpeedToCarlaVelocity(speed, heading):
    currYaw = scenicToCarlaRotation(heading).yaw
    xVel = speed * math.cos(currYaw)
    yVel = speed * math.sin(currYaw)
    return scenicToCarlaVector3D(xVel, yVel)

def carlaToScenicPosition(loc):
    return Vector(loc.x, -loc.y, loc.z)

def carlaToScenicElevation(loc):
    return loc.z

def carlaToScenicOrientation(rot):
    angles = (rot.pitch, rot.yaw, rot.roll)
    r = scipy.spatial.transform.Rotation.from_euler(seq="YZX", angles=angles)
    return Orientation(r)

def carlaToScenicHeading(rot):
    return normalizeAngle(-math.radians(rot.yaw + 90))

def carlaToScenicAngularSpeed(vel):
    return math.hypot(
            math.radians(vel.x),
            -math.radians(vel.y),
            math.radians(vel.y)
        )

def carlaToScenicAngularVel(vel):
    return Vector(
            math.radians(vel.x),
            -math.radians(vel.y),
            math.radians(vel.y)
           )


_scenicToCarlaMap = {
    "red": carla.TrafficLightState.Red,
    "green": carla.TrafficLightState.Green,
    "yellow": carla.TrafficLightState.Yellow,
    "off": carla.TrafficLightState.Off,
    "unknown": carla.TrafficLightState.Unknown,
}

def scenicToCarlaTrafficLightStatus(status):
    return _scenicToCarlaMap.get(status, None)

def carlaToScenicTrafficLightStatus(status):
    return str(status).lower()
