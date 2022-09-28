#!/usr/bin/python3



# Examples:
# 
# CONFIG=./configuration.cfg 
# PROJECT=u-boot
# ARCH=arm64
# PFW=/mnt/dev/TDA/python_fw
# 
# ./linux_kernel.py --config=${CONFIG} --include=${PFW} --arch=${ARCH} --project=${PROJECT} --action=info
# ./linux_kernel.py --config=${CONFIG} --include=${PFW} --arch=${ARCH} --project=${PROJECT} --action=sync
# ./linux_kernel.py --config=${CONFIG} --include=${PFW} --arch=${ARCH} --project=${PROJECT} --action=clean
# ./linux_kernel.py --config=${CONFIG} --include=${PFW} --arch=${ARCH} --project=${PROJECT} --action=config
# ./linux_kernel.py --config=${CONFIG} --include=${PFW} --arch=${ARCH} --project=${PROJECT} --action=config --target=menuconfig
# ./linux_kernel.py --config=${CONFIG} --include=${PFW} --arch=${ARCH} --project=${PROJECT} --action=build
# ./linux_kernel.py --config=${CONFIG} --include=${PFW} --arch=${ARCH} --project=${PROJECT} --action=deploy
# 
# ./linux_kernel.py --config=${CONFIG} --include=${PFW} --arch=${ARCH} --action=mkimage
# ./linux_kernel.py --config=${CONFIG} --include=${PFW} --arch=${ARCH} --action=start
# ./linux_kernel.py --config=${CONFIG} --include=${PFW} --arch=${ARCH} --action=gdb
# 
# In case if variable "INCLUDE" defined with path to "pfw" "--include" option could be omitted.
# If "INCLUDE" variable defined several times in configuration file all mentioned values will be used.



import os
import sys
import getopt
import argparse
import re



##########################################################################
#                                                                        #
#                          Begin configuration                           #
#                                                                        #
##########################################################################

MIN_PYTHON = (3, 8)
if sys.version_info < MIN_PYTHON:
   print( "Python minimal required version is %s.%s" % MIN_PYTHON )
   print( "Current version is %s.%s" % ( sys.version_info.major, sys.version_info.minor ) )
   sys.exit( )



class ApplicationDataNew:
   def info( self, **kwargs ):
      print( self.__class__.__name__, ":" )
      print( "   config:         \'", self.config, "\'" )
      print( "   includes:       \'", self.includes, "\'" )
      print( "   arch:           \'", self.arch, "\'" )
      print( "   actions:        \'", self.actions, "\'" )
      print( "   projects:       \'", self.projects, "\'" )
      print( "   targets:        \'", self.targets, "\'" )

      print( "   antlr_jar:      \'", self.antlr_jar, "\'" )
      print( "   antlr_outdir:   \'", self.antlr_outdir, "\'" )
      print( "   antlr_lexers:   \'", self.antlr_lexers, "\'" )
      print( "   antlr_parsers:  \'", self.antlr_parsers, "\'" )
   # def info

   __config: str = None
   __includes: list = [ ]
   __arch: str = None
   __actions: list = [ ]
   __projects: list = [ ]
   __targets: list = [ ]

   __antlr_jar: str = None
   __antlr_outdir: str = None
   __antlr_lexers: list = [ ]
   __antlr_parsers: list = [ ]
# class ApplicationData




class ApplicationData:
   def info( self, **kwargs ):
      print( self.__class__.__name__, ":" )
      print( "   config:         \'", self.config, "\'" )
      print( "   includes:       \'", self.includes, "\'" )
      print( "   arch:           \'", self.arch, "\'" )
      print( "   actions:        \'", self.actions, "\'" )
      print( "   projects:       \'", self.projects, "\'" )
      print( "   targets:        \'", self.targets, "\'" )

      print( "   antlr_jar:      \'", self.antlr_jar, "\'" )
      print( "   antlr_outdir:   \'", self.antlr_outdir, "\'" )
      print( "   antlr_lexers:   \'", self.antlr_lexers, "\'" )
      print( "   antlr_parsers:  \'", self.antlr_parsers, "\'" )
   # def info

   config: str = None
   includes: list = [ ]
   arch: str = None
   actions: list = [ ]
   projects: list = [ ]
   targets: list = [ ]

   antlr_jar: str = None
   antlr_outdir: str = None
   antlr_lexers: list = [ ]
   antlr_parsers: list = [ ]
# class ApplicationData




class Description:
   help = "Show this help menu."
   config = "Configuration"
   include = "Additional directory to search import packages"
   arch = "Architecture"
   action = "Action"
   project = "Project"
   target = "Target"

   antlr_jar = "Path to antlr jar file"
   antlr_outdir = "Output directory for generated lexer, parser, listener and visitor files."
   antlr_lexer = "Path to lexer grammer files"
   antlr_parser = "Path to parser grammer files"
# class Description
g_description = Description( )



def cmdline_argparse( argv ):
   print( "Number of arguments:", len(sys.argv) )
   print( "Argument List:", str(sys.argv) )

   application_data = ApplicationData( )

   parser = argparse.ArgumentParser( description = 'App description' )

   parser.add_argument( "--version", action = "version", version = '%(prog)s 2.0' )

   parser.add_argument( "--config", dest = "config", type = str, action = "store", required = False, help = g_description.config )

   parser.add_argument( "--include", dest = "include", type = str, action = "append", help = g_description.include )

   parser.add_argument( "--arch", dest = "arch", type = str, action = "store", required = False, help = g_description.arch )
   parser.add_argument( "--action", dest = "action", type = str, action = "store", required = False, help = g_description.action )
   parser.add_argument( "--project", dest = "project", type = str, action = "store", required = False, help = g_description.project )
   parser.add_argument( "--target", dest = "target", type = str, action = "store", required = False, help = g_description.target )

   parser.add_argument( "--antlr_jar", dest = "antlr_jar", type = str, action = "store", help = g_description.antlr_jar )
   parser.add_argument( "--antlr_outdir", dest = "antlr_outdir", type = str, action = "store", help = g_description.antlr_outdir )
   parser.add_argument( "--antlr_lexer", dest = "antlr_lexer", type = str, action = "append", help = g_description.antlr_lexer )
   parser.add_argument( "--antlr_parser", dest = "antlr_parser", type = str, action = "append", help = g_description.antlr_parser )

   # parser.print_help( )
   try:
      argument = parser.parse_args( )
   except argparse.ArgumentError:
      print( 'Catching an ArgumentError' )

   if argument.config:
      print( "config: ", argument.config )
      application_data.config = argument.config

   if argument.include:
      print( "include: ", argument.include )
      application_data.includes.extend( argument.include )

   if argument.arch:
      print( "arch: ", argument.arch )
      application_data.arch = argument.arch

   if argument.action:
      print( "action: ", argument.action )
      application_data.actions = argument.action.split( "," )

   if argument.project:
      print( "project: ", argument.project )
      application_data.projects = argument.project.split( "," )

   if argument.target:
      print( "target: ", argument.target )
      application_data.targets = argument.target.split( "," )

   if argument.antlr_jar:
      print( "antlr_jar: ", argument.antlr_jar )
      application_data.antlr_jar = argument.antlr_jar

   if argument.antlr_outdir:
      print( "antlr_outdir: ", argument.antlr_outdir )
      application_data.includes.append( argument.antlr_outdir )
      application_data.antlr_outdir = argument.antlr_outdir

   if argument.antlr_lexer:
      print( "antlr_lexer: ", argument.antlr_lexer )
      application_data.antlr_lexers.extend( argument.antlr_lexer )

   if argument.antlr_parser:
      print( "antlr_parser: ", argument.antlr_parser )
      application_data.antlr_parsers.extend( argument.antlr_parser )

   return application_data
# def cmdline_argparse



def configure( app_data ):
   config_variables: dict = { }

   if None != app_data.config:
      pattern: str = r"^\s*(.*)\s*:\s*(.*)\s*$"
      config_file = open( app_data.config, "r" )
      for line in config_file:
         match = re.match( pattern, line )
         if match:
            var_name = match.group( 1 )
            var_value = match.group( 2 )
            if "INCLUDE" == var_name:
               app_data.includes.append( var_value )
            elif "ANTLR_JAR" == var_name and None == app_data.antlr_jar:
               app_data.antlr_jar = var_value
            elif "ANTLR_OUTDIR" == var_name and None == app_data.antlr_outdir:
               app_data.antlr_outdir = var_value
            elif "ANTLR_LEXER" == var_name:
               app_data.antlr_lexers.append( var_value )
            elif "ANTLR_PARSER" == var_name:
               app_data.antlr_parsers.append( var_value )
            else:
               config_variables[ var_name ] = var_value
      config_file.close( )



   for path in reversed( app_data.includes ):
      sys.path.insert( 0, path )

   return config_variables
# def configure



g_app_data: ApplicationData = cmdline_argparse( sys.argv[1:] )
g_config_variables: dict = configure( g_app_data )
g_app_data.info( )



import pfw.console
import pfw.shell
import pfw.size
import pfw.image

import base
import configuration
import dt
import tools
import qemu
import antlr
import linux.base
import linux.uboot
import linux.buildroot
import linux.busybox
import linux.kernel
import linux.xen
import linux.qemu
import aosp.base
import aosp.aosp



configuration.init( g_config_variables )
qemu.init( configuration.QEMU_BIN_DIR )
antlr.init( g_app_data.antlr_jar )
antlr_gendir = antlr.gen_grammar( lexers = g_app_data.antlr_lexers, parsers = g_app_data.antlr_parsers )
sys.path.insert( 0, antlr_gendir )



import generator.pdl.parser



ENVIRONMENT = dict( os.environ )
ENVIRONMENT["LFS_VERSION"] = str(1.0)
pfw.shell.run_and_wait_with_status( "/bin/echo ${LFS_VERSION}", env = ENVIRONMENT, shell = True )

##########################################################################
#                                                                        #
#                           End configuration                            #
#                                                                        #
##########################################################################









def init_actions( ):
   actions_map: dict = {
      "info"         : [ base.eAction.info ],
      "sync"         : [ base.eAction.sync ],
      "clean"        : [ base.eAction.clean ],
      "config"       : [ base.eAction.config ],
      "build"        : [ base.eAction.build ],
      "deploy"       : [ base.eAction.deploy ],
      "mkall"        : [ base.eAction.info, base.eAction.clean, base.eAction.config, base.eAction.build, base.eAction.deploy ],
      "run"          : [ base.eAction.run ],
      "run_debug"    : [ base.eAction.run_debug ],
      "run_gdb"      : [ base.eAction.run_gdb ],
   }

   return actions_map
# def init_actions

def main( app_data: ApplicationData ):
   projects_map = generator.pdl.parser.parse( configuration.PDL )
   actions_map = init_actions( )

   projects: list = [ ]
   for project in app_data.projects:
      if "all" == project:
         projects = projects_map.values( )
         break
      projects.append( projects_map[ project ] )

   actions: list = [ ]
   for action in app_data.actions:
      # Processing extended actions
      if "gdb" == action:
         tools.debug( projects_map, project_name = "uboot" )
         sys.exit( )
      elif "start" == action:
         # tools.start_trout(
         tools.start(
               projects_map,
               bios = True,
               # gdb = True
            )

         # projects_map["aosp"].run( debug = True )

         sys.exit( )
      elif "mkimage" == action:
         tools.mkpartition( projects_map )
         tools.mkdrive( projects_map )

         # projects_map["aosp"].build_ramdisk( )
         # projects_map["aosp"].build_main_image( )

         sys.exit( )
      else:
         # Collecting standart actions
         actions.extend( actions_map[ action ] )

   targets: list = app_data.targets



   for project in projects:
      kw: dict = { }
      if type( project ) == type( projects_map["kernel"] ):
         kw["configs"] = {
               # "CONFIG_CMDLINE": "\"console=ttyAMA0\"",
               # "CONFIG_INITRAMFS_SOURCE": "\"" + projects["buildroot"].dirs( ).product( "rootfs.cpio" ) + "\"",
            }
      elif type( project ) == type( projects_map["buildroot"] ) or type( project ) == type( projects_map["busybox"] ):
         if "arm" == project.config( ).arch( ) or "arm32" == project.config( ).arch( ):
            kernel_file = "zImage"
         elif "arm64" == project.config( ).arch( ) or "aarch64" == project.config( ).arch( ):
            kernel_file = "Image"
         kw["kernel"] = os.path.join( projects_map["kernel"].dirs( ).product( ), kernel_file )
      project.action( actions = actions, targets = targets, **kw )


# def main



if __name__ == "__main__":
   main( g_app_data )

   pfw.console.debug.error( "----- END -----" )
