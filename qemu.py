#!/usr/bin/python3

import pfw.shell

import configuration
import dt



EMULATOR = "/mnt/dev/git/qemu/build/"

def run( parameters, **kwargs ):
   kw_emulator = kwargs.get( "emulator", EMULATOR )
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
      kw_emulator = kw_emulator + f"qemu-system-x86_64"
   elif "x86_64" == kw_arch:
      kw_emulator = kw_emulator + f"qemu-system-x86_64"
   elif "arm" == kw_arch or "arm32" == kw_arch:
      kw_emulator = kw_emulator + f"qemu-system-arm"
   elif "arm64" == kw_arch or "aarch64" == kw_arch:
      kw_emulator = kw_emulator + f"qemu-system-aarch64"

   command: str = f"{kw_emulator} {parameters}"

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
# def run