import os
import re
import git
from enum import Enum

import pfw.base
import pfw.console
import pfw.archive
import pfw.shell
import pfw.git

import base
import tools
import linux.base



BUSYBOX_LINK_PATTERN = "https://busybox.net/downloads/busybox-VERSION.tar.bz2"
BUSYBOX_NAME_PATTERN = "busybox-VERSION"
BUSYBOX_ARCHIVE_PATTERN = "busybox-VERSION.tar.bz2"



class BusyBox:
   def __init__( self, config: linux.base.Configuration, root_dir: str, version: str, **kwargs ):
      self.reset( )
      self.__config = config
      self.__version = version
      self.__name = BUSYBOX_NAME_PATTERN.replace( "VERSION", self.__version )
      self.__url = BUSYBOX_LINK_PATTERN.replace( "VERSION", self.__version )
      self.__archive_name = BUSYBOX_ARCHIVE_PATTERN.replace( "VERSION", self.__version )
      self.__directories = linux.base.Directories( self.__config, root_dir, self.__name, product_subdir = "_install" )
   # def __init__

   def __del__( self ):
      pass
   # def __del__

   def __setattr__( self, attr, value ):
      attr_list = [ i for i in BusyBox.__dict__.keys( ) ]
      if attr in attr_list:
         self.__dict__[ attr ] = value
         return
      raise AttributeError
   # def __setattr__

   def __str__( self ):
      attr_list = [ i for i in BusyBox.__dict__.keys( ) if i[:2] != pfw.base.class_ignore_field ]
      vector = [ ]
      for attr in attr_list:
         vector.append( str( attr ) + " = " + str( self.__dict__.get( attr ) ) )
      name = "BusyBox { " + ", ".join( vector ) + " }"
      return name
   # def __str__

   def info( self, **kwargs ):
      tabulations: int = kwargs.get( "tabulations", 0 )
      pfw.console.debug.info( self.__class__.__name__, ":", tabs = ( tabulations + 0 ) )
      pfw.console.debug.info( "version:         \'", self.__version, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "name:            \'", self.__name, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "url:             \'", self.__url, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "archive name:    \'", self.__archive_name, "\'", tabs = ( tabulations + 1 ) )
      self.__directories.info( tabulations + 1 )
   # def info

   def reset( self ):
      pass
   # def reset

   def download( self ):
      pfw.base.download( self.__url, self.__directories.download( ) )
   # def download

   def extract( self ):
      pfw.shell.run_and_wait_with_status(
              "tar", "-xvf"
            , self.__directories.download( self.__archive_name )
            , "--checkpoint=100"
            , "--directory=" + self.__directories.source( ".." )
         )
   # def extract

   def sync( self, **kwargs ):
      self.download( )
      self.extract( )
   # def sync

   def default_config( self ):
      config: str = None
      if "arm" == self.__config.arch( ):
         config = "defconfig"
      elif "arm64" == self.__config.arch( ):
         config = "defconfig"
      else:
         config = "defconfig"

      return config
   # def default_config

   def configure( self, **kwargs ):
      kw_targets = kwargs.get( "targets", ["default", "menuconfig"] )

      if 0 == len(kw_targets):
         kw_targets = ["default", "menuconfig"]

      command = "make"
      command += f" O={self.__directories.build( )}"
      command += f" -C {self.__directories.source( )}"
      command += f" ARCH={self.__config.arch( )}"
      command += f" CROSS_COMPILE={self.__config.compiler( )}"

      for target in kw_targets:
         if "default" == target:
            target = self.default_config( )
         pfw.shell.run_and_wait_with_status( command, target, print = False, collect = False )
   # def configure

   def build( self, **kwargs ):
      target = kwargs.get( "build_target", "all" )

      command = "make"
      command += f" O={self.__directories.build( )}"
      command += f" -C {self.__directories.source( )}"
      command += f" ARCH={self.__config.arch( )}"
      command += f" CROSS_COMPILE={self.__config.compiler( )}"
      command += f" -j{self.__config.cores( )}"

      pfw.shell.run_and_wait_with_status( command, target, output = pfw.shell.eOutput.PTY )

      self.install( )
   # def build

   def install( self ):
      command = "make"
      command += f" O={self.__directories.build( )}"
      command += f" -C {self.__directories.source( )}"
      command += f" ARCH={self.__config.arch( )}"
      command += f" CROSS_COMPILE={self.__config.compiler( )}"
      command += f" -j{self.__config.cores( )}"

      pfw.shell.run_and_wait_with_status( command, "install", output = pfw.shell.eOutput.PTY )
   # def build

   def clean( self, **kwargs ):
      target = kwargs.get( "clean_target", "distclean" )

      command = "make"
      command += f" O={self.__directories.build( )}"
      command += f" -C {self.__directories.source( )}"
      command += f" ARCH={self.__config.arch( )}"
      command += f" CROSS_COMPILE={self.__config.compiler( )}"

      pfw.shell.run_and_wait_with_status( command, target, output = pfw.shell.eOutput.PTY )
   # def clean

   def deploy( self, **kwargs ):
      deploy_path = kwargs.get( "deploy_path", None )
      is_create_structure = kwargs.get( "is_create_structure", False )

      if None == deploy_path:
         deploy_path = self.__directories.deploy( )
      else:
         if True != os.path.isdir( deploy_path ):
            pfw.console.debug.error( "deploy path does noe exist: ", deploy_path )
            return None

         if True == is_create_structure:
            deploy_path = os.path.join( deploy_path, self.__config.arch( ), self.__name )
            pfw.shell.run_and_wait_with_status( f"mkdir -p {deploy_path}" )
      pfw.console.debug.info( "deploy -> ", deploy_path )
      pfw.shell.run_and_wait_with_status( f"rm -r {deploy_path}" )
      pfw.shell.run_and_wait_with_status( f"mkdir -p {deploy_path}" )



      rootfs_path = os.path.join( deploy_path, "initramfs" )
      pfw.shell.run_and_wait_with_status( f"mkdir -p {rootfs_path}" )

      files_list: list = [ ]

      for file in files_list:
         pfw.console.debug.trace( "file: '%s' ->\n     '%s'" % ( file, rootfs_path ) )
         pfw.shell.run_and_wait_with_status( f"cp {file} {rootfs_path}" )

      directories_list: list = [
            os.path.join( self.__directories.product( ), "." )
         ]

      for directory in directories_list:
         pfw.console.debug.trace( "directory: '%s' ->\n     '%s'" % ( directory, rootfs_path ) )
         pfw.shell.run_and_wait_with_status( f"cp -r {directory}, {rootfs_path}" )

      pfw.shell.run_and_wait_with_status( f"mkdir -p " + os.path.join( rootfs_path, "lib" ) )
      pfw.shell.run_and_wait_with_status(
           f"cp -r " + self.__config.compiler_path( "lib/." ) + " " + os.path.join( rootfs_path, "lib" )
         )

      pfw.shell.run_and_wait_with_status( f"mkdir -p " + os.path.join( rootfs_path, "dev" ) )
      for index in range( 1, 5 ):
         pfw.shell.run_and_wait_with_status(
              f"sudo -S mknod -m 666 " + os.path.join( rootfs_path, "dev/tty" + str(index) ) + f" c 4 {str(index)}"
            )
      pfw.shell.run_and_wait_with_status(
           f"sudo -S mknod -m 666 " + os.path.join( rootfs_path, "dev/console" ) + f" c 5 1"
         )
      pfw.shell.run_and_wait_with_status(
            f"sudo -S mknod -m 666 " + os.path.join( rootfs_path, "dev/null" ) + f" c 1 3"
         )

      os.system(
         "cd " + rootfs_path + " ; "
         "find . | " +
         "cpio -H newc -ov --owner root:root > " + os.path.join( deploy_path, "initramfs.cpio" )
      )

      pfw.shell.run_and_wait_with_status(
         f"gzip -k " + os.path.join( deploy_path, "initramfs.cpio" )
      )
   # def post_build

   def run( self, **kwargs ):
      command: str = ""

      if "arm" == self.__config.arch( ):
         command += f" -machine virt"
         command += f" -cpu cortex-a15"
      elif "arm64" == self.__config.arch( ):
         command += f" -machine virt"
         command += f" -cpu cortex-a53"

      command += f" -smp cores=1"
      command += f" -m 512M"
      command += f" -nographic"
      command += f" -serial mon:stdio"
      command += f" -no-reboot"
      command += f" -d guest_errors"

      tools.run_qemu(
            command,
            arch = self.__config.arch( ),
            initrd = self.__directories.deploy( "initramfs.cpio" ),
            append = "root=/dev/ram rw rdinit=/sbin/init console=ttyAMA0",
            **kwargs
         )
   # def run

   def action( self, **kwargs ):
      _actions = kwargs.get( "actions", [ ] )
      _actions.append( kwargs.get( "action", base.eAction.none ) )
      pfw.console.debug.info( "actions: ", _actions )

      for _action in _actions:
         if base.eAction.sync == _action:
            self.sync( **kwargs )
         elif base.eAction.clean == _action:
            self.clean( **kwargs )
         elif base.eAction.config == _action:
            self.configure( **kwargs )
         elif base.eAction.build == _action:
            self.build( **kwargs )
         elif base.eAction.deploy == _action:
            self.deploy( **kwargs )
         elif base.eAction.run == _action:
            self.run( **kwargs )
         elif base.eAction.run_debug == _action:
            self.run( debug = True, **kwargs )
         elif base.eAction.info == _action:
            self.info( **kwargs )
         elif base.eAction.none == _action:
            pass
         else:
            pfw.console.debug.warning( "unsuported action: ", _action )
   # def action



   def dirs( self ):
      return self.__directories
   # def dirs

   def config( self ):
      return self.__config
   # def config



   __version: str = None
   __name: str = None
   __url: str = None
   __archive_name: str = None
   __directories: linux.base.Directories = None
   __config: linux.base.Configuration = None
# class BusyBox
