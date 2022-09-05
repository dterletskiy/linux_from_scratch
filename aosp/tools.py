#!/usr/bin/python3

import os
import subprocess

import pfw.console
import pfw.shell
import pfw.size
import pfw.image



def mkimage( projects_map: dict ):
   # Preparing u-images
   project_aosp = projects_map["aosp"]
   mkimage_tool = projects_map["u-boot"].mkimage

   uimg_dir = project_aosp.dirs( ).experimental( "uimg" )
   pfw.shell.run_and_wait_with_status( f"mkdir -p {uimg_dir}", output = pfw.shell.eOutput.PTY )

   mkimage_tool(
           project_aosp.dirs( ).product( "kernel" ), "kernel"
         , compression = "none", load_addr = "0x50000000"
         , destination = os.path.join( uimg_dir, "kernel.uimg" )
      )
   mkimage_tool(
           project_aosp.dirs( ).experimental( "ramdisk" ), "ramdisk"
         , compression = "none", load_addr = "0x54000000"
         , destination = os.path.join( uimg_dir, "ramdisk.uimg" )
      )
   mkimage_tool(
           project_aosp.dirs( ).experimental( "dtb.dtb" ), "flat_dt"
         , compression = "none", load_addr = "0x57000000"
         , destination = os.path.join( uimg_dir, "dtb.dtb.uimg" )
      )
   mkimage_tool(
           project_aosp.dirs( ).root( "configuration/boot.cmd" ), "script"
         , compression = "none", load_addr = "0x58000000"
         , destination = os.path.join( uimg_dir, "boot.scr.uimg" )
      )
# def mkimage

def deploy( projects_map: dict, mount_point: str, pause: bool = False ):
   project_aosp = projects_map["aosp"]
   uimg_dir = project_aosp.dirs( ).experimental( "uimg" )

   files_list: list = [
         # {
         #    "src": project_aosp.dirs( ).product( "kernel" ),
         #    "dest": os.path.join( mount_point, "boot/kernel" )
         # },
         # {
         #    "src": os.path.join( uimg_dir, "kernel.uimg" ),
         #    "dest": os.path.join( mount_point, "boot/kernel.uimg" )
         # },
         # {
         #    "src": project_aosp.dirs( ).experimental( "ramdisk" ),
         #    "dest": os.path.join( mount_point, "boot/ramdisk" )
         # },
         # {
         #    "src": os.path.join( uimg_dir, "ramdisk.uimg" ),
         #    "dest": os.path.join( mount_point, "boot/ramdisk.uimg" )
         # },
         {
            "src": project_aosp.dirs( ).experimental( "dtb.dtb" ),
            "dest": os.path.join( mount_point, "boot/dtb.dtb" )
         },
         # {
         #    "src": os.path.join( uimg_dir, "dtb.dtb.uimg" ),
         #    "dest": os.path.join( mount_point, "boot/dtb.dtb.uimg" )
         # },
         {
            "src": os.path.join( uimg_dir, "boot.scr.uimg" ),
            "dest": os.path.join( mount_point, "boot/boot.scr.uimg" )
         },
         # {
         #    "src": project_aosp.dirs( ).root( "configuration/extlinux.conf" ),
         #    "dest": os.path.join( mount_point, "boot/extlinux/extlinux.conf" )
         # },
         {
            "src": project_aosp.dirs( ).experimental( "boot.img" ),
            "dest": os.path.join( mount_point, "boot/boot.img" )
         },
         # {
         #    "src": os.path.join( uimg_dir, "boot.img.uimg" ),
         #    "dest": os.path.join( mount_point, "boot/boot.img.uimg" )
         # },
      ]

   for item in files_list:
      if False == os.path.exists( item["src"] ):
         pfw.console.debug.warning( "file does not exist: ", item["src"] )
         continue
      pfw.shell.run_and_wait_with_status( "sudo mkdir -p " + os.path.dirname( item["dest"] ), output = pfw.shell.eOutput.PTY )
      pfw.console.debug.trace( "file: '%s' ->\n     '%s'" % ( item["src"], item["dest"] ) )
      pfw.shell.run_and_wait_with_status( f"sudo cp " + item["src"] + " " + item["dest"], output = pfw.shell.eOutput.PTY )

   subprocess.Popen(['xdg-open', mount_point])
   pfw.console.debug.promt( )
# def deploy

def mkdrive( projects_map: dict, image_description: pfw.image.Description ):
   partitions = [
      pfw.image.Drive.Partition( size = pfw.size.Size( 512, pfw.size.Size.eGran.M ), fs = image_description.fs( ) ),
   ]

   mmc: pfw.image.Drive = pfw.image.Drive( image_description.file( ) )
   mmc.create( partitions = partitions, force = True )
   mmc.attach( )
   mmc.init( partitions, bootable = 1 )
   mmc.mount( 1, image_description.mount_point( ) )

   mkimage( projects_map )
   deploy( projects_map, image_description.mount_point( ), pause = True )

   mmc.info( )
   mmc.detach( )
# def mkdrive





def build_main_image( projects_map: dict, **kwargs ):
   project_aosp = projects_map["aosp"]

   # project_aosp.build_ramdisk( )

   # project_aosp.extract_android_boot_image( )

   cmdline = "loglevel=7 debug printk.devkmsg=on drm.debug=0x0 console=ttyAMA0 earlyprintk=ttyAMA0"
   cmdline += " root=/dev/ram rw"
   cmdline += " loop.max_loop=10"
   project_aosp.create_android_boot_image(
         header_version = 2,
         kernel = project_aosp.dirs( ).product( "kernel"),
         ramdisk = project_aosp.dirs( ).experimental( "ramdisk"),
         dtb = project_aosp.dirs( ).experimental( "dtb.dtb"),
         cmdline = cmdline
      )

   # project_aosp.build_main_image( )
# def build_main_image
