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



def mkimage( projects_map: dict, root_dir: str ):
   mkimage_tool = projects_map["u-boot"].mkimage
   # Preparing u-images
   mkimage_tool(
           projects_map["kernel"].dirs( ).deploy( "Image" ), "kernel"
         , compression = "none", load_addr = "0x53000000"
      )
   mkimage_tool(
           projects_map["kernel"].dirs( ).deploy( "Image.gz" ), "kernel"
         , compression = "none", load_addr = "0x53000000"
      )
   mkimage_tool(
           projects_map["kernel"].dirs( ).deploy( "zImage" ), "kernel"
         , compression = "none", load_addr = "0x53000000"
      )
   mkimage_tool(
           projects_map["kernel"].dirs( ).deploy( "vmlinux" ), "kernel"
         , compression = "none", load_addr = "0x53000000"
      )
   # mkimage_tool(
   #         projects_map["kernel"].dirs( ).deploy( "dts/vexpress-v2p-ca9.dtb" ), "flat_dt"
   #       , compression = "none", load_addr = "0x54000000"
   #    )
   # mkimage_tool(
   #         os.path.join( root_dir, "configuration/dtb.dtb" ), "flat_dt"
   #       , compression = "none", load_addr = "0x54000000"
   #    )
   mkimage_tool(
           projects_map["buildroot"].dirs( ).deploy( "rootfs.ext2" ), "filesystem"
         , compression = "none", load_addr = "0x55000000"
      )
   mkimage_tool(
           projects_map["buildroot"].dirs( ).deploy( "rootfs.cpio" ), "ramdisk"
         , compression = "none", load_addr = "0x55000000"
      )
   mkimage_tool(
           projects_map["buildroot"].dirs( ).deploy( "rootfs.cpio.gz" ), "ramdisk"
         , compression = "gzip", load_addr = "0x55000000"
      )
   mkimage_tool(
           projects_map["busybox"].dirs( ).deploy( "initramfs.cpio" ), "ramdisk"
         , compression = "none", load_addr = "0x55000000"
      )
   mkimage_tool(
           projects_map["busybox"].dirs( ).deploy( "initramfs.cpio.gz" ), "ramdisk"
         , compression = "gzip", load_addr = "0x55000000"
      )
   mkimage_tool(
           os.path.join( root_dir, "configuration/boot.cmd" ), "script"
         , compression = "none", load_addr = "0x65000000"
         , destination = os.path.join( root_dir, "configuration/boot.scr" )
      )
# def mkimage

def deploy( projects_map: dict, mount_point: str, root_dir: str, pause: bool = False ):
   files_list: list = [
         {
            "src": os.path.join( root_dir, "configuration/boot.scr" ),
            "dest": os.path.join( mount_point, "boot/boot.scr" )
         },
         # {
         #    "src": os.path.join( root_dir, "configuration/extlinux.conf" ),
         #    "dest": os.path.join( mount_point, "boot/extlinux/extlinux.conf" )
         # },
         {
            "src": projects_map["kernel"].dirs( ).deploy( "Image.uimg" ),
            "dest": os.path.join( mount_point, "boot/Image.uimg" )
         },
         {
            "src": projects_map["kernel"].dirs( ).deploy( "zImage.uimg" ),
            "dest": os.path.join( mount_point, "boot/zImage.uimg" )
         },
         # {
         #    "src": projects_map["kernel"].dirs( ).deploy( "dts/vexpress-v2p-ca9.dtb" ),
         #    "dest": os.path.join( mount_point, "boot/vexpress-v2p-ca9.dtb" )
         # },
         {
            "src": os.path.join( root_dir, "configuration/dtb.dtb" ),
            "dest": os.path.join( mount_point, "boot/dtb.dtb" )
         },
         # {
         #    "src": os.path.join( root_dir, "configuration/dtb.dtb.uimg" ),
         #    "dest": os.path.join( mount_point, "boot/dtb.dtb.uimg" )
         # },
         {
            "src": projects_map["buildroot"].dirs( ).deploy( "rootfs.cpio.uimg" ),
            "dest": os.path.join( mount_point, "boot/rootfs.cpio.uimg" )
         },
         {
            "src": projects_map["busybox"].dirs( ).deploy( "initramfs.cpio.uimg" ),
            "dest": os.path.join( mount_point, "boot/initramfs.cpio.uimg" )
         },
         {
            "src": "/home/dmytro_terletskyi/Sources/TDA/Examples/module/tda.ko",
            "dest": os.path.join( mount_point, "boot/tda.ko" )
         },
         {
            "src": projects_map["aosp"].dirs( ).experimental( "boot.img" ),
            "dest": os.path.join( mount_point, "boot/boot.img" )
         },
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

def mkpartition( projects_map: dict, image_description: pfw.image.Description, root_dir: str ):
   mmc: pfw.image.Partition = pfw.image.Partition( image_description.file( ) )
   mmc.create( image_description.size( ), force = True )
   mmc.format( image_description.fs( ) )
   mmc.mount( image_description.mount_point( ) )

   mkimage( projects_map, root_dir )
   deploy( projects_map, image_description.mount_point( ), root_dir, pause = True )

   mmc.info( )
   mmc.umount( )
# def mkpartition

def mkdrive( projects_map: dict, image_description: pfw.image.Description, root_dir: str ):
   partitions = [
      pfw.image.Drive.Partition( size = pfw.size.Size( 128, pfw.size.Size.eGran.M ), fs = image_description.fs( ) ),
      pfw.image.Drive.Partition( size = pfw.size.Size( 64, pfw.size.Size.eGran.M ), fs = image_description.fs( ) ),
      pfw.image.Drive.Partition( size = pfw.size.Size( 32, pfw.size.Size.eGran.M ), fs = image_description.fs( ) ),
      pfw.image.Drive.Partition( size = pfw.size.Size( 31, pfw.size.Size.eGran.M ), fs = image_description.fs( ) ),
   ]

   mmc: pfw.image.Drive = pfw.image.Drive( image_description.file( ) )
   mmc.create( partitions = partitions, force = True )
   mmc.attach( )
   mmc.init( partitions, bootable = 1 )
   mmc.mount( 1, image_description.mount_point( ) )

   mkimage( projects_map, root_dir )
   deploy( projects_map, image_description.mount_point( ), root_dir, pause = True )

   mmc.info( )
   mmc.detach( )
# def mkdrive



QEMU_PATH="/mnt/dev/git/qemu/build/"

def run_vexpress_ca9x4( projects_map: dict, **kwargs ):
   kw_partition = kwargs.get( "partition", None )
   kw_drive = kwargs.get( "drive", None )

   # u-boot: vexpress_ca9x4_defconfig
   # kernel: vexpress_defconfig
   # busybox: defconfig
   # buildroot: qemu_arm_vexpress_defconfig
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

def run_experimental_arm( projects_map: dict, **kwargs ):
   kw_partition = kwargs.get( "partition", None )
   kw_drive = kwargs.get( "drive", None )

   command: str = None
   parameters: list = [ ]

   command = f"{QEMU_PATH}qemu-system-arm"
   parameters.append( "-machine virt" )
   parameters.append( "-cpu cortex-a15" )
   parameters.append( "-nographic" )
   parameters.append( "-smp 1" )
   parameters.append( "-m 512M" )
   parameters.append( "-bios " + projects_map["u-boot"].dirs( ).product( "u-boot.bin" ) )
   parameters.append( "-drive if=none,index=0,id=kernel,file=" + kw_drive )
   parameters.append( "-device virtio-blk-pci,modern-pio-notify,drive=kernel" )
   pfw.shell.run_and_wait_with_status( command, args = parameters, output = pfw.shell.eOutput.PTY )
# run_experimental_arm

def run_arm64( **kwargs ):
   kw_uboot = kwargs.get( "uboot", None )
   kw_dtb = kwargs.get( "dtb", None )
   kw_kernel = kwargs.get( "kernel", None )
   kw_initrd = kwargs.get( "initrd", None )
   kw_append = kwargs.get( "append", None )
   kw_drive = kwargs.get( "drive", None )

   command: str = ""
   command += f" -machine virt"
   command += f" -cpu cortex-a53"
   command += f" -smp cores=4"
   command += f" -m 8192"
   # command += f" -nographic"
   command += f" -serial mon:stdio"
   command += f" -nodefaults"
   command += f" -no-reboot"
   command += f" -d guest_errors"
   command += f" -drive if=none,index=0,id=kernel,file={kw_drive}"
   command += f" -device virtio-blk-pci,modern-pio-notify,drive=kernel"

   tools.run_qemu( command, arch = "arm64", **kwargs )
# run_experimental_arm64

def run( projects_map: dict, **kwargs ):
   # run_vexpress_ca9x4( projects_map, **kwargs )
   # run_experimental_arm( projects_map, **kwargs )
   run_arm64( **kwargs )
   pass
# run
