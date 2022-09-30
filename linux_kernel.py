#!/usr/bin/python3



# Examples:
# 
# CONFIG=./configuration.cfg 
# PROJECT=u-boot
# ARCH=arm64
# PFW=/mnt/dev/TDA/python_fw
# 
# ./linux_kernel.py --config=${CONFIG} --include=${PFW} --arch=${ARCH} --project=${PROJECT} --action=info
# ./linux_kernel.py --config=${CONFIG} --include=${PFW} --arch=${ARCH} --project=${PROJECT} --action=sync
# ./linux_kernel.py --config=${CONFIG} --include=${PFW} --arch=${ARCH} --project=${PROJECT} --action=clean
# ./linux_kernel.py --config=${CONFIG} --include=${PFW} --arch=${ARCH} --project=${PROJECT} --action=config
# ./linux_kernel.py --config=${CONFIG} --include=${PFW} --arch=${ARCH} --project=${PROJECT} --action=config --target=menuconfig
# ./linux_kernel.py --config=${CONFIG} --include=${PFW} --arch=${ARCH} --project=${PROJECT} --action=build
# ./linux_kernel.py --config=${CONFIG} --include=${PFW} --arch=${ARCH} --project=${PROJECT} --action=deploy
# 
# ./linux_kernel.py --config=${CONFIG} --include=${PFW} --arch=${ARCH} --action=mkimage
# ./linux_kernel.py --config=${CONFIG} --include=${PFW} --arch=${ARCH} --action=start
# ./linux_kernel.py --config=${CONFIG} --include=${PFW} --arch=${ARCH} --action=gdb
# 
# In case if variable "INCLUDE" defined with path to "pfw" "--include" option could be omitted.
# If "INCLUDE" variable defined several times in configuration file all mentioned values will be used.



import os
import sys
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
import pfw.image

import base
import dt
import tools
import qemu
import antlr
import linux.base
import linux.uboot
import linux.buildroot
import linux.busybox
import linux.kernel
import linux.xen
import linux.qemu
import aosp.base
import aosp.aosp



def extend_configuration( ):
   configuration.config.set_value( "linux_image_partition",
      pfw.image.Description(
           os.path.join( configuration.config.get_value( "tmp_path" ), "partition.img" )
         , os.path.join( configuration.config.get_value( "tmp_path" ), "partition" )
         , pfw.size.Size( 512, pfw.size.Size.eGran.M )
         , "ext2"
      )
   )
   configuration.config.set_value( "linux_image_drive",
      pfw.image.Description(
           os.path.join( configuration.config.get_value( "tmp_path" ), "drive.img" )
         , os.path.join( configuration.config.get_value( "tmp_path" ), "drive" )
         , pfw.size.Size( 512, pfw.size.Size.eGran.M )
         , "ext2"
      )
   )
# def extend_configuration

extend_configuration( )


qemu.init( configuration.config.get_value( "qemu_path" ) )
antlr.init( configuration.config.get_value( "antlr_jar" ) )
antlr.gen_grammar( lexers = configuration.config.get_values( "antlr_lexer" ), parsers = configuration.config.get_values( "antlr_parser" ) )



import generator.pdl.parser



ENVIRONMENT = dict( os.environ )
ENVIRONMENT["LFS_VERSION"] = str(1.0)
pfw.shell.run_and_wait_with_status( "/bin/echo ${LFS_VERSION}", env = ENVIRONMENT, shell = True )



# configuration.init( g_config_variables )

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

def main( app_data: configuration.ConfigurationContainer ):
   projects_map = generator.pdl.parser.parse( configuration.value( "pdl" ) )
   actions_map = init_actions( )

   projects: list = [ ]
   for project in app_data.get_values( "project" ):
      if "all" == project:
         projects = projects_map.values( )
         break
      projects.append( projects_map[ project ] )

   actions: list = [ ]
   for action in app_data.get_values( "action" ):
      # Processing extended actions
      if "gdb" == action:
         tools.debug( projects_map, project_name = "uboot" )
         sys.exit( )
      elif "start" == action:
         # tools.start_trout(
         tools.start(
               projects_map,
               bios = True,
               # gdb = True
            )

         # projects_map["aosp"].run( debug = True )

         sys.exit( )
      elif "mkimage" == action:
         tools.mkpartition( projects_map )
         tools.mkdrive( projects_map )

         # projects_map["aosp"].build_ramdisk( )
         # projects_map["aosp"].build_main_image( )

         sys.exit( )
      else:
         # Collecting standart actions
         actions.extend( actions_map[ action ] )

   targets: list = app_data.get_values( "target" )



   for project in projects:
      kw: dict = { }
      if type( project ) == type( projects_map["kernel"] ):
         kw["configs"] = {
               # "CONFIG_CMDLINE": "\"console=ttyAMA0\"",
               # "CONFIG_INITRAMFS_SOURCE": "\"" + projects["buildroot"].dirs( ).product( "rootfs.cpio" ) + "\"",
            }
      elif type( project ) == type( projects_map["buildroot"] ) or type( project ) == type( projects_map["busybox"] ):
         if "arm" == project.config( ).arch( ) or "arm32" == project.config( ).arch( ):
            kernel_file = "zImage"
         elif "arm64" == project.config( ).arch( ) or "aarch64" == project.config( ).arch( ):
            kernel_file = "Image"
         kw["kernel"] = os.path.join( projects_map["kernel"].dirs( ).product( ), kernel_file )
      project.action( actions = actions, targets = targets, **kw )


# def main



if __name__ == "__main__":
   main( configuration.config )

   pfw.console.debug.error( "----- END -----" )
