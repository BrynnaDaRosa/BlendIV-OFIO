import os
import bpy
from .parser import parse
from .onim_import import import_onim


def import_oad(oad_path, arma_ob):
    """
    Imports an .oad file onto an armature object.
    Imports each .onim the .oad contains.
    """
    with open(oad_path, "r") as f:
        oad = parse(f)
    oad = oad[1]  # Skip version in oad[0]

    oad_dir = os.path.dirname(oad_path)

    for line in oad:
        if line[0] == "crAnimation":
            onim_path = line[1].replace('\\', os.path.sep)
            onim_path = os.path.join(oad_dir, onim_path)
            import_onim(onim_path, arma_ob)
