# BlendIV-OFIO
A WIP Grand Theft Auto IV OpenFormats importer addon for Blender, with just limited (buggy) oad/onim support, originally written by scurest and uploaded here with permission, tested with Blender 2.9.

![alt text](https://images-ext-1.discordapp.net/external/6oB0et_HVv3C9OdhfqwmeANJ0hineDFabCMfJp8qNPU/https/repository-images.githubusercontent.com/632805563/e891452a-bef3-41c8-ad82-c49d212d10e9?width=932&height=417)

How to Install:

1. Click the "Code" dropdown on Github, download zip, do NOT unzip it
2. In Blender, go to Edit > Preferences... > Addons tab, select "install" and install the zip.

scurest's own readme modified below:

Buggy Blender Importer for GTA IV .oad/.onim files

Instructions:

1. Install and enable addon.
2. Select armature in Object Mode.
3. File > Import > GTA IV Anim.
4. Select .oad or .onim file.
5. Look for imported animations in the NLA editor. Star a track to see it play.

Current issues involving "floaty" animations may or may not have something to do with the nature of IK in the GTA IV animations.
An issue with "foretwist" bones being unanimated are expected as there may be certain flags in the animation that would normally move the foretwist with the forearm bones as if it were their parent in-game. 
