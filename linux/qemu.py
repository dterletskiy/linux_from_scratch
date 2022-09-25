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
import qemu
import linux.base



QEMU_GITHUB_REPO = "https://github.com/qemu/qemu.git"



class Qemu:
   def __init__( self, config: linux.base.Configuration, root_dir: str, **kwargs ):
      self.reset( )
      self.__config = config
      self.__version = kwargs.get( "version", "master" )
      self.__name = kwargs.get( "name", "qemu-" + self.__version )
      self.__url_git = QEMU_GITHUB_REPO
      self.__directories = linux.base.Directories( self.__config, root_dir, self.__name, product_subdir = "arch/" + self.__config.arch( ) + "/boot" )
   # def __init__

   def __del__( self ):
      pass
   # def __del__

   def __setattr__( self, attr, value ):
      attr_list = [ i for i in Qemu.__dict__.keys( ) ]
      if attr in attr_list:
         self.__dict__[ attr ] = value
         return
      raise AttributeError
   # def __setattr__

   def __str__( self ):
      attr_list = [ i for i in Qemu.__dict__.keys( ) if i[:2] != pfw.base.class_ignore_field ]
      vector = [ ]
      for attr in attr_list:
         vector.append( str( attr ) + " = " + str( self.__dict__.get( attr ) ) )
      name = "Qemu { " + ", ".join( vector ) + " }"
      return name
   # def __str__

   def info( self, **kwargs ):
      tabulations: int = kwargs.get( "tabulations", 0 )
      pfw.console.debug.info( self.__class__.__name__, ":", tabs = ( tabulations + 0 ) )
      pfw.console.debug.info( "version:         \'", self.__version, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "name:            \'", self.__name, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "url:             \'", self.__url, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "git repo:        \'", self.__url_git, "\'", tabs = ( tabulations + 1 ) )
      self.__directories.info( tabulations + 1 )
   # def info

   def reset( self ):
      pass
   # def reset

   def clone( self ):
      command = f"git clone"
      if None != self.__version:
         command += f" -b {self.__version}"
      command += f" {self.__url_git} {self.__directories.source( )}"
      pfw.shell.run_and_wait_with_status( command, output = pfw.shell.eOutput.PTY )

      command = f"git submodule init"
      pfw.shell.run_and_wait_with_status( command, output = pfw.shell.eOutput.PTY, cwd = self.__directories.source( ) )

      command = f"git submodule update --recursive"
      pfw.shell.run_and_wait_with_status( command, output = pfw.shell.eOutput.PTY, cwd = self.__directories.source( ) )

      command = f"git submodule status --recursive"
      pfw.shell.run_and_wait_with_status( command, output = pfw.shell.eOutput.PTY, cwd = self.__directories.source( ) )

   # def clone

   def sync( self, **kwargs ):
      self.clone( )
   # def sync

   def configure( self, **kwargs ):
      kw_prefix = kwargs.get( "prefix", self.__directories.deploy( ) )
      kw_options = kwargs.get( "options", [ "--enable-gtk" ] )
      # kw_options = kwargs.get( "options", [ "--enable-gtk", "--static", "--disable-system", "--enable-linux-user" ] )

      command = self.__directories.source( "configure" )
      command += f" --prefix={kw_prefix}"

      for option in kw_options:
         command += f" {option}"

      pfw.shell.run_and_wait_with_status( command, print = False, collect = False, cwd = self.__directories.build( ) )
   # def configure

   def build( self, **kwargs ):
      kw_targets = kwargs.get( "targets", [ ] )

      if None == kw_targets or 0 == len(kw_targets):
         kw_targets = [ ]

      targets: str = ""
      for target in kw_targets:
         targets += f"{target} "

      command = "make"
      command += f" -j{self.__config.cores( )}"

      pfw.shell.run_and_wait_with_status( command, targets, output = pfw.shell.eOutput.PTY, cwd = self.__directories.build( ) )
   # def build

   def clean( self, **kwargs ):
      kw_targets = kwargs.get( "targets", ["clean", "distclean", "mrproper"] )

      if None == kw_targets or 0 == len(kw_targets):
         kw_targets = ["clean", "distclean", "mrproper"]

      targets: str = ""
      for target in kw_targets:
         targets += f"{target} "

      command = "make"

      pfw.shell.run_and_wait_with_status( command, targets, output = pfw.shell.eOutput.PTY, cwd = self.__directories.build( ) )
   # def clean

   def deploy( self, **kwargs ):
      deploy_path = kwargs.get( "deploy_path", None )

      command = "make install"
      pfw.shell.run_and_wait_with_status( command, output = pfw.shell.eOutput.PTY, cwd = self.__directories.build( ) )

      return deploy_path
   # def deploy

   def run( self, **kwargs ):
      pass
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

   def version( self ):
      return self.__version
   # def version



   __version: str = None
   __name: str = None
   __url: str = None
   __url_git: str = None
   __archive_name: str = None
   __directories: linux.base.Directories = None
   __config: linux.base.Configuration = None
# class Qemu