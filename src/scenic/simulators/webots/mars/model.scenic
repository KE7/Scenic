"""Scenic model for Mars rover scenarios in Webots."""

from pathlib import Path

from scenic.simulators.webots.model import WebotsObject, Ground, Hill

# Set up workspace
width = 10
length = 10
workspace = Workspace(RectangularRegion(0 @ 0, 0, width, length))

# types of objects

class MarsGround(Ground):
    color: (220, 114, 9)
    gridSize: 20

class MarsHill(Hill):
    position: new Point in workspace
    width: Range(1,2)
    length: Range(1,2)
    height: Range(0.1, 0.3)
    spread: Range(0.2, 0.3)
    regionContainedIn: everywhere

class Goal(WebotsObject):
    """Flag indicating the goal location."""
    width: 0.1
    length: 0.1
    webotsType: 'GOAL'
    color: (9 ,163, 220)

class Rover(WebotsObject):
    """Mars rover."""
    width: 0.5
    length: 0.7
    height: 0.4
    webotsType: 'ROVER'
    rotationOffset: (90 deg, 0, 0)

class Debris(WebotsObject):
    """Abstract class for debris scattered randomly in the workspace."""
    # Recess things into the ground slightly by default
    baseOffset: (0,0, -self.height/2-0.025)

class BigRock(Debris):
    """Large rock."""
    shape: MeshShape.fromFile(Path(localPath(".")).parent.parent.parent.parent.parent / "tools" / "meshes" / "webots_rock_large.obj.bz2")
    yaw: Range(0, 360 deg)
    webotsType: 'ROCK_BIG'
    positionOffset: Vector(0,0, -self.height/2)

class Rock(Debris):
    """Small rock."""
    shape: MeshShape.fromFile(Path(localPath(".")).parent.parent.parent.parent.parent / "tools" / "meshes" / "webots_rock_small.obj.bz2")
    yaw: Range(0, 360 deg)
    webotsType: 'ROCK_SMALL'
    positionOffset: Vector(0,0, -self.height/2)

class Pipe(Debris):
    """Pipe with variable length."""
    width: 0.2
    length: Range(0.5, 1.5)
    height: self.width
    shape: CylinderShape(initial_rotation=(90 deg, 0, 90 deg))
    yaw: Range(0, 360 deg)
    webotsType: 'PIPE'
    rotationOffset: (90 deg, 0, 90 deg)

    def startDynamicSimulation(self):
        # Apply variable length
        self.webotsObject.getField('height').setSFFloat(self.length)
