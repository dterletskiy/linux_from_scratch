#!/usr/bin/python3

import os
import subprocess

import pfw.console
import pfw.shell
import pfw.size
import pfw.image

import tools
import linux.base
import linux.uboot
import linux.buildroot
import linux.busybox
import linux.kernel



QEMU_PATH="/mnt/dev/git/qemu/build/"

# u-boot: vexpress_ca9x4_defconfig
# kernel: vexpress_defconfig
# busybox: defconfig
# buildroot: qemu_arm_vexpress_defconfig
def run_vexpress_ca9x4( projects_map: dict, **kwargs ):
   kw_partition = kwargs.get( "partition", None )
   kw_drive = kwargs.get( "drive", None )

   command: str = None
   parameters: list = [ ]

   command = f"{QEMU_PATH}qemu-system-arm"
   parameters.append( "-machine vexpress-a9" )
   parameters.append( "-nographic" )
   parameters.append( "-smp 1" )
   parameters.append( "-m 256M" )
   parameters.append( "-kernel " + os.path.join( projects_map["u-boot"].dirs( ).product( ), "u-boot" ) )
   parameters.append( "-sd " + kw_drive )
   # parameters.append( "-hda " + kw_partition )
   # parameters.append( "-drive file= " + kw_drive + ",if=sd,format=raw" )
   # parameters.append( "-netdev user,id=eth0" )
   # parameters.append( "-device virtio-net-device,netdev=eth0" )
   # parameters.append( "-drive file=rootfs.ext4,if=none,format=raw,id=hd0" )
   # parameters.append( "-device virtio-blk-device,drive=hd0" )
   # parameters.append( "-s -S" )
   pfw.shell.run_and_wait_with_status( command, args = parameters, output = pfw.shell.eOutput.PTY )
# run_vexpress_ca9x4
