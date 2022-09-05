from enum import IntEnum



class eAction( IntEnum ):
   info        = 0
   sync        = 1
   clean       = 2
   config      = 3
   build       = 4
   deploy      = 6
   run         = 7
   run_debug   = 8
   run_gdb     = 9
   none        = 0xFFFFFFFF
# class eAction
