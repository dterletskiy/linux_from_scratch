#!/usr/bin/python3

import os
import sys
import getopt
import argparse



MIN_PYTHON = (3, 8)
if sys.version_info < MIN_PYTHON:
   print( "Python minimal required version is %s.%s" % MIN_PYTHON )
   print( "Current version is %s.%s" % ( sys.version_info.major, sys.version_info.minor ) )
   sys.exit( )



class ApplicationData:
   def info( self, **kwargs ):
      print( self.__class__.__name__, ":" )
      print( "   includes:    \'", self.includes, "\'" )
      print( "   arch:        \'", self.arch, "\'" )
      print( "   actions:     \'", self.actions, "\'" )
      print( "   projects:    \'", self.projects, "\'" )
      print( "   targets:     \'", self.targets, "\'" )
   # def info

   includes: list = [ ]
   arch: str = None
   actions: list = [ ]
   projects: list = [ ]
   targets: list = [ ]
# class ApplicationData




class Description:
   help = "Show this help menu."
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



LINUX_ROOT_DIR: str = "/mnt/dev/linux_from_scratch/"
KERNEL_VERSION: str = "5.19"
BUSYBOX_VERSION: str = "1.35.0"
BUILDROOT_VERSION: str = "2022.05.2"
UBOOT_VERSION: str = "v2022.07"

ANDROID_ROOT_DIR = "/mnt/dev/android/"
ANDROID_VERSION="android-12.1.0_r8"







LINUX_IMAGE_DIR: str = os.path.join( LINUX_ROOT_DIR, "images" )
LINUX_IMAGE_PARTITION: pfw.image.Description = pfw.image.Description(
        os.path.join( LINUX_IMAGE_DIR, "partition.img" )
      , os.path.join( LINUX_IMAGE_DIR, "partition" )
      , pfw.size.Size( 256, pfw.size.Size.eGran.M )
      , "ext2"
   )
LINUX_IMAGE_DRIVE: pfw.image.Description = pfw.image.Description(
        os.path.join( LINUX_IMAGE_DIR, "drive.img" )
      , os.path.join( LINUX_IMAGE_DIR, "drive" )
      , pfw.size.Size( 256, pfw.size.Size.eGran.M )
      , "ext2"
   )



ANDROID_IMAGE_DIR: str = os.path.join( ANDROID_ROOT_DIR, "images" )
ANDROID_IMAGE_DRIVE: pfw.image.Description = pfw.image.Description(
        os.path.join( ANDROID_IMAGE_DIR, "drive.img" )
      , os.path.join( ANDROID_IMAGE_DIR, "drive" )
      , pfw.size.Size( 256, pfw.size.Size.eGran.M )
      , "fat32"
   )



def init_projects( arch: str ):
   linux_configuration: linux.base.Configuration = linux.base.config[ arch ]
   aosp_configuration: aosp.base.Configuration = aosp.base.config[ arch ]

   projects_map: dict = {
      "u-boot"       : linux.uboot.UBoot( linux_configuration, LINUX_ROOT_DIR, version = UBOOT_VERSION, url = linux.uboot.UBOOT_GITHUB_REPO ),
      "buildroot"    : linux.buildroot.BuildRoot( linux_configuration, LINUX_ROOT_DIR, version = BUILDROOT_VERSION ),
      "busybox"      : linux.busybox.BusyBox( linux_configuration, LINUX_ROOT_DIR, version = BUSYBOX_VERSION ),
      "kernel"       : linux.kernel.Kernel( linux_configuration, LINUX_ROOT_DIR, version = KERNEL_VERSION ),
      "aosp"         : aosp.aosp.AOSP( aosp_configuration, ANDROID_ROOT_DIR, tag = ANDROID_VERSION ),
      "u-boot-aosp"  : linux.uboot.UBoot( linux_configuration, ANDROID_ROOT_DIR, version = "master", url = linux.uboot.UBOOT_ANDROID_GOOGLESOURCE_REPO ),
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
         debug: str = "u-boot"
         if "u-boot" == debug:
            project = projects_map["u-boot"]
            tools.gdb(
                  # arch = project.config( ).arch( ),
                  file = project.dirs( ).product( "u-boot" ),
                  # lib_path = os.path.join( project.config( ).compiler_path( ), "lib" ),
                  # src_path = project.dirs( ).source( ),
                  # rellocate_offset = 0x23ff0d000, # u-boot-aosp
                  rellocate_offset = 0x23ff1b000, # u-boot
                  break_names = [
                     # "do_bootm",
                     # "do_bootm_states",
                     # "bootm_find_other",
                     # "bootm_find_images",
                     # "boot_get_ramdisk",
                     # "select_ramdisk",
                     "boot_jump_linux",
                     "armv8_switch_to_el2"
                  ],
                  none = None
               )
         elif "kernel" == debug:
            project = projects_map["kernel"]
            tools.gdb(
                  # arch = project.config( ).arch( ),
                  file = project.dirs( ).build( "vmlinux" ),
                  break_names = [
                     "primary_entry",
                     "__primary_switch",
                     "__primary_switched",
                     "start_kernel",
                     "rest_init",
                     "cpu_startup_entry"
                  ],
                  ex_list = [
                     # f"add-auto-load-safe-path {project.dirs( ).build( )}",
                     # f"add-auto-load-safe-path " + project.dirs( ).source( "scripts/gdb/vmlinux-gdb.py" ),
                     # f"source {project.dirs( ).build( 'vmlinux-gdb.py' )}",
                  ],
                  none = None
               )

         sys.exit( )
      elif "start" == action:
         dt_path = "/mnt/dev/linux/configuration/"
         dtb_name = "dtb"
         dtb = f"{dt_path}/{dtb_name}.dtb"
         dts = f"{dt_path}/{dtb_name}.dts"

         # dt.decompile( dtb, dts )
         # dt.compile( dts, dtb )

         tools.run_arm64(
               bios = projects_map["u-boot"].dirs( ).product( "u-boot.bin" ),
               # kernel = projects_map["kernel"].dirs( ).deploy( "Image" ),
               # initrd = projects_map["buildroot"].dirs( ).deploy( "rootfs.cpio" ),
               # append = "loglevel=7 debug printk.devkmsg=on drm.debug=0x0 console=ttyAMA0",
               # dtb = dtb,
               drive = LINUX_IMAGE_DRIVE.file( ),
               # dump_dtb = True, dump_dtb_path = dtb,
               # gdb = True
            )

         sys.exit( )
      elif "mkimage" == action:
         tools.mkdrive( projects_map, LINUX_IMAGE_DRIVE, LINUX_ROOT_DIR )

         sys.exit( )
      else:
         # Collecting standart actions
         actions.extend( actions_map[ action ] )

   targets: list = app_data.targets



   for project in projects:
      kw: dict = { }
      if type( project ) == type( projects_map["kernel"] ):
         kw["configs"] = {
               "CONFIG_CMDLINE": "\"console=ttyAMA0\"",
               # "CONFIG_INITRAMFS_SOURCE": "\"" + projects["buildroot"].dirs( ).product( "rootfs.cpio" ) + "\"",
            }
      elif type( project ) == type( projects_map["buildroot"] ) or type( project ) == type( projects_map["busybox"] ):
         # kernel_file: str = ""
         if "arm" == project.config( ).arch( ):
            kernel_file = "zImage"
         elif "arm64" == project.config( ).arch( ) or "aarch64" == project.config( ).arch( ):
            kernel_file = "Image"
         kw["kernel"] = os.path.join( projects_map["kernel"].dirs( ).product( ), kernel_file )
      elif type( project ) == type( projects_map["aosp"] ):
         kw["image"] = ANDROID_IMAGE_DRIVE.file( )
         # kw["image"] = projects_map["aosp"].dirs( ).experimental( "main.img" )
         kw["uboot"] = projects_map["u-boot"].dirs( ).product( "u-boot" )
         # kw["uboot"] = projects_map["u-boot-aosp"].dirs( ).product( "u-boot" )
      project.action( actions = actions, targets = targets, **kw )


# def main



if __name__ == "__main__":
   main( g_app_data )

   pfw.console.debug.error( "----- END -----" )
