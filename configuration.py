import os
import re
from enum import IntEnum

import pfw.console



# Next variables must be defined in configuration file:
# LINUX_ROOT_DIR: str = None
# KERNEL_VERSION: str = None
# BUSYBOX_VERSION: str = None
# BUILDROOT_VERSION: str = None
# UBOOT_VERSION: str = None

# ANDROID_ROOT_DIR: str = None
# ANDROID_VERSION: str = None

# UBOOT_SCRIPT: str = None
# SYSLINUX_SCRIPT: str = None
# DTB_PATH: str = None

# ANDROID_BOOTCONFIG_X86: str = None
# ANDROID_BOOTCONFIG_ARM64: str = None

# TMP_PATH: str = None



LINUX_IMAGE_PARTITION: pfw.image.Description = None
LINUX_IMAGE_DRIVE: pfw.image.Description = None

ANDROID_IMAGE_DRIVE: pfw.image.Description = None



def init( variables: dict = { } ):
   global_variables = globals( )
   global_variables.update( variables )

   global LINUX_IMAGE_PARTITION
   LINUX_IMAGE_PARTITION = pfw.image.Description(
           os.path.join( TMP_PATH, "partition_linux.img" )
         , os.path.join( TMP_PATH, "partition_linux" )
         , pfw.size.Size( 256, pfw.size.Size.eGran.M )
         , "ext2"
      )
   global LINUX_IMAGE_DRIVE
   LINUX_IMAGE_DRIVE = pfw.image.Description(
           os.path.join( TMP_PATH, "drive_linux.img" )
         , os.path.join( TMP_PATH, "drive_linux" )
         , pfw.size.Size( 256, pfw.size.Size.eGran.M )
         , "ext2"
      )

   global ANDROID_IMAGE_DRIVE
   ANDROID_IMAGE_DRIVE = pfw.image.Description(
           os.path.join( TMP_PATH, "drive_aosp.img" )
         , os.path.join( TMP_PATH, "drive_aosp" )
         , pfw.size.Size( 256, pfw.size.Size.eGran.M )
         , "fat32"
      )

   info( )
   return True
# def init



def info( ):
   print( "LINUX_ROOT_DIR:             ", LINUX_ROOT_DIR )
   print( "KERNEL_VERSION:             ", KERNEL_VERSION )
   print( "BUSYBOX_VERSION:            ", BUSYBOX_VERSION )
   print( "BUILDROOT_VERSION:          ", BUILDROOT_VERSION )
   print( "UBOOT_VERSION:              ", UBOOT_VERSION )

   print( "ANDROID_ROOT_DIR:           ", ANDROID_ROOT_DIR )
   print( "ANDROID_VERSION:            ", ANDROID_VERSION )

   print( "UBOOT_SCRIPT:               ", UBOOT_SCRIPT )
   print( "SYSLINUX_SCRIPT:            ", SYSLINUX_SCRIPT )
   print( "DTB_PATH:                   ", DTB_PATH )

   print( "ANDROID_BOOTCONFIG_X86:     ", ANDROID_BOOTCONFIG_X86 )
   print( "ANDROID_BOOTCONFIG_ARM64:   ", ANDROID_BOOTCONFIG_ARM64 )

   print( "TMP_PATH:                   ", TMP_PATH )

   print( "LINUX_IMAGE_DRIVE:          ", LINUX_IMAGE_DRIVE )
   print( "ANDROID_IMAGE_DRIVE:        ", ANDROID_IMAGE_DRIVE )
