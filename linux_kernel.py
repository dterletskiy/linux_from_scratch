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
import getopt
import argparse
import re



MIN_PYTHON = (3, 8)
if sys.version_info < MIN_PYTHON:
   print( "Python minimal required version is %s.%s" % MIN_PYTHON )
   print( "Current version is %s.%s" % ( sys.version_info.major, sys.version_info.minor ) )
   sys.exit( )



class ApplicationData:
   def info( self, **kwargs ):
      print( self.__class__.__name__, ":" )
      print( "   config:      \'", self.config, "\'" )
      print( "   includes:    \'", self.includes, "\'" )
      print( "   arch:        \'", self.arch, "\'" )
      print( "   actions:     \'", self.actions, "\'" )
      print( "   projects:    \'", self.projects, "\'" )
      print( "   targets:     \'", self.targets, "\'" )
   # def info

   config: str = None
   includes: list = [ ]
   arch: str = None
   actions: list = [ ]
   projects: list = [ ]
   targets: list = [ ]
# class ApplicationData




class Description:
   help = "Show this help menu."
   config = "Configuration"
   include = "Additional directory to search import packages"
   arch = "Architecture"
   action = "Action"
   project = "Project"
   target = "Target"
# class Description
g_description = Description( )



def cmdline_argparse( argv ):
   print( "Number of arguments:", len(sys.argv) )
   print( "Argument List:", str(sys.argv) )

   application_data = ApplicationData( )

   parser = argparse.ArgumentParser( description = 'App description' )

   parser.add_argument( "--version", action = "version", version = '%(prog)s 2.0' )

   parser.add_argument( "--config", dest = "config", type = str, action = "store", required = False, help = g_description.config )

   parser.add_argument( "--include", dest = "include", type = str, action = "append", help = g_description.include )

   parser.add_argument( "--arch", dest = "arch", type = str, action = "store", required = False, help = g_description.arch )
   parser.add_argument( "--action", dest = "action", type = str, action = "store", required = False, help = g_description.action )
   parser.add_argument( "--project", dest = "project", type = str, action = "store", required = False, help = g_description.project )
   parser.add_argument( "--target", dest = "target", type = str, action = "store", required = False, help = g_description.target )

   # parser.print_help( )
   try:
      argument = parser.parse_args( )
   except argparse.ArgumentError:
      print( 'Catching an ArgumentError' )

   if argument.config:
      print( "config: ", argument.config )
      application_data.config = argument.config

   if argument.include:
      print( "include: ", argument.include )
      application_data.includes.extend( argument.include )

   if argument.arch:
      print( "arch: ", argument.arch )
      application_data.arch = argument.arch

   if argument.action:
      print( "action: ", argument.action )
      application_data.actions = argument.action.split( "," )

   if argument.project:
      print( "project: ", argument.project )
      application_data.projects = argument.project.split( "," )

   if argument.target:
      print( "target: ", argument.target )
      application_data.targets = argument.target.split( "," )

   return application_data
# def cmdline_argparse

g_app_data = cmdline_argparse( sys.argv[1:] )
g_app_data.info( )



def configure( app_data ):
   if None != app_data.config:
      global_variables = globals( )

      pattern: str = r"^\s*(.*)\s*:\s*(.*)\s*$"
      config_file = open( app_data.config, "r" )
      for line in config_file:
         match = re.match( pattern, line )
         if match:
            var_name = match.group( 1 )
            var_value = match.group( 2 )
            if "INCLUDE" == var_name:
               app_data.includes.append( var_value )
            else:
               global_variables.__setitem__( var_name, var_value )
      config_file.close( )



   include_count: int = 0
   for path in app_data.includes:
      include_count += 1
      sys.path.insert( include_count, path )
# def configure
configure( g_app_data )



import pfw.console
import pfw.shell
import pfw.size
import pfw.image

import base
import configuration
import dt
import tools
import linux.base
import linux.uboot
import linux.buildroot
import linux.busybox
import linux.kernel
import linux.tools
import aosp.base
import aosp.aosp
import aosp.tools



ENVIRONMENT = dict( os.environ )
ENVIRONMENT["LFS_VERSION"] = str(1.0)
pfw.shell.run_and_wait_with_status( "/bin/echo ${LFS_VERSION}", env = ENVIRONMENT, shell = True )



# Next variables must be defined in configuration file:
configuration.LINUX_ROOT_DIR: str = LINUX_ROOT_DIR
configuration.KERNEL_VERSION: str = KERNEL_VERSION
configuration.BUSYBOX_VERSION: str = BUSYBOX_VERSION
configuration.BUILDROOT_VERSION: str = BUILDROOT_VERSION
configuration.UBOOT_VERSION: str = UBOOT_VERSION
configuration.ANDROID_ROOT_DIR: str = ANDROID_ROOT_DIR
configuration.ANDROID_VERSION: str = ANDROID_VERSION
configuration.UBOOT_SCRIPT: str = UBOOT_SCRIPT
configuration.SYSLINUX_SCRIPT: str = SYSLINUX_SCRIPT
configuration.DTB_PATH: str = DTB_PATH
configuration.ANDROID_BOOTCONFIG_X86: str = ANDROID_BOOTCONFIG_X86
configuration.ANDROID_BOOTCONFIG_ARM64: str = ANDROID_BOOTCONFIG_ARM64
configuration.TMP_PATH: str = TMP_PATH
configuration.init( )
configuration.print( )







def init_projects( arch: str ):
   linux_configuration: linux.base.Configuration = linux.base.config[ arch ]
   aosp_configuration: aosp.base.Configuration = aosp.base.config[ arch ]

   projects_map: dict = {
      "u-boot"       : linux.uboot.UBoot(
                           linux_configuration,
                           configuration.LINUX_ROOT_DIR,
                           version = UBOOT_VERSION,
                        ),
      "buildroot"    : linux.buildroot.BuildRoot(
                           linux_configuration,
                           configuration.LINUX_ROOT_DIR,
                           version = BUILDROOT_VERSION
                        ),
      "busybox"      : linux.busybox.BusyBox(
                           linux_configuration,
                           configuration.LINUX_ROOT_DIR,
                           version = BUSYBOX_VERSION
                        ),
      "kernel"       : linux.kernel.Kernel(
                           linux_configuration,
                           configuration.LINUX_ROOT_DIR,
                           version = KERNEL_VERSION
                        ),
      "aosp"         : aosp.aosp.AOSP(
                           aosp_configuration,
                           ANDROID_ROOT_DIR,
                           tag = ANDROID_VERSION
                        ),
   }

   return projects_map
# def init_projects

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

def main( app_data: ApplicationData ):
   projects_map = init_projects( app_data.arch )
   actions_map = init_actions( )

   projects: list = [ ]
   for project in app_data.projects:
      if "all" == project:
         projects = projects_map.values( )
         break
      projects.append( projects_map[ project ] )

   actions: list = [ ]
   for action in app_data.actions:
      # Processing extended actions
      if "gdb" == action:
         tools.debug( projects_map, project_name = "u-boot" )
         sys.exit( )
      elif "start" == action:
         tools.start(
               projects_map,
               configuration.LINUX_IMAGE_DRIVE,
               bios = True,
               # gdb = True
            )
         sys.exit( )
      elif "mkimage" == action:
         tools.mkdrive( projects_map, configuration.LINUX_IMAGE_DRIVE )
         sys.exit( )
      else:
         # Collecting standart actions
         actions.extend( actions_map[ action ] )

   targets: list = app_data.targets



   for project in projects:
      kw: dict = { }
      if type( project ) == type( projects_map["kernel"] ):
         kw["configs"] = {
               # "CONFIG_CMDLINE": "\"console=ttyAMA0\"",
               # "CONFIG_INITRAMFS_SOURCE": "\"" + projects["buildroot"].dirs( ).product( "rootfs.cpio" ) + "\"",
            }
      elif type( project ) == type( projects_map["buildroot"] ) or type( project ) == type( projects_map["busybox"] ):
         if "arm" == project.config( ).arch( ):
            kernel_file = "zImage"
         elif "arm64" == project.config( ).arch( ) or "aarch64" == project.config( ).arch( ):
            kernel_file = "Image"
         kw["kernel"] = os.path.join( projects_map["kernel"].dirs( ).product( ), kernel_file )
      elif type( project ) == type( projects_map["aosp"] ):
         kw["image"] = configuration.ANDROID_IMAGE_DRIVE.file( )
         # kw["image"] = projects_map["aosp"].dirs( ).experimental( "main.img" )
         kw["uboot"] = projects_map["u-boot"].dirs( ).product( "u-boot" )
      project.action( actions = actions, targets = targets, **kw )


# def main



if __name__ == "__main__":
   main( g_app_data )

   pfw.console.debug.error( "----- END -----" )
