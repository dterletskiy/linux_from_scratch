#!/usr/bin/python3

import pfw.shell



def compile( in_dts: str, out_dtb: str ):
   command = f"dtc -I dts -O dtb -o {out_dtb} {in_dts}"

   pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )
# def compile

def decompile( in_dtb: str, out_dts: str ):
   command = f"dtc -I dtb -O dts -o {out_dts} {in_dtb}"

   pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )
# def decompile
