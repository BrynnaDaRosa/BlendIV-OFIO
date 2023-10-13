import os
import bpy
from mathutils import Quaternion, Vector
from .bone_names import BoneNameMap
from .parser import parse, get_key, get_after_key


def import_onim(onim_path, arma_ob):
    """
    Imports a .onim file for an armature object.
    Stashes the created action to an NLA track.
    """
    with open(onim_path, "r") as f:
        onim = parse(f)
    anim_name = os.path.basename(onim_path)
    bind_pose = gather_bind_pose(arma_ob.data)

    action = OnimImport(onim, anim_name, bind_pose).run()

    stash_action(arma_ob, action)


def stash_action(ob, action):
    if not ob.animation_data:
        ob.animation_data_create()

    nla = ob.animation_data.nla_tracks

    # Check if track for the action already exists
    for track in nla:
        if track.name == action.name:
            track.strips[0].action = action  # Update the action
            break
    else:
        # If not, create a new track and add the action
        track = nla.new()
        track.name = action.name
        track.strips.new(action.name, 0, action)

    track.lock = True
    track.mute = True

    # Set the action as the active action
    ob.animation_data.action = action


def gather_bind_pose(arma):
    """
    Gathers the local-to-parent (Loc,Rot) for each bone.
    """
    bind_pose = {}

    for bone in arma.bones:
        # Matrix relative to arma
        m = bone.matrix_local
        # Cancel the parent to get relative to parent
        if bone.parent:
            m = bone.parent.matrix_local.inverted() @ m

        loc, rot, _scale = m.decompose()  # Note: edit bones have no scale
        bind_pose[bone.name] = (loc, rot)

    return bind_pose


class OnimImport:
    def __init__(self, onim, action_name, bind_pose):
        self.onim = onim[1]  # Ignore version in onim[0]
        self.bind_pose = bind_pose
        self.action = bpy.data.actions.new(action_name)
        self.dt = 0

    def run(self):
        print("[DEBUG] Running OnimImport... V1")
        self.calculate_dt()
        print(f"[DEBUG] Calculated dt: {self.dt}")
        self.process_animation()
        return self.action

    def calculate_dt(self):
        onim = self.onim
        frames = get_key(onim, "Frames")
        duration = get_key(onim, "Duration")
        print(f"[DEBUG] Frames: {frames}, Duration: {duration}")

        # Convert duration from seconds to Blender-frames
        # using scene's current FPS
        fps = bpy.context.scene.render.fps
        bf_duration = duration * fps

        # Calculate one frame length in Blender-frames
        self.dt = bf_duration / frames

    def process_animation(self):
        print("[DEBUG] Processing Animation...")
        onim = self.onim
        anim = get_after_key(onim, "Animation")
        i = 0
        while i < len(anim):
            line = anim[i]
            print(f"[DEBUG] Processing line: {line[0]}")
            if line[0] in ["BonePosition", "BoneRotation"]:
                self.process_bone_anim(anim[i], anim[i + 1])
                i += 1
            elif line[0] in ["ModelPosition", "ModelRotation"]:
                self.process_model_anim(anim[i], anim[i + 1])
                pass
            elif line[0] == "ActionFlags":
                # unhandled
                pass
            elif line[0] == "AudioEvent":
                # unhandled
                pass
            i += 1

    def read_framesdata(self, framesdata_line, data_block):
        # Example:
        #   FramesData SingleChannel Static
        #   {
        #     0.123 0.234 0.345
        #   }
        if framesdata_line == ("FramesData", "SingleChannel", "Static"):
            return [tuple(data_block[0])]

        # Example:
        #   FramesData MultiChannel
        #   {
        #     channel
        #     {
        #       0.123
        #       ...
        #     }
        #     channel
        #     {
        #       0.234
        #       ...
        #     }
        #     ...
        #   }
        elif framesdata_line[1] == "MultiChannel":
            chan_blocks = [
                data_block[i] for i in range(1, len(data_block), 2)
            ]

            # Expand any static (1 frame) channels to full length
            # Example:
            #   channel Static
            #   {
            #     1.0
            #   }
            count = max(len(chan_block) for chan_block in chan_blocks)
            for i in range(len(chan_blocks)):
                if len(chan_blocks[i]) == 1:
                    chan_blocks[i] = [chan_blocks[i][0]] * count

            # They should now be the same length
            assert all(len(chan_block) == count for chan_block in chan_blocks)

            # Channels (eg XYZ) are separated, put them back together
            return [
                tuple(chan_block[i][0] for chan_block in chan_blocks)
                for i in range(count)
            ]

        else:
            assert False, "unknown FramesData format"

    def process_bone_anim(self, target_line, data_block):
        print(f"[DEBUG] Processing Bone Animation for {target_line}")
        anim_type, _, bone_id = target_line
        values = self.read_framesdata(data_block[0], data_block[1])
        bone_name = BoneNameMap[bone_id]
        group_name = bone_name

        if anim_type == "BonePosition":
            data_path = 'pose.bones["%s"].location' % bone_name
            values = self.convert_bone_positions(bone_id, values)

        elif anim_type == "BoneRotation":
            data_path = 'pose.bones["%s"].rotation_quaternion' % bone_name
            values = self.convert_bone_rotations(bone_id, values)

        self.add_fcurves(data_path, values, group_name)

    def process_model_anim(self, target_line, data_block):
        # Note: not tested

        anim_type, _, _ = target_line
        values = self.read_framesdata(data_block[0], data_block[1])

        if anim_type == "ModelPosition":
            data_path = "location"
            group_name = "Location"

        elif anim_type == "ModelRotation":
            data_path = "rotation_quaternion"
            values = self.convert_model_rotations(values)
            group_name = "Rotation"

        self.add_fcurves(data_path, values, group_name)

    def convert_bone_positions(self, bone_id, values):
        # Note: not tested

        # Blender bones are relative to the bind pose / edit bone
        #   Final = EditBone @ PoseBone
        # We have Final, we need to find PoseBone
        bone_name = BoneNameMap[bone_id]
        bind_loc, bind_rot = self.bind_pose[bone_name]
        bind_rot_inv = bind_rot.inverted()
        return [
            bind_rot_inv @ (Vector(v) - bind_loc)
            for v in values
        ]

    def convert_bone_rotations(self, bone_id, values):
        # Quaternion convention xyzw -> wxyz
        values = [
            Quaternion((v[3], v[0], v[1], v[2]))
            for v in values
        ]

        # Blender bones are relative to the bind pose / edit bone
        #   Final = EditBone @ PoseBone
        # We have Final, we need to find PoseBone
        bone_name = BoneNameMap[bone_id]
        _bind_loc, bind_rot = self.bind_pose[bone_name]
        bind_rot_inv = bind_rot.inverted()
        return [
            bind_rot_inv @ v
            for v in values
        ]

    def convert_model_rotations(self, values):
        # Note: not tested

        # Quaternion convention xyzw -> wxyz
        return [
            Quaternion((v[3], v[0], v[1], v[2]))
            for v in values
        ]

    def add_fcurves(self, data_path, values, group_name):
        print(f"[DEBUG] Adding fcurves to {data_path} with {len(values)} values.")
        pts = [0] * (2 * len(values))
        keyframe_times = (i * self.dt for i in range(len(values)))
        pts[0::2] = keyframe_times

        n = len(values[0])
        for index in range(n):
            fcurve = self.action.fcurves.new(
                data_path=data_path,
                index=index,
                action_group=group_name,
            )

            pts[1::2] = (v[index] for v in values)
            fcurve.keyframe_points.add(len(values))
            fcurve.keyframe_points.foreach_set("co", pts)
            fcurve.update()  # Update the F-Curve after adding keyframes
