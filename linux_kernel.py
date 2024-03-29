#!/usr/bin/python3



# Examples:
# 
# CONFIG=./configuration.cfg
# PROJECT=u-boot
# ARCH=arm64
# PFW=/mnt/dev/TDA/python_fw
# 
# ./linux_kernel.py --config=${CONFIG} --include=${PFW} --project=${PROJECT} --action=info
# ./linux_kernel.py --config=${CONFIG} --include=${PFW} --project=${PROJECT} --action=sync
# ./linux_kernel.py --config=${CONFIG} --include=${PFW} --project=${PROJECT} --action=clean
# ./linux_kernel.py --config=${CONFIG} --include=${PFW} --project=${PROJECT} --action=config
# ./linux_kernel.py --config=${CONFIG} --include=${PFW} --project=${PROJECT} --action=config --target=menuconfig
# ./linux_kernel.py --config=${CONFIG} --include=${PFW} --project=${PROJECT} --action=build
# ./linux_kernel.py --config=${CONFIG} --include=${PFW} --project=${PROJECT} --action=deploy
# 
# ./linux_kernel.py --config=${CONFIG} --include=${PFW} --action=mkimage
# ./linux_kernel.py --config=${CONFIG} --include=${PFW} --action=start
# ./linux_kernel.py --config=${CONFIG} --include=${PFW} --action=gdb
# 
# In case if variable "INCLUDE" defined with path to "pfw" "--include" option could be omitted.
# If "INCLUDE" variable defined several times in configuration file all mentioned values will be used.



import os
import sys
import subprocess
import copy

import configuration



##########################################################################
#                                                                        #
#                          Begin configuration                           #
#                                                                        #
##########################################################################

MIN_PYTHON = (3, 8)
if sys.version_info < MIN_PYTHON:
   print( "Python minimal required version is %s.%s" % MIN_PYTHON )
   print( "Current version is %s.%s" % ( sys.version_info.major, sys.version_info.minor ) )
   sys.exit( )



configuration.configure( sys.argv[1:] )



import pfw.console
import pfw.shell
import pfw.size
import pfw.linux.image
import pfw.linux.image2
import pfw.os.signal
import pfw.linux.ping
import pfw.linux.ramdisk

import base
import tools
import docker.container
import qemu
import antlr
import ubuntu
import signal
import linux.base
import linux.uboot
import linux.buildroot
import linux.busybox
import linux.kernel
import linux.rootfs
import linux.xen
import linux.qemu
import aosp.base
import aosp.aosp



def extend_configuration( ):
   configuration.config.set_value( "boot_partition_image",
      pfw.linux.image2.Partition.Description(
           file = os.path.join( configuration.config.get_value( "tmp_path" ), "boot.img" )
         , size = pfw.size.Size( 512, pfw.size.Size.eGran.M )
         , fs = "ext2"
      )
   )
   configuration.config.set_value( "rootfs_partition_image",
      pfw.linux.image2.Partition.Description(
           file = os.path.join( configuration.config.get_value( "tmp_path" ), "rootfs.img" )
         , size = pfw.size.Size( 5, pfw.size.Size.eGran.G )
         , fs = "ext4"
      )
   )
   configuration.config.set_value( "main_drive_image", os.path.join( configuration.config.get_value( "tmp_path" ), "main.img" ) )
   configuration.config.set_value( "device_0_image", os.path.join( configuration.config.get_value( "tmp_path" ), "device_0.img" ) )
   configuration.config.set_value( "device_1_image", os.path.join( configuration.config.get_value( "tmp_path" ), "device_1.img" ) )
# def extend_configuration

extend_configuration( )


qemu.init( configuration.config.get_value( "qemu_path" ) )
antlr.init( configuration.config.get_value( "antlr_jar" ) )
antlr.gen_grammar( lexers = configuration.config.get_values( "antlr_lexer" ), parsers = configuration.config.get_values( "antlr_parser" ) )



import generator.pdl.parser



ENVIRONMENT = dict( os.environ )
ENVIRONMENT["LFS_VERSION"] = str(1.0)
pfw.shell.execute( "/bin/echo ${LFS_VERSION}", env = ENVIRONMENT, shell = True )



##########################################################################
#                                                                        #
#                           End configuration                            #
#                                                                        #
##########################################################################









def init_actions( ):
   actions_map: dict = {
      "info"         : [ base.eAction.info ],
      "sync"         : [ base.eAction.sync ],
      "clean"        : [ base.eAction.clean ],
      "config"       : [ base.eAction.config ],
      "build"        : [ base.eAction.build ],
      "deploy"       : [ base.eAction.deploy ],
      "mkall"        : [ base.eAction.info, base.eAction.clean, base.eAction.config, base.eAction.build, base.eAction.deploy ],
      "run"          : [ base.eAction.run ],
      "run_debug"    : [ base.eAction.run_debug ],
      "run_gdb"      : [ base.eAction.run_gdb ],
   }

   return actions_map
# def init_actions

def main( ):
   projects_map = generator.pdl.parser.parse( configuration.value( "pdl" ) )
   actions_map = init_actions( )



   actions: list = None
   action_name = configuration.value( "action" )
   if None == action_name:
      pfw.console.debug.error( "undefined --action parameter" )
      sys.exit( 253 )

   project = None
   project_name: str = configuration.value( "project" )
   if None != project_name:
      project = projects_map[ project_name ]

   targets: list = configuration.values( "target" )



   if None != project:
      actions = actions_map[ action_name ]
      kw: dict = { }
      project.action( actions = actions, targets = targets, **kw )

   else:
      if "gdb" == action_name:
         tools.debug( projects_map, project_name = "uboot" )
      elif "start" == action_name:
         if "aosp-uboot" == targets[0]:
            tools.start( projects_map, mode = "aosp-uboot", arch = "arm64", gdb = False )
         elif "aosp-kernel" == targets[0]:
            tools.start( projects_map, mode = "aosp-kernel", arch = "arm64", gdb = False )
         else:
            tools.start( projects_map, mode = "u-boot", gdb = False )
            tools.start( projects_map, mode = "kernel_rd", gdb = False )
            tools.start( projects_map, mode = "kernel_rf", gdb = False )
      elif "mkimage" == action_name:
         tools.mkdrive( projects_map )
      elif "docker" == action_name:
         if "ubuntu_x86_64" == targets[0]:
            container = docker.container.build(
                  image = "ubuntu:20.04",
                  name = "ubuntu-20.04-x86_64",
                  packages = ubuntu.packages_all
               )
            # docker.container.commit( container, image = "ubuntu/x86_64:20.04" )
         elif "ubuntu_arm64v8" == targets[0]:
            container = docker.container.build(
                  image = "arm64v8/ubuntu:20.04",
                  name = "ubuntu-20.04-arm64v8",
                  packages = ubuntu.packages_all
               )
            # docker.container.commit( container, image = "ubuntu/arm64v8:20.04" )
         elif "prune" == action_name:
            pfw.linux.docker2.prune( )
      elif "dummy" == action_name:

         # projects_map["aosp"].extract_android_boot_image(
         #       boot_img = "/mnt/dev/android/deploy/kernel/common-android14-6.1/virtual_device_aarch64/boot.img",
         #       out = "/mnt/dev/android/deploy/kernel/common-android14-6.1/virtual_device_aarch64/extracted/boot.img",
         #       format = "mkbootimg"
         #    )

         # pfw.linux.ramdisk.extract(
         #       source = "/mnt/dev/android/deploy/kernel/common-android14-6.1/virtual_device_aarch64/initramfs.img",
         #       destination = "/mnt/dev/android/deploy/kernel/common-android14-6.1/virtual_device_aarch64/extracted/initramfs.img",
         #    )

         projects_map["aosp"].extract_android_boot_image(
               boot_img = projects_map["aosp"].dirs( ).product( "boot.img" ),
               out = projects_map["aosp"].dirs( ).product( "experimental/extracted/boot.img" ),
               format = "mkbootimg"
            )

         projects_map["aosp"].extract_android_boot_image(
               boot_img = projects_map["aosp"].dirs( ).product( "vendor_boot.img" ),
               out = projects_map["aosp"].dirs( ).product( "experimental/extracted/vendor_boot.img" ),
               format = "mkbootimg"
            )

         pfw.linux.ramdisk.extract(
               source = projects_map["aosp"].dirs( ).product( "experimental/extracted/boot.img/ramdisk" ),
               destination = projects_map["aosp"].dirs( ).product( "experimental/extracted/ramdisk" ),
            )

         pfw.linux.ramdisk.extract(
               source = projects_map["aosp"].dirs( ).product( "experimental/extracted/vendor_boot.img/vendor_ramdisk" ),
               destination = projects_map["aosp"].dirs( ).product( "experimental/extracted/vendor_ramdisk" ),
            )




         # ANDROID_PRODUCT_RAMDISK_DIR = projects_map["aosp"].dirs( ).product( "ramdisk" )
         # ANDROID_PRODUCT_VENDOR_RAMDISK_DIR = projects_map["aosp"].dirs( ).product( "vendor_ramdisk" )
         # EXPERIMENTAL_RAMDISK_DIR = projects_map["aosp"].dirs( ).product( "experimental/ramdisk" )
         # EXPERIMENTAL_RAMDISK_IMAGE = projects_map["aosp"].dirs( ).product( "experimental/ramdisk.img" )
         # BOOTCONFIG = configuration.value( "android_bootconfig_arm64" )

         # pfw.linux.ramdisk.pack(
         #       source = ANDROID_PRODUCT_RAMDISK_DIR,
         #       sources = [ ANDROID_PRODUCT_VENDOR_RAMDISK_DIR ],
         #       destination = EXPERIMENTAL_RAMDISK_IMAGE,
         #       bootconfig = BOOTCONFIG
         #    )





         # pfw.linux.imgage.map(
         #       "/mnt/img/tmp/device_0.img",
         #       mount_point = "/mnt/img/tmp/loop/",
         #       processor = lambda: pfw.console.debug.promt( )
         #    )
      elif "ping" == action_name:
         pfw.linux.ping.ping( processor = pfw.linux.ping.processor )

# def main



if __name__ == "__main__":
   pfw.console.debug.ok( "------------------------- BEGIN -------------------------" )
   main( )
   pfw.console.debug.ok( "-------------------------- END --------------------------" )
