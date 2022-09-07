import os
import re
from enum import IntEnum

import pfw.console



INCLUDES: list = [ ]

# Next variables must be defined in configuration file:
LINUX_ROOT_DIR: str = None
KERNEL_VERSION: str = None
BUSYBOX_VERSION: str = None
BUILDROOT_VERSION: str = None
UBOOT_VERSION: str = None

ANDROID_ROOT_DIR: str = None
ANDROID_VERSION: str = None

UBOOT_SCRIPT: str = None
SYSLINUX_SCRIPT: str = None
DTB_PATH: str = None

ANDROID_BOOTCONFIG_X86: str = None
ANDROID_BOOTCONFIG_ARM64: str = None

TMP_PATH: str = None



LINUX_IMAGE_PARTITION: pfw.image.Description = None
LINUX_IMAGE_DRIVE: pfw.image.Description = None

ANDROID_IMAGE_DRIVE: pfw.image.Description = None



def init( ):
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

   return True



def print( ):
   pfw.console.debug.info( "LINUX_ROOT_DIR:             ", LINUX_ROOT_DIR )
   pfw.console.debug.info( "KERNEL_VERSION:             ", KERNEL_VERSION )
   pfw.console.debug.info( "BUSYBOX_VERSION:            ", BUSYBOX_VERSION )
   pfw.console.debug.info( "BUILDROOT_VERSION:          ", BUILDROOT_VERSION )
   pfw.console.debug.info( "UBOOT_VERSION:              ", UBOOT_VERSION )

   pfw.console.debug.info( "ANDROID_ROOT_DIR:           ", ANDROID_ROOT_DIR )
   pfw.console.debug.info( "ANDROID_VERSION:            ", ANDROID_VERSION )

   pfw.console.debug.info( "UBOOT_SCRIPT:               ", UBOOT_SCRIPT )
   pfw.console.debug.info( "SYSLINUX_SCRIPT:            ", SYSLINUX_SCRIPT )
   pfw.console.debug.info( "DTB_PATH:                   ", DTB_PATH )

   pfw.console.debug.info( "ANDROID_BOOTCONFIG_X86:     ", ANDROID_BOOTCONFIG_X86 )
   pfw.console.debug.info( "ANDROID_BOOTCONFIG_ARM64:   ", ANDROID_BOOTCONFIG_ARM64 )

   pfw.console.debug.info( "TMP_PATH:                   ", TMP_PATH )

   pfw.console.debug.info( "LINUX_IMAGE_DRIVE:          ", LINUX_IMAGE_DRIVE )
   pfw.console.debug.info( "ANDROID_IMAGE_DRIVE:        ", ANDROID_IMAGE_DRIVE )
