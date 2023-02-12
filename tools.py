#!/usr/bin/python3

import os
import subprocess
import re

import pfw.console
import pfw.shell

import configuration
import gdb
import qemu



def mkimage( projects_map: dict ):
   mkimage_tool = projects_map["uboot"].mkimage

   mkimage_tool(
           projects_map["kernel"].dirs( ).deploy( "Image" ), "kernel"
         , compression = "none", load_addr = "0x53000000"
      )

   mkimage_tool(
           projects_map["xen"].dirs( ).deploy( "boot/xen-" + projects_map["xen"].version( ) ), "kernel"
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
           configuration.value( "uboot_script" ), "script"
         , compression = "none", load_addr = "0x65000000"
      )
# def mkimage

def mkbootimg( projects_map: dict ):
   mkbootimg_tool = projects_map["aosp"].create_android_boot_image

   cmdline = qemu.build_kernel_parameters( arch = projects_map["aosp"].config( ).arch( ), debug = True )
   # cmdline += " root=/dev/ram rw"

   mkbootimg_tool(
         header_version = 2,
         kernel = projects_map["kernel"].dirs( ).deploy( "Image" ),
         ramdisk = projects_map["buildroot"].dirs( ).deploy( "rootfs.cpio" ),
         dtb = configuration.value( "dtb_export_path" ),
         cmdline = cmdline,
         out = os.path.join( configuration.value( "tmp_path" ), "boot_linux.img" ),
         base = 0x50000000,
         kernel_offset = 0x3000000,
         ramdisk_offset = 0x6000000,
         dtb_offset = 0x00000000,
      )

   mkbootimg_tool(
         header_version = 2,
         kernel = projects_map["aosp"].dirs( ).product( "kernel"),
         # kernel = "/mnt/dev/android/deploy/kernel/common-android14-6.1/virtual_device_aarch64/extracted/boot.img/kernel",
         ramdisk = projects_map["aosp"].dirs( ).experimental( "ramdisk.img"),
         dtb = configuration.value( "dtb_export_path" ),
         cmdline = cmdline,
         out = os.path.join( configuration.value( "tmp_path" ), "boot_aosp.img" ),
         base = 0x50000000,
         kernel_offset = 0x3000000,
         ramdisk_offset = 0x6000000,
         dtb_offset = 0x00000000,
      )
# def mkbootimg

def prepare_boot( projects_map: dict ):
   projects_map["uboot"].build_uboot_script( configuration.value( "uboot_script_source" ), configuration.value( "uboot_script" ) )

   mkimage( projects_map )

   bootconfig_file: str = None
   if projects_map["aosp"].config( ).arch( ) in [ "x86", "x86_64" ]:
      bootconfig_file = configuration.value( "android_bootconfig_x86" )
   elif projects_map["aosp"].config( ).arch( ) in [ "arm64", "aarch64" ]:
      bootconfig_file = configuration.value( "android_bootconfig_arm64" )

   projects_map["aosp"].build_ramdisk(
         bootconfig = { "tool": projects_map["kernel"].bootconfig, "config": bootconfig_file }
      )

   mkbootimg( projects_map )
# def prepare_boot

def deploy_boot( projects_map: dict, mount_point: str, pause: bool = False ):
   files_list: list = [
         # {
         #    "src": configuration.value( "syslinux_script" ),
         #    "dest": os.path.join( mount_point, "boot/extlinux/extlinux.conf" )
         # },
         {
            "src": configuration.value( "uboot_script" ) + ".uimg",
            "dest": os.path.join( mount_point, "boot/boot.scr" )
         },
         {
            "src": configuration.value( "dtb_export_path" ),
            "dest": os.path.join( mount_point, "boot/export.dtb" )
         },
         {
            "src": configuration.value( "dtb_dump_path" ),
            "dest": os.path.join( mount_point, "boot/dump.dtb" )
         },
         {
            "src": projects_map["kernel"].dirs( ).deploy( "Image" ),
            "dest": os.path.join( mount_point, "boot/kernel-" + projects_map["kernel"].version( ) )
         },
         {
            "src": projects_map["kernel"].dirs( ).deploy( "Image.uimg" ),
            "dest": os.path.join( mount_point, "boot/kernel-" + projects_map["kernel"].version( ) + ".uimg" )
         },
         {
            "src": projects_map["xen"].dirs( ).deploy( "boot/xen-" + projects_map["xen"].version( ) ),
            "dest": os.path.join( mount_point, "boot/xen-" + projects_map["xen"].version( ) )
         },
         {
            "src": projects_map["xen"].dirs( ).deploy( "boot/xen-" + projects_map["xen"].version( ) + ".uimg" ),
            "dest": os.path.join( mount_point, "boot/xen-" + projects_map["xen"].version( ) + ".uimg" )
         },
         {
            "src": projects_map["buildroot"].dirs( ).deploy( "rootfs.cpio" ),
            "dest": os.path.join( mount_point, "boot/rootfs-" + projects_map["buildroot"].version( ) + ".cpio" )
         },
         {
            "src": projects_map["buildroot"].dirs( ).deploy( "rootfs.cpio.uimg" ),
            "dest": os.path.join( mount_point, "boot/rootfs-" + projects_map["buildroot"].version( ) + ".cpio.uimg" )
         },
         {
            "src": projects_map["busybox"].dirs( ).deploy( "initramfs.cpio" ),
            "dest": os.path.join( mount_point, "boot/initramfs-" + projects_map["busybox"].version( ) + ".cpio" )
         },
         {
            "src": projects_map["busybox"].dirs( ).deploy( "initramfs.cpio.uimg" ),
            "dest": os.path.join( mount_point, "boot/initramfs-" + projects_map["busybox"].version( ) + ".cpio.uimg" )
         },
         {
            "src": os.path.join( configuration.value( "tmp_path" ), "boot_linux.img" ),
            "dest": os.path.join( mount_point, "boot/boot_linux.img" )
         },
         {
            "src": os.path.join( configuration.value( "tmp_path" ), "boot_aosp.img" ),
            "dest": os.path.join( mount_point, "boot/boot_aosp.img" )
         },
      ]

   for item in files_list:
      if False == os.path.exists( item["src"] ):
         pfw.console.debug.warning( "file does not exist: ", item["src"] )
         continue
      pfw.shell.execute( "sudo mkdir -p " + os.path.dirname( item["dest"] ), output = pfw.shell.eOutput.PTY )
      pfw.console.debug.trace( "file: '%s' ->\n     '%s'" % ( item["src"], item["dest"] ) )
      pfw.shell.execute( f"sudo cp " + item["src"] + " " + item["dest"], output = pfw.shell.eOutput.PTY )

   if True == pause:
      subprocess.Popen(['xdg-open', mount_point])
      pfw.console.debug.promt( )
# def deploy_boot

def mkpartition_boot( projects_map: dict ):
   mmc: pfw.linux.image.Partition = pfw.linux.image.Partition( configuration.value( "boot_partition_image" ), build = True, force = True )
   mount_point = mmc.mount( configuration.value( "tmp_path" ), True )

   prepare_boot( projects_map )
   deploy_boot( projects_map, mount_point, pause = True )

   mmc.info( )
   mmc.umount( )
# def mkpartition_boot

def mkpartition_rootfs( projects_map: dict ):
   rootfs_project = projects_map["rootfs"]

   rootfs_project.init( )
   rootfs_project.execute( f"mkdir /projects" )
   rootfs_project.execute( f"git clone https://xenbits.xen.org/git-http/xen.git /projects/xen" )
   rootfs_project.execute( f"cd /projects/xen; git checkout origin/stable-4.15 --track" )
   rootfs_project.execute( f"cd /projects/xen; ./configure --disable-docs --disable-stubdom --prefix=/usr/local --libdir=/usr/lib --enable-systemd" )
   rootfs_project.execute( f"cd /projects/xen; CC=gcc make -j4 debball" )
   rootfs_project.deinit( )


   if True == pause:
      subprocess.Popen(['xdg-open', mount_point])
      pfw.console.debug.promt( )
# def mkpartition_rootfs

def mkdrive( projects_map: dict ):
   mkpartition_boot( projects_map )
   boot_image = configuration.value( "boot_partition_image" ).file( )

   # mkpartition_rootfs( projects_map )
   # rootfs_image = projects_map["rootfs"].dirs( ).build( "rootfs.img" )

   super_image = projects_map["aosp"].dirs( ).product( "super.img" )
   if "arm64" == projects_map["aosp"].config( ).arch( ):
      super_image = projects_map["aosp"].dirs( ).experimental( "super.raw" )
      projects_map["aosp"].simg_to_img( projects_map["aosp"].dirs( ).product( "super.img" ), super_image )

   userdata_image = projects_map["aosp"].dirs( ).product( "userdata.img" )
   if "arm64" == projects_map["aosp"].config( ).arch( ):
      userdata_image = projects_map["aosp"].dirs( ).experimental( "userdata.raw" )
      projects_map["aosp"].simg_to_img( projects_map["aosp"].dirs( ).product( "userdata.img" ), userdata_image )

   vbmeta_image = projects_map["aosp"].dirs( ).product( "vbmeta.img" )
   vbmeta_system_image = projects_map["aosp"].dirs( ).product( "vbmeta_system.img" )

   boot_part_num = 1
   partitions = [
      pfw.linux.image.Partition.Description( clone_from = boot_image, label = "boot" ),
      # pfw.linux.image.Partition.Description( clone_from = rootfs_image, label = "rootfs" ),

      pfw.linux.image.Partition.Description( clone_from = super_image, label = "super" ),

      pfw.linux.image.Partition.Description( clone_from = userdata_image, label = "userdata" ),
      pfw.linux.image.Partition.Description( size = pfw.size.SizeGigabyte, label = "cache", fs = "ext4" ),
      pfw.linux.image.Partition.Description( size = pfw.size.SizeGigabyte, label = "metadata", fs = "ext4" ),
      pfw.linux.image.Partition.Description( size = pfw.size.SizeGigabyte, label = "misc", fs = "ext4" ),

      pfw.linux.image.Partition.Description( clone_from = vbmeta_image, label = "vbmeta_a" ),
      pfw.linux.image.Partition.Description( clone_from = vbmeta_system_image, label = "vbmeta_system_a" ),
   ]

   mmc: pfw.linux.image.Drive = pfw.linux.image.Drive( configuration.value( "main_drive_image" ) )
   mmc.create( partitions = partitions, force = True )
   mmc.attach( )
   mmc.init( partitions, bootable = boot_part_num )
   mmc.info( )
   mmc.detach( )
# def mkdrive

def debug( projects_map: dict, **kwargs ):
   kw_project_name = kwargs.get( "project_name", "uboot" )

   project = projects_map[ kw_project_name ]

   if "uboot" == kw_project_name:
      gdb.run(
            # arch = projects_map[ "uboot" ].config( ).arch( ),
            file = projects_map[ "uboot" ].dirs( ).product( "u-boot" ),
            # lib_path = projects_map[ "uboot" ].config( ).compiler_path( "lib" ),
            # src_path = projects_map[ "uboot" ].dirs( ).source( ),
            load_symbols = {
               # projects_map[ "uboot" ].dirs( ).product( "u-boot" ): [ 0x000000000 ], # in case of "u-boot" "x0" register when enter to "relocate_code" function
               # projects_map[ "uboot" ].dirs( ).product( "u-boot" ): [ 0x23ff03000 ], # u-boot v2021.10
               projects_map[ "uboot" ].dirs( ).product( "u-boot" ): [ 0x23ff03000 ], # u-boot v2022.07
               # projects_map[ "kernel" ].dirs( ).deploy( "vmlinux" ): [ 0x40410800 ], # kernel 5.15 loaded to 0x40410800
               # projects_map[ "kernel" ].dirs( ).deploy( "vmlinux" ): [ 0x53010000 ], # kernel 5.15 loaded to 0x40410800
            },
            break_names = [
               ### u-boot functions
               # "do_bootm",
               # "do_bootm_states",
               # "bootm_find_other",
               # "bootm_find_images",
               # "boot_get_ramdisk",
               # "select_ramdisk",
               "boot_jump_linux",
               "announce_and_cleanup",
               "armv8_switch_to_el2",
               ### kernel functions
               # "primary_entry",
               # "__primary_switch",
               # "__primary_switched",
               # "start_kernel",
               # "rest_init",
               # "cpu_startup_entry"
            ],
            break_addresses = [
            ],
            break_code = {
               # u-boot code
               projects_map[ "uboot" ].dirs( ).source( "arch/arm/cpu/armv8/transition.S" ): [ 30 ]
               # kernel code
            },
            none = None
         )
   elif "kernel" == kw_project_name:
      gdb.run(
            # arch = project.config( ).arch( ),
            file = project.dirs( ).deploy( "vmlinux" ),
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
# def debug



def build_emulator_parameters( projects_map, **kwargs ):
   kw_drive = kwargs.get( "drive", None )
   kw_arch = projects_map["aosp"].config( ).arch( )
   kw_inet_dump = os.path.join( configuration.value( "tmp_path" ), "eth0_inet_dump_$(date '+%Y-%m-%d_%H:%M:%S').dat" )
   # For using qemu-bridge-helper
   # https://mike42.me/blog/2019-08-how-to-use-the-qemu-bridge-helper-on-debian-10
   kw_qemu_bridge_helper = "/usr/lib/qemu/qemu-bridge-helper"

   PARAMETERS = f""
   PARAMETERS =+ f" -serial mon:stdio"
   PARAMETERS =+ f" -nodefaults"
   PARAMETERS =+ f" -no-reboot"
   PARAMETERS =+ f" -d guest_errors"
   if "x86" == kw_arch:
      PARAMETERS = PARAMETERS + f" -enable-kvm"
      PARAMETERS = PARAMETERS + f" -smp cores=2"
      PARAMETERS = PARAMETERS + f" -m 8192"
   elif "arm64" == kw_arch:
      PARAMETERS = PARAMETERS + f" -machine virt"
      # PARAMETERS = PARAMETERS + f" -machine virtualization=true"
      PARAMETERS = PARAMETERS + f" -cpu cortex-a53"
      PARAMETERS = PARAMETERS + f" -smp cores=4"
      PARAMETERS = PARAMETERS + f" -m 8192"

   IMAGE_DEVICES_MAIN = f"" \
      + f" -drive if=none,index=0,id=main,file={kw_drive}" \
      + f" -device virtio-blk-pci,modern-pio-notify=on,drive=main"

   NETWORK_NETDEV_USER = f"" \
      + f" -netdev user,id=eth0_inet,hostfwd=tcp::5550-:5555,ipv6=off" \
      + f" -device virtio-net-pci,netdev=eth0_inet,id=android"

   NETWORK_NETDEV_BRIDGE = f"" \
      + f" -netdev bridge,id=eth0_inet,br=virbr0,helper={kw_qemu_bridge_helper}" \
      + f" -device virtio-net-pci,netdev=eth0_inet,id=android"

   NETWORK_NETDEV_TAP = f"" \
      + f" -netdev tap,id=eth0_inet,ifname=ethernet_tap,script=no,downscript=no,vhost=on" \
      + f" -device virtio-net-pci-non-transitional,netdev=eth0_inet,id=android"

   NETWORK_OBJECT_DUMP = f"" \
      + f" -object filter-dump,id=f1,netdev=eth0_inet,file={kw_inet_dump}" \

   NETWORK_NET_USER = f"" \
      + f" -net user" \
      + f" -net nic" \

   NETWORK_NET_BRIDGE = f"" \
      + f" -net bridge,br=virbr0,helper={kw_qemu_bridge_helper}" \
      + f" -net nic,model=virtio"

   PCI_KBD_MOUSE = f"" \
      + " -device virtio-keyboard-pci" \
      + " -device virtio-mouse-pci"

   USB_BUS = f"" \
      + " -usb"

   USB_KBD_MOUSE = f"" \
      + " -device usb-kbd" \
      + " -device usb-mouse"

   GRAPHIC_DEVICES = f"" \
      + " -display gtk,gl=on,show-cursor=on" \
      + " -device virtio-gpu-gl-pci"

   DEVICES_AUDIO_VIRTIO = f"" \
      + " -audiodev alsa,id=snd0,out.dev=default" \
      + " -device virtio-snd-pci,disable-legacy=on,audiodev=snd0"

   DEVICES_AUDIO_INTEL = f"" \
      + " -audiodev alsa,id=snd0,out.dev=default" \
      + " -device intel-hda" \
      + " -device hda-duplex,audiodev=snd0"

   CHAR_DEVICES = f"" \
      + " -device virtio-serial-pci,ioeventfd=off" \
      + " -chardev null,id=forhvc0" \
      + " -device virtconsole,chardev=forhvc0" \
      + " -chardev null,id=forhvc1" \
      + " -device virtconsole,chardev=forhvc1"

   OTHER_DEVICES = f"" \
      + " -device nec-usb-xhci,id=xhci" \
      + " -device sdhci-pci" \
      + " -device virtio-rng-pci"

   command: str = f" {PARAMETERS}"
   command += f" {IMAGE_DEVICES_MAIN}"
   command += f" {NETWORK_NETDEV_USER}"
   command += f" {GRAPHIC_DEVICES}"
   command += f" {DEVICES_AUDIO_INTEL}"
   # command += f" {USB_BUS}"
   # command += f" {USB_KBD_MOUSE}"
   # command += f" {CHAR_DEVICES}"
   # command += f" {OTHER_DEVICES}"

   return command
# def build_emulator_parameters

def start( projects_map: dict, **kwargs ):
   kw_mode = kwargs.get( "mode", None )
   kw_gdb = kwargs.get( "gdb", False )
   kw_drive = kwargs.get( "drive", None )
   kw_arch = kwargs.get( "arch", "arm64" )

   if None == kw_drive:
      if  kw_mode in [ "u-boot", "kernel_rd", "aosp" ]:
         kw_drive = configuration.value( "main_drive_image" )
      elif kw_mode in [ "kernel_rf" ]:
         kw_drive = projects_map["rootfs"].dirs( ).build( "rootfs.img" )
      else:
         pass

   command: str = ""
   if "aosp" == kw_mode:
      command = build_emulator_parameters( projects_map,  drive = kw_drive )
   elif kw_mode in [ "u-boot", "kernel_rd", "kernel_rf" ]:
      command = qemu.build_parameters( arch = kw_arch )

      command += f" -drive if=none,index=0,id=main,file={kw_drive}"
      command += f" -device virtio-blk-pci,modern-pio-notify,drive=main"

      command += f" -netdev user,id=net0,hostfwd=tcp::2222-:22"
      command += f" -device virtio-net-device,netdev=net0"

      command += f" -device virtio-serial-pci"
      command += f" -device nec-usb-xhci,id=xhci"
      command += f" -device sdhci-pci"
      command += f" -device virtio-rng-pci"

      # vc_pipe = "/tmp/virtio_console_chardev.pipe"
      # pfw.shell.execute( f"rm {vc_pipe}; mkfifo {vc_pipe}", output = pfw.shell.eOutput.PTY )
      # pfw.shell.execute( f"rm {vc_pipe}.in; mkfifo {vc_pipe}.in", output = pfw.shell.eOutput.PTY )
      # pfw.shell.execute( f"rm {vc_pipe}.out; mkfifo {vc_pipe}.out", output = pfw.shell.eOutput.PTY )
      # command += f" -chardev pipe,id=virtio_console_chardev,path={vc_pipe}"
      # command += f" -device virtconsole,chardev=virtio_console_chardev,id=virtio_console"

      # command += f" -device virtio-gpu-pci"
      # command += f" -device virtio-gpu-gl-pci"
      # command += f" -display gtk,gl=on,show-cursor=on"
      # command += f" -vga cirrus"
      # command += f" -display gtk,show-cursor=on"
   else:
      pass

   kw_args: dict = { }
   kw_args["arch"] = kw_arch
   kw_args["gdb"] = kw_gdb
   if "aosp-uboot" == kw_mode:
      if kw_arch in [ "x86", "x86_64" ]:
         kw_args["bios"] = projects_map["uboot"].dirs( ).product( "u-boot.rom" )
      elif kw_arch in [ "arm", "arm32", "arm64", "aarch64" ]:
         kw_args["bios"] = projects_map["uboot"].dirs( ).product( "u-boot.bin" )
   elif "aosp-kernel" == kw_mode:
      kw_args["kernel"] = projects_map["aosp"].dirs( ).product( "kernel" )
      kw_args["initrd"] = projects_map["aosp"].dirs( ).experimental( "ramdisk.img")
      kw_args["append"] = "loglevel=7 debug printk.devkmsg=on drm.debug=0x1FF console=ttyAMA0"
      kw_args["dtb"] = configuration.value( "dtb_export_path" )
   elif "u-boot" == kw_mode:
      if kw_arch in [ "x86", "x86_64" ]:
         kw_args["bios"] = projects_map["uboot"].dirs( ).product( "u-boot.rom" )
      elif kw_arch in [ "arm", "arm32", "arm64", "aarch64" ]:
         kw_args["bios"] = projects_map["uboot"].dirs( ).product( "u-boot.bin" )
   elif "kernel_rd" == kw_mode:
      kw_args["kernel"] = projects_map["kernel"].dirs( ).deploy( "Image" )
      kw_args["initrd"] = projects_map["buildroot"].dirs( ).deploy( "rootfs.cpio" )
      kw_args["append"] = "loglevel=7 debug printk.devkmsg=on drm.debug=0x1FF console=ttyAMA0"
      kw_args["dtb"] = configuration.value( "dtb_export_path" )
   elif "kernel_rf" == kw_mode:
      kw_args["kernel"] = projects_map["kernel"].dirs( ).deploy( "Image" )
      kw_args["append"] = "loglevel=7 debug printk.devkmsg=on drm.debug=0x1FF console=ttyAMA0 init=/bin/bash root=/dev/vda rw"
      kw_args["dtb"] = configuration.value( "dtb_export_path" )
   else:
      pass

   qemu.run( command, **kw_args )
# def start





# u-boot: vexpress_ca9x4_defconfig
# kernel: vexpress_defconfig
# busybox: defconfig
# buildroot: qemu_arm_vexpress_defconfig
def run_vexpress_ca9x4( projects_map: dict, **kwargs ):
   kw_partition = kwargs.get( "partition", None )
   kw_drive = kwargs.get( "drive", None )

   command: str = None
   parameters: list = [ ]

   QEMU_PATH=""

   command = f"{QEMU_PATH}qemu-system-arm"
   parameters.append( "-machine vexpress-a9" )
   parameters.append( "-nographic" )
   parameters.append( "-smp 1" )
   parameters.append( "-m 256M" )
   parameters.append( "-kernel " + os.path.join( projects_map["uboot"].dirs( ).product( ), "u-boot" ) )
   parameters.append( "-sd " + kw_drive )
   # parameters.append( "-hda " + kw_partition )
   # parameters.append( "-drive file= " + kw_drive + ",if=sd,format=raw" )
   # parameters.append( "-netdev user,id=eth0" )
   # parameters.append( "-device virtio-net-device,netdev=eth0" )
   # parameters.append( "-drive file=rootfs.ext4,if=none,format=raw,id=hd0" )
   # parameters.append( "-device virtio-blk-device,drive=hd0" )
   # parameters.append( "-s -S" )
   pfw.shell.execute( command, args = parameters, output = pfw.shell.eOutput.PTY )
# run_vexpress_ca9x4
