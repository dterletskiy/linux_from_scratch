#!/usr/bin/python3

import os
import subprocess
import re

import pfw.console
import pfw.shell

import configuration
import gdb
import qemu



def build_uboot_script( ):
   script_in_file = configuration.UBOOT_SCRIPT_SOURCE
   script_out_file = configuration.UBOOT_SCRIPT

   script_in_dir = os.path.dirname( script_in_file )

   script_in_file_names = os.listdir( script_in_dir )
   script_in_files = [ os.path.join( script_in_dir, script_in_file_name ) for script_in_file_name in script_in_file_names ]

   script_in_file_h = open( script_in_file, "r" )
   pattern: str = r"^\s*import\s*\"(.*)\"\s*$"
   script_out_file_lines: str = ""
   for script_in_file_line in script_in_file_h:
      match = re.match( pattern, script_in_file_line )
      if match:
         import_file_name = match.group( 1 )
         import_file = os.path.join( script_in_dir, import_file_name )
         import_file_h = open( import_file, "r" )
         for import_file_line in import_file_h:
            script_out_file_lines += import_file_line
         import_file_h.close( )
         script_out_file_lines += "\n\n\n"
      else:
         script_out_file_lines += script_in_file_line
   script_in_file_h.close( )

   script_out_file_h = open( script_out_file, "w+" )
   script_out_file_h.write( script_out_file_lines )
   script_out_file_h.close( )
# def build_uboot_script

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
           configuration.UBOOT_SCRIPT, "script"
         , compression = "none", load_addr = "0x65000000"
      )
# def mkimage

def mkbootimg( projects_map: dict ):
   mkbootimg_tool = projects_map["aosp"].create_android_boot_image

   cmdline = qemu.build_cmdline( arch = projects_map["aosp"].config( ).arch( ) )
   # cmdline += " root=/dev/ram rw"

   mkbootimg_tool(
         header_version = 2,
         kernel = projects_map["kernel"].dirs( ).deploy( "Image" ),
         ramdisk = projects_map["buildroot"].dirs( ).deploy( "rootfs.cpio" ),
         dtb = configuration.DTB_PATH,
         cmdline = cmdline,
         out = os.path.join( configuration.TMP_PATH, "boot_linux.img" ),
         base = 0x50000000,
         kernel_offset = 0x3000000,
         ramdisk_offset = 0x6000000,
         dtb_offset = 0x00000000,
      )

   mkbootimg_tool(
         header_version = 2,
         kernel = projects_map["aosp"].dirs( ).product( "kernel"),
         ramdisk = projects_map["aosp"].dirs( ).experimental( "ramdisk.img"),
         dtb = configuration.DTB_PATH,
         cmdline = cmdline,
         out = os.path.join( configuration.TMP_PATH, "boot_aosp.img" ),
         base = 0x50000000,
         kernel_offset = 0x3000000,
         ramdisk_offset = 0x6000000,
         dtb_offset = 0x00000000,
      )
# def mkbootimg

def prepare( projects_map: dict ):
   build_uboot_script( )
   mkimage( projects_map )
   bootconfig_file: str = None
   if "x86" == projects_map["aosp"].config( ).arch( ) or "x86_64" == projects_map["aosp"].config( ).arch( ):
      bootconfig_file = configuration.ANDROID_BOOTCONFIG_X86
   elif "arm64" == projects_map["aosp"].config( ).arch( ) or "aarch64" == projects_map["aosp"].config( ).arch( ):
      bootconfig_file = configuration.ANDROID_BOOTCONFIG_ARM64
   projects_map["aosp"].build_ramdisk(
         bootconfig = { "tool": projects_map["kernel"].bootconfig, "config": bootconfig_file }
      )
   mkbootimg( projects_map )
# def prepare

def deploy( projects_map: dict, mount_point: str, pause: bool = False ):
   files_list: list = [
         # {
         #    "src": configuration.SYSLINUX_SCRIPT,
         #    "dest": os.path.join( mount_point, "boot/extlinux/extlinux.conf" )
         # },
         {
            "src": configuration.UBOOT_SCRIPT + ".uimg",
            "dest": os.path.join( mount_point, "boot/boot.scr" )
         },
         {
            "src": configuration.DTB_PATH,
            "dest": os.path.join( mount_point, "boot/dtb.dtb" )
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
            "src": os.path.join( configuration.TMP_PATH, "boot_linux.img" ),
            "dest": os.path.join( mount_point, "boot/boot_linux.img" )
         },
         {
            "src": os.path.join( configuration.TMP_PATH, "boot_aosp.img" ),
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

   if True == pause:
      subprocess.Popen(['xdg-open', mount_point])
      pfw.console.debug.promt( )
# def deploy

def mkpartition( projects_map: dict ):
   mmc: pfw.image.Partition = pfw.image.Partition( configuration.LINUX_IMAGE_PARTITION )
   mmc.create( force = True )
   mmc.format( )
   mmc.mount( )

   prepare( projects_map )
   deploy( projects_map, configuration.LINUX_IMAGE_PARTITION.mount_point( ), pause = True )

   mmc.info( )
   mmc.umount( )
# def mkpartition

def mkdrive( projects_map: dict ):
   boot_image = configuration.LINUX_IMAGE_PARTITION.file( )

   super_image = projects_map["aosp"].dirs( ).product( "super.img" )
   if "arm64" == projects_map["aosp"].config( ).arch( ):
      projects_map["aosp"].simg_to_img( projects_map["aosp"].dirs( ).product( "super.img" ), projects_map["aosp"].dirs( ).experimental( "super.raw" ) )
      super_image = projects_map["aosp"].dirs( ).experimental( "super.raw" )

   userdata_image = projects_map["aosp"].dirs( ).product( "userdata.img" )
   if "arm64" == projects_map["aosp"].config( ).arch( ):
      projects_map["aosp"].simg_to_img( projects_map["aosp"].dirs( ).product( "userdata.img" ), projects_map["aosp"].dirs( ).experimental( "userdata.raw" ) )
      userdata_image = projects_map["aosp"].dirs( ).experimental( "userdata.raw" )

   vbmeta_image = projects_map["aosp"].dirs( ).product( "vbmeta.img" )
   vbmeta_system_image = projects_map["aosp"].dirs( ).product( "vbmeta_system.img" )

   boot_part_num = 1
   partitions = [
      pfw.image.Drive.Partition( clone_from = boot_image, label = "boot" ),
      # pfw.image.Drive.Partition( clone_from = super_image, label = "super" ),
      # pfw.image.Drive.Partition( clone_from = userdata_image, label = "userdata" ),
      # pfw.image.Drive.Partition( size = pfw.size.SizeGigabyte, label = "cache", fs = "ext4" ),
      # pfw.image.Drive.Partition( size = pfw.size.SizeGigabyte, label = "metadata", fs = "ext4" ),
      # pfw.image.Drive.Partition( size = pfw.size.SizeGigabyte, label = "misc", fs = "ext4" ),
      # pfw.image.Drive.Partition( clone_from = vbmeta_image, label = "vbmeta_a" ),
      # pfw.image.Drive.Partition( clone_from = vbmeta_system_image, label = "vbmeta_system_a" ),
   ]

   mmc: pfw.image.Drive = pfw.image.Drive( configuration.LINUX_IMAGE_DRIVE.file( ) )
   mmc.create( partitions = partitions, force = True )
   mmc.attach( )
   mmc.init( partitions, bootable = boot_part_num )
   mmc.info( )
   mmc.detach( )
# def mkdrive

def run_arm64( **kwargs ):
   kw_drive = kwargs.get( "drive", None )

   command: str = qemu.build_parameters( arch = "arm64" )
   command += f" -drive if=none,index=0,id=main,file={kw_drive}"
   command += f" -device virtio-blk-pci,modern-pio-notify,drive=main"

   qemu.run( command, arch = "arm64", **kwargs )
# run_arm64



def start( projects_map: dict, **kwargs ):
   kw_bios = kwargs.get( "bios", True )
   kw_gdb = kwargs.get( "gdb", False )

   if True == kw_bios:
      run_arm64(
            bios = projects_map["uboot"].dirs( ).product( "u-boot.bin" ),
            drive = configuration.LINUX_IMAGE_DRIVE.file( ),
            gdb = kw_gdb
         )
   else:
      run_arm64(
            kernel = projects_map["kernel"].dirs( ).deploy( "Image" ),
            initrd = projects_map["buildroot"].dirs( ).deploy( "rootfs.cpio" ),
            append = "loglevel=7 debug printk.devkmsg=on drm.debug=0x0 console=ttyAMA0",
            dtb = configuration.DTB_PATH,
            drive = configuration.LINUX_IMAGE_DRIVE.file( ),
            gdb = kw_gdb
         )
# def start

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






def build_emulator_parameters_trout( projects_map, **kwargs ):
   kw_drive = kwargs.get( "drive", None )
   kw_arch = projects_map["aosp"].config( ).arch( )

   PARAMETERS = f"" \
      + f" -serial mon:stdio" \
      + f" -nodefaults" \
      + f" -no-reboot" \
      + f" -d guest_errors"

   if "x86" == kw_arch:
      PARAMETERS = PARAMETERS + f" -enable-kvm"
      PARAMETERS = PARAMETERS + f" -smp cores=2"
      PARAMETERS = PARAMETERS + f" -m 8192"
   elif "arm64" == kw_arch:
      PARAMETERS = PARAMETERS + f" -machine virt"
      PARAMETERS = PARAMETERS + f" -cpu cortex-a53"
      PARAMETERS = PARAMETERS + f" -smp cores=4"
      PARAMETERS = PARAMETERS + f" -m 8192"

   IMAGE_DEVICE_TYPE = f"virtio-blk-pci,modern-pio-notify,iothread=disk-iothread"
   IMAGE_DEVICES_MAIN = f"" \
      + f" -drive if=none,index=0,id=main,file={kw_drive}" \
      + f" -device {IMAGE_DEVICE_TYPE},drive=main"

   NETWORK_NETDEV_USER = f"" \
      + f" -netdev user,id=eth0_inet,hostfwd=tcp::5550-:5555,ipv6=off" \
      + f" -device virtio-net-pci,netdev=eth0_inet,id=android"

   NETWORK_NETDEV_BRIDGE = f"" \
      + f" -netdev bridge,id=eth0_inet,br=virbr0,helper=/mnt/dev/git/qemu/build/qemu-bridge-helper" \
      + f" -device virtio-net-pci,netdev=eth0_inet,id=android"

   NETWORK_NETDEV_TAP = f"" \
      + f" -netdev tap,id=eth0_inet,ifname=ethernet_tap,script=no,downscript=no,vhost=on" \
      + f" -device virtio-net-pci-non-transitional,netdev=eth0_inet,id=android"

   NETWORK_OBJECT_DUMP = f"" \
      + f" -object filter-dump,id=f1,netdev=eth0_inet,file=/mnt/dev/android/logs/net_dump/eth0_inet_dump_$(date '+%Y-%m-%d_%H:%M:%S').dat" \

   NETWORK_NET_USER = f"" \
      + f" -net user" \
      + f" -net nic" \

   NETWORK_NET_BRIDGE = f"" \
      + f" -net bridge,br=virbr0,helper=/mnt/dev/git/qemu/build/qemu-bridge-helper" \
      + f" -net nic,model=virtio"

   PCI_KBD_MOUSE = f"" \
      + " -device virtio-keyboard-pci" \
      + " -device virtio-mouse-pci"

   USB_BUS = f"" \
      + " -usb" \

   USB_KBD_MOUSE = f"" \
      + " -usb" \
      + " -device usb-kbd" \
      + " -device usb-mouse" \

   AUDIO_DEVICES = f"" \
      + " -device intel-hda" \
      + " -device hda-duplex,audiodev=snd0" \
      + " -audiodev alsa,id=snd0,out.dev=default" \
      + " -device virtio-snd-pci,disable-legacy=on,audiodev=snd0"

   CHAR_DEVICES = f"" \
      + " -device virtio-serial-pci,ioeventfd=off" \
      + " -chardev null,id=forhvc0" \
      + " -device virtconsole,chardev=forhvc0" \
      + " -chardev null,id=forhvc1" \
      + " -device virtconsole,chardev=forhvc1"

   OTHER_DEVICES = f"" \
      + " -device virtio-gpu-gl-pci" \
      + " -display gtk,gl=on,show-cursor=on" \
      + " -device nec-usb-xhci,id=xhci" \
      + " -device sdhci-pci" \
      + " -object iothread,id=disk-iothread" \
      + " -device virtio-rng-pci"

   command: str = ""\
      + f" {PARAMETERS}" \
      + f" {IMAGE_DEVICES_MAIN}" \
      + f" {NETWORK_NETDEV_USER}" \
      + f" {USB_BUS}" \
      + f" {AUDIO_DEVICES}" \
      + f" {CHAR_DEVICES}" \
      + f" {OTHER_DEVICES}"

   return command
# def build_emulator_parameters_trout

def build_bootconfig_trout( **kwargs ):
   kw_vbmeta_digest = "61344eefe85d31337ffda864c567f529fc18ec1bafa240bb1f46bd561f39a053"

   cmdline = f""
   cmdline += f" androidboot.qemu=1"
   cmdline += f" androidboot.selinux=permissive"
   cmdline += f" androidboot.fstab_suffix=trout"
   cmdline += f" androidboot.hardware=cutf_cvm"
   cmdline += f" androidboot.slot_suffix=_a"
   cmdline += f" androidboot.vbmeta.size=5568"
   cmdline += f" androidboot.vbmeta.hash_alg=sha256"
   cmdline += f" androidboot.vbmeta.digest={kw_vbmeta_digest}"
   cmdline += f" androidboot.hardware.gralloc=minigbm"
   cmdline += f" androidboot.hardware.hwcomposer=drm_minigbm"
   cmdline += f" androidboot.hardware.egl=mesa"
   cmdline += f" androidboot.logcat=*:V"
   cmdline += f" androidboot.vendor.vehiclehal.server.cid=2"
   cmdline += f" androidboot.vendor.vehiclehal.server.port=9300"
   cmdline += f" androidboot.vendor.vehiclehal.server.psf=/data/data/power.file"
   cmdline += f" androidboot.vendor.vehiclehal.server.pss=/data/data/power.socket"
   # cmdline += f" androidboot.first_stage_console=1"
   # cmdline += f" androidboot.force_normal_boot=1"

   if "x86" == kw_arch:
      cmdline += f" androidboot.boot_devices=pci0000:00/0000:00:02.0"
   elif "arm64" == kw_arch:
      cmdline += f" androidboot.boot_devices=4010000000.pcie"

   pfw.console.debug.trace( "cmdline = '%s'" % (cmdline) )
   return cmdline
# def build_cmdline_trout

def start_trout( projects_map: dict, **kwargs ):
   kw_bios = kwargs.get( "bios", True )
   kw_gdb = kwargs.get( "gdb", False )

   command = build_emulator_parameters_trout(
         projects_map, 
         drive = configuration.LINUX_IMAGE_DRIVE.file( ),
         debug = True
      )

   qemu.run(
         command,
         arch = "arm64",
         bios = projects_map["uboot"].dirs( ).product( "u-boot.bin" ),
         # kernel = projects_map["aosp"].dirs( ).product( "kernel" ),
         # initrd = projects_map["aosp"].dirs( ).experimental( "ramdisk.img" ),
         # append = build_cmdline_trout( projects_map ),
         gdb = kw_gdb,
      )
# def start_trout



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
   pfw.shell.run_and_wait_with_status( command, args = parameters, output = pfw.shell.eOutput.PTY )
# run_vexpress_ca9x4
