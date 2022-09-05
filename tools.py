#!/usr/bin/python3

import os
import subprocess

import pfw.console
import pfw.shell

import dt



def run_qemu( parameters, **kwargs ):
   EMULATOR = "/mnt/dev/git/qemu/build/"

   kw_bios = kwargs.get( "bios", None )
   kw_kernel = kwargs.get( "kernel", None )
   kw_initrd = kwargs.get( "initrd", None )
   kw_append = kwargs.get( "append", None )
   kw_dtb = kwargs.get( "dtb", None )
   kw_cwd = kwargs.get( "cwd", None )
   kw_arch = kwargs.get( "arch", None )
   kw_gdb = kwargs.get( "gdb", False )
   kw_dump_dtb = kwargs.get( "dump_dtb", False )
   kw_dump_dtb_path = kwargs.get( "dump_dtb_path", "/tmp/dump.dtb" )
   kw_output = kwargs.get( "output", pfw.shell.eOutput.PTY )

   if "x86" == kw_arch:
      EMULATOR = EMULATOR + f"qemu-system-x86_64"
   elif "x86_64" == kw_arch:
      EMULATOR = EMULATOR + f"qemu-system-x86_64"
   elif "arm" == kw_arch or "arm32" == kw_arch:
      EMULATOR = EMULATOR + f"qemu-system-arm"
   elif "arm64" == kw_arch or "aarch64" == kw_arch:
      EMULATOR = EMULATOR + f"qemu-system-aarch64"

   command: str = f"{EMULATOR} {parameters}"

   if None != kw_bios:
      command += f" -bios {kw_bios}"
   if None != kw_kernel:
      command += f" -kernel {kw_kernel}"
   if None != kw_initrd:
      command += f" -initrd {kw_initrd}"
   if None != kw_append:
      command += f" -append \"{kw_append}\""
   if None != kw_dtb:
      command += f" -dtb {kw_dtb}"

   if True == kw_dump_dtb:
      command += f" -machine dumpdtb={kw_dump_dtb_path}"

   if True == kw_gdb:
      command += f" -s -S"

   result = pfw.shell.run_and_wait_with_status(
         command,
         cwd = kw_cwd,
         output = kw_output
      )

   if True == kw_dump_dtb:
      dt.decompile( kw_dump_dtb_path, kw_dump_dtb_path + ".dts" )

   return result["code"]
# def run_qemu



def gdb( **kwargs ):
   kw_ip = kwargs.get( "ip", "localhost" )
   kw_port = kwargs.get( "port", 1234 )
   kw_arch = kwargs.get( "arch", None ) # configuration.arch( )
   kw_file = kwargs.get( "file", None )
   kw_lib_path = kwargs.get( "lib_path", None ) # os.path.join( configuration.compiler_path( ), "lib" )
   kw_src_path = kwargs.get( "src_path", None )
   kw_rellocate_offset = kwargs.get( "rellocate_offset", None ) # In case of u-boot will be printed as "Relocation Offset is: ..."
   kw_break_names = kwargs.get( "break_names", None )
   kw_break_addresses = kwargs.get( "break_addresses", None )
   kw_ex_list = kwargs.get( "ex_list", [ ] )

   command = f"gdb-multiarch"
   command += f" -q"
   command += f" --nh"
   command += f" -tui"

   # command += f" -ex \"layout split\""
   # command += f" -ex \"layout asm\""
   command += f" -ex \"layout regs\""
   command += f" -ex \"set disassemble-next-line on\""
   command += f" -ex \"show configuration\""
   # Processing ex_list and filling "-ex" parameters
   for kw_ex_list_item in kw_ex_list:
      command += f" -ex \"{kw_ex_list_item}\""
   # Processing specifik named kwargs parameters and filling/overriding "-ex" parameters
   command += f" -ex \"target remote {kw_ip}:{str(kw_port)}\""
   if None != kw_arch:
      command += f" -ex \"set architecture {kw_arch}\""
   if None != kw_file:
      command += f" -ex \"file {kw_file}\""
   if None != kw_lib_path:
      command += f" -ex \"set solib-search-path {kw_lib_path}\""
   if None != kw_src_path:
      command += f" -ex \"set directories {kw_src_path}\""
   if None != kw_rellocate_offset:
      command += f" -ex \"symbol-file\""
      command += f" -ex \"add-symbol-file {kw_file} {kw_rellocate_offset}\""
   if None != kw_break_names:
      for break_name in kw_break_names:
         command += f" -ex \"b {break_name}\""
   if None != kw_break_addresses:
      for break_addr in kw_break_addresses:
         command += f" -ex \"b *{break_addr}\""

   command += f" -ex \"info breakpoints\""
   command += f" -ex \"info files\""
      
   # command += f" -ex \"c\""

   pfw.shell.run_and_wait_with_status( command, output = pfw.shell.eOutput.PTY )
# gdb



def mkimage( projects_map: dict, root_dir: str ):
   mkimage_tool = projects_map["u-boot"].mkimage

   mkimage_tool(
           projects_map["kernel"].dirs( ).deploy( "Image" ), "kernel"
         , compression = "none", load_addr = "0x53000000"
      )
   mkimage_tool(
           projects_map["kernel"].dirs( ).deploy( "Image.gz" ), "kernel"
         , compression = "none", load_addr = "0x53000000"
      )

   mkimage_tool(
           projects_map["buildroot"].dirs( ).deploy( "rootfs.ext2" ), "filesystem"
         , compression = "none", load_addr = "0x55000000"
      )
   mkimage_tool(
           projects_map["buildroot"].dirs( ).deploy( "rootfs.cpio" ), "ramdisk"
         , compression = "none", load_addr = "0x55000000"
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

def mkbootimg( projects_map: dict, root_dir: str ):
   mkbootimg_tool = projects_map["aosp"].create_android_boot_image

   cmdline = "loglevel=7 debug printk.devkmsg=on drm.debug=0x0 console=ttyAMA0 earlyprintk=ttyAMA0"
   cmdline += " root=/dev/ram rw"
   cmdline += " loop.max_loop=10"

   mkbootimg_tool(
         header_version = 2,
         kernel = projects_map["kernel"].dirs( ).deploy( "Image" ),
         ramdisk = projects_map["buildroot"].dirs( ).deploy( "rootfs.cpio" ),
         dtb = os.path.join( root_dir, "configuration/dtb/aarch64_virt_cortex-a53/dtc_export_fixed.dtb" ),
         cmdline = cmdline,
         out = "/mnt/dev/tmp/images/boot_linux.img"
      )

   mkbootimg_tool(
         header_version = 2,
         kernel = projects_map["aosp"].dirs( ).product( "kernel"),
         ramdisk = projects_map["aosp"].dirs( ).experimental( "ramdisk"),
         dtb = os.path.join( root_dir, "configuration/dtb/aarch64_virt_cortex-a53/dtc_export_fixed.dtb" ),
         cmdline = cmdline,
         out = "/mnt/dev/tmp/images/boot_aosp.img"
      )
# def mkbootimg

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
         {
            "src": os.path.join( root_dir, "configuration/dtb/aarch64_virt_cortex-a53/dtc_export_fixed.dtb" ),
            "dest": os.path.join( mount_point, "boot/dtb.dtb" )
         },
         {
            "src": projects_map["buildroot"].dirs( ).deploy( "rootfs.cpio.uimg" ),
            "dest": os.path.join( mount_point, "boot/rootfs.cpio.uimg" )
         },
         {
            "src": projects_map["busybox"].dirs( ).deploy( "initramfs.cpio.uimg" ),
            "dest": os.path.join( mount_point, "boot/initramfs.cpio.uimg" )
         },
         {
            "src": "/mnt/dev/tmp/images/boot_linux.img",
            "dest": os.path.join( mount_point, "boot/boot_linux.img" )
         },
         {
            "src": "/mnt/dev/tmp/images/boot_aosp.img",
            "dest": os.path.join( mount_point, "boot/boot_aosp.img" )
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
      pfw.image.Drive.Partition( size = pfw.size.Size( 512, pfw.size.Size.eGran.M ), fs = image_description.fs( ) ),
   ]

   mmc: pfw.image.Drive = pfw.image.Drive( image_description.file( ) )
   mmc.create( partitions = partitions, force = True )
   mmc.attach( )
   mmc.init( partitions, bootable = 1 )
   mmc.mount( 1, image_description.mount_point( ) )

   mkimage( projects_map, root_dir )
   projects_map["aosp"].build_ramdisk( )
   mkbootimg( projects_map, root_dir )
   deploy( projects_map, image_description.mount_point( ), root_dir, pause = True )

   mmc.info( )
   mmc.detach( )
# def mkdrive

def run_arm64( **kwargs ):
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
   command += f" -drive if=none,index=0,id=main,file={kw_drive}"
   command += f" -device virtio-blk-pci,modern-pio-notify,drive=main"

   run_qemu( command, arch = "arm64", **kwargs )
# run_experimental_arm64

