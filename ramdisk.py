#!/usr/bin/python3

import os

import pfw.console
import pfw.shell



# Parameters:
#  - source - directory with content to be packed
#  - destination - resulting ramdisk file
#  - bootconfig - map { "tool": <tool_path>, "config": <config_path> }
#     - tool_path - path to tool for adding bootconfig parameters to ramdisk.
#     - config_path - path to file with bootconfig parameters for bootconfig tool.
def pack( source: str, destination: str, **kwargs ):
   kw_bootconfig = kwargs.get( "bootconfig", None )

   command = f"find . ! -name . | LC_ALL=C sort | cpio -o -H newc -R root:root | lz4 -l -12 --favor-decSpeed > {destination};"
   pfw.shell.execute( command, cwd = source, output = pfw.shell.eOutput.PTY )

   if None != kw_bootconfig and isinstance( kw_bootconfig, dict ):
      pfw.console.debug.info( "Adding bootconfig to ramdisk" )
      kw_bootconfig["tool"]( destination, clear = True, add = kw_bootconfig["config"] )
# def pack

# Parameters:
#  - source - ramdisk file
#  - destination - directory for extracting content from ramdisk
def extract( source: str, destination: str, **kwargs ):
   command = f"rm -rf {destination}; mkdir -p {destination}"
   pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )

   command = f" lz4 -d -c {source} | cpio -i"
   pfw.shell.execute( command, cwd = destination, output = pfw.shell.eOutput.PTY )
# def extract
