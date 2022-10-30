#!/usr/bin/python3

import pfw.console
import pfw.shell



def run( **kwargs ):
   kw_ip = kwargs.get( "ip", "localhost" )
   kw_port = kwargs.get( "port", 1234 )
   kw_arch = kwargs.get( "arch", None )
   kw_file = kwargs.get( "file", None )
   kw_lib_path = kwargs.get( "lib_path", None )
   kw_src_path = kwargs.get( "src_path", None )
   kw_load_symbols = kwargs.get( "load_symbols", None ) # { str: [ ] }
   kw_break_names = kwargs.get( "break_names", None ) # [ ]
   kw_break_addresses = kwargs.get( "break_addresses", None ) # [ ]
   kw_break_code = kwargs.get( "break_code", None ) # { str: [ ] }
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
   # Processing specific named kwargs parameters and filling/overriding "-ex" parameters
   command += f" -ex \"target remote {kw_ip}:{str(kw_port)}\""
   if None != kw_arch:
      command += f" -ex \"set architecture {kw_arch}\""
   if None != kw_file:
      command += f" -ex \"file {kw_file}\""
   if None != kw_lib_path:
      command += f" -ex \"set solib-search-path {kw_lib_path}\""
   if None != kw_src_path:
      command += f" -ex \"set directories {kw_src_path}\""
   if None != kw_load_symbols:
      for symbols_file in kw_load_symbols:
         for symbols_offset in kw_load_symbols[ symbols_file ]:
            if None == symbols_offset:
               symbols_offset = ""
            command += f" -ex \"add-symbol-file {symbols_file} {symbols_offset}\""
   if None != kw_break_names:
      for break_name in kw_break_names:
         command += f" -ex \"b {break_name}\""
   if None != kw_break_addresses:
      for break_addr in kw_break_addresses:
         command += f" -ex \"b *{break_addr}\""
   if None != kw_break_code:
      for break_file in kw_break_code:
         for break_line in kw_break_code[ break_file ]:
            command += f" -ex \"b {break_file}:{break_line}\""

   command += f" -ex \"info breakpoints\""
   command += f" -ex \"info files\""

   pfw.shell.execute( command, output = pfw.shell.eOutput.PTY )
# run
