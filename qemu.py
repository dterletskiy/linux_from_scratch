#!/usr/bin/python3

import os
import datetime

import pfw.console
import pfw.shell

import dt



EMULATOR: str = ""

def init( qemu_path: str ):
   global EMULATOR
   EMULATOR = qemu_path
# def init

def qemu( emulator: str, **kwargs ):
   kw_qemu_path = kwargs.get( "qemu_path", None )

   if None == kw_qemu_path:
      kw_qemu_path = EMULATOR

   return os.path.join( kw_qemu_path, emulator )
# def qemu

def run( parameters, **kwargs ):
   kw_emulator = kwargs.get( "emulator", None )
   kw_bios = kwargs.get( "bios", None )
   kw_kernel = kwargs.get( "kernel", None )
   kw_initrd = kwargs.get( "initrd", None )
   kw_append = kwargs.get( "append", None )
   kw_dtb = kwargs.get( "dtb", None )
   kw_cwd = kwargs.get( "cwd", None )
   kw_arch = kwargs.get( "arch", None )
   kw_gdb = kwargs.get( "gdb", False )
   kw_dump_dtb = kwargs.get( "dump_dtb", False )
   kw_dump_dtb_path = kwargs.get( "dump_dtb_path", f"/tmp/dtb/{str(datetime.datetime.now( ))}.dtb" )
   kw_output = kwargs.get( "output", pfw.shell.eOutput.PTY )

   if kw_dump_dtb:
      pfw.shell.execute( f"mkdir -p {os.path.dirname( kw_dump_dtb_path )}", output = kw_output )

   if "x86" == kw_arch:
      kw_emulator = qemu( f"qemu-system-x86_64", qemu_path = kw_emulator )
   elif "x86_64" == kw_arch:
      kw_emulator = qemu( f"qemu-system-x86_64", qemu_path = kw_emulator )
   elif "arm" == kw_arch or "arm32" == kw_arch:
      kw_emulator = qemu( f"qemu-system-arm", qemu_path = kw_emulator )
   elif "arm64" == kw_arch or "aarch64" == kw_arch:
      kw_emulator = qemu( f"qemu-system-aarch64", qemu_path = kw_emulator )

   command: str = f"{kw_emulator} {parameters}"
   command += f" -bios {kw_bios}" if kw_bios else ""
   command += f" -kernel {kw_kernel}" if kw_kernel else ""
   command += f" -initrd {kw_initrd}" if kw_initrd else ""
   command += f" -append \"{kw_append}\"" if kw_append else ""
   command += f" -dtb {kw_dtb}" if kw_dtb else ""
   command += f" -machine dumpdtb={kw_dump_dtb_path}" if kw_dump_dtb else ""
   command += f" -s -S" if kw_gdb else ""

   result = pfw.shell.execute( command, cwd = kw_cwd, sudo = False, output = kw_output )

   if True == kw_dump_dtb:
      dt.decompile( kw_dump_dtb_path, kw_dump_dtb_path + ".dts" )

   return result["code"]
# def run



def build_parameters( **kwargs ):
   kw_arch = kwargs.get( "arch", "arm64" )
   kw_nographic = kwargs.get( "nographic", False )
   kw_nodefaults = kwargs.get( "nodefaults", False )

   parameters = f""
   parameters += f" -serial mon:stdio"
   parameters += f" -no-reboot"
   parameters += f" -d guest_errors"

   # parameters += f" -chardev socket,id=qemu-monitor,host=localhost,port=7777,server=on,wait=off,telnet=on"
   # parameters += f" -mon qemu-monitor,mode=readline"

   if True == kw_nodefaults:
      parameters += f" -nodefaults"

   if True == kw_nographic:
      parameters += f" -nographic"

   if kw_arch in [ "x86", "x86_64" ]:
      parameters += f" -enable-kvm"
      parameters += f" -smp cores=2"
      parameters += f" -m 8192"
   elif kw_arch in [ "arm", "arm32", "arm64", "aarch64" ]:
      parameters += f" -machine virt"
      parameters += f" -machine virtualization=true"
      parameters += f" -cpu cortex-a53"
      parameters += f" -smp cores=4"
      parameters += f" -m 8192"

   return parameters
# def build_parameters


def build_kernel_parameters( **kwargs ):
   kw_arch = kwargs.get( "arch", "arm64" )
   kw_max_loop = kwargs.get( "max_loop", 100 )
   kw_bootconfig = kwargs.get( "bootconfig", True )
   kw_debug = kwargs.get( "debug", True )

   cmdline = f"loop.max_loop={kw_max_loop}"
   if True == kw_debug:
      cmdline += f" loglevel=7"
      cmdline += f" printk.devkmsg=on"
      # cmdline += f" earlyprintk"
      # cmdline += f" debug"
      # cmdline += f" drm.debug=0x1FF"
   else:
      cmdline += f" loglevel=1"

   if True == kw_bootconfig:
      cmdline += f" bootconfig"

   if kw_arch in [ "x86", "x86_64" ]:
      cmdline += f" console=ttyS0,38400"
   elif kw_arch in [ "arm", "arm32", "arm64", "aarch64" ]:
      cmdline += f" console=ttyAMA0"


   pfw.console.debug.trace( "cmdline = '%s'" % (cmdline) )
   return cmdline
# def build_kernel_parameters
