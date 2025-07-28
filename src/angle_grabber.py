import math
from dataclasses import dataclass, field
from functools import reduce

import bpy
import mathutils

MODELS_TO_GRAB_ANGLES: dict[str, "Bone"] = dict()


@dataclass
class Bone:
    name: str
    angle: bool = False
    parent_armature: "Armature | None" = None
    parent: "Bone | None" = None
    children: list["Bone"] = field(default_factory=list)
    bpy_bone: bpy.types.PoseBone | None = None
    invalid: bool = field(default=False)

    def __post_init__(self):
        assert not (self.parent is None and self.parent_armature is None), (
            f"Bone: {self.get_full_name()} must have either parent or parent_armature."
        )
        if self.parent_armature is None and self.parent is not None:
            self.parent_armature = self.parent.parent_armature
        assert self.parent_armature is not None, (
            f"Bone: {self.get_full_name()} has no parent_armature."
        )
        assert self.parent_armature.armature is not None, (
            f"Armature: {self.parent_armature.name} is not valid."
        )
        assert self.parent_armature.armature.pose is not None, (
            f"Armature: {self.parent_armature.name} has no pose."
        )
        for n in self.parent_armature.armature.pose.bones:
            if n.name == self.name:
                print(
                    f"Bone: {self.get_full_name()} found in parent armature: {self.parent_armature.name}."
                )
                self.bpy_bone = n
                break
        if self.bpy_bone is None:
            print(
                f"Bone: {self.get_full_name()} not found in {'armature' if self.parent_armature else 'parent bone'}."
            )
            self.invalid = True
            return
        if self.angle:
            MODELS_TO_GRAB_ANGLES[self.get_full_name()] = self
        if self.children is None:
            return
        self.children = [Bone(**child, parent=self) for child in self.children]
        if reduce(
            lambda x, y: x or y,
            [child.invalid for child in self.children],
            False,
        ):
            print(f"Bone: {self.get_full_name()} has invalid children.")
            self.invalid = True
            return

    def get_full_name(self) -> str:
        if self.parent is None:
            if self.parent_armature is not None:
                return f"{self.parent_armature.name}.{self.name}"
            return self.name
        return f"{self.parent.get_full_name()}.{self.name}"

    def get_angle(self) -> float | mathutils.Matrix | None:
        """Returns the angle of the bone in degrees."""
        if not self.parent:
            return self.bpy_bone.matrix if self.bpy_bone else None
        if (
            self.bpy_bone is None
            or self.bpy_bone.matrix is None
            or self.parent.bpy_bone is None
            or self.parent.bpy_bone.matrix is None
        ):
            print(f"Bone: {self.get_full_name()} has no matrix.")
            return None
        thisQ = self.bpy_bone.matrix.to_quaternion()
        parentQ = self.parent.bpy_bone.matrix.to_quaternion()
        relative_rot = thisQ.rotation_difference(parentQ)
        return math.degrees(relative_rot.angle)


@dataclass
class Armature:
    name: str
    armature: bpy.types.Object | None = field(default=None)
    invalid: bool = field(default=False)
    bones: list[Bone] = field(default_factory=list)

    def __post_init__(self):
        self.armature = bpy.data.objects.get(self.name)
        if not self.armature:
            print(f"Armature: {self.name} not found.")
            self.invalid = True
            return
        print(f"Armature: {self.name} found. type: {self.armature.type}")
        assert self.armature.type == "ARMATURE", (
            f"Armature: {self.name} is not of type ARMATURE."
        )
        self.bones = [Bone(**v, parent_armature=self) for v in self.bones]
        if reduce(
            lambda x, y: x or y,
            [bone.invalid for bone in self.bones],
            False,
        ):
            print(f"Armature: {self.name} has invalid bones.")
            self.invalid = True
            return


def set_model_namespace(config: dict) -> bool:
    """Grabs the armature and its bones from the scene and sets up the MODELS_TO_GRAB_ANGLES
    returns True if the armature is valid, False otherwise.
    """
    if len(MODELS_TO_GRAB_ANGLES) > 0:
        print("Models to grab angles already set.")
        return False
    print(config)
    armatures = [Armature(**v, name=k) for k, v in config.items()]
    return reduce(
        lambda x, y: x or y,
        [armature.invalid for armature in armatures],
        False,
    )


def get_model_angles() -> dict[str, float | mathutils.Matrix | None]:
    """Returns the angles of the bones in the armature."""
    return {k: v.get_angle() for k, v in MODELS_TO_GRAB_ANGLES.items()}
