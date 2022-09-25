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



XEN_ARCHIVE_PATTERN = "xen-VERSION.tar.gz"
XEN_LINK_PATTERN = "https://downloads.xenproject.org/release/xen/VERSION/" + XEN_ARCHIVE_PATTERN
XEN_GITHUB_REPO = "https://github.com/xen-project/xen.git"



class Xen:
   def __init__( self, config: linux.base.Configuration, root_dir: str, **kwargs ):
      self.reset( )
      self.__config = config
      self.__version = kwargs.get( "version", "master" )
      self.__name = kwargs.get( "name", "xen-" + self.__version )
      self.__url = XEN_LINK_PATTERN.replace( "EPOCH", self.__version[0] ).replace( "VERSION", self.__version )
      self.__url_git = XEN_GITHUB_REPO
      self.__archive_name = XEN_ARCHIVE_PATTERN.replace( "VERSION", self.__version )
      self.__directories = linux.base.Directories( self.__config, root_dir, self.__name, product_subdir = "arch/" + self.__config.arch( ) + "/boot" )
   # def __init__

   def __del__( self ):
      pass
   # def __del__

   def __setattr__( self, attr, value ):
      attr_list = [ i for i in Xen.__dict__.keys( ) ]
      if attr in attr_list:
         self.__dict__[ attr ] = value
         return
      raise AttributeError
   # def __setattr__

   def __str__( self ):
      attr_list = [ i for i in Xen.__dict__.keys( ) if i[:2] != pfw.base.class_ignore_field ]
      vector = [ ]
      for attr in attr_list:
         vector.append( str( attr ) + " = " + str( self.__dict__.get( attr ) ) )
      name = "Xen { " + ", ".join( vector ) + " }"
      return name
   # def __str__

   def info( self, **kwargs ):
      tabulations: int = kwargs.get( "tabulations", 0 )
      pfw.console.debug.info( self.__class__.__name__, ":", tabs = ( tabulations + 0 ) )
      pfw.console.debug.info( "version:         \'", self.__version, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "name:            \'", self.__name, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "url:             \'", self.__url, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "git repo:        \'", self.__url_git, "\'", tabs = ( tabulations + 1 ) )
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
      # pfw.archive.extract( os.path.join( self.__directories.download( ), self.__archive_name ), "xztar", self.__directories.source( ) )
      pfw.shell.run_and_wait_with_status(
              "tar", "-xvf"
            , self.__directories.download( self.__archive_name )
            , "--checkpoint=100"
            , "--directory=" + self.__directories.source( ".." )
         )
   # def extract

   def clone( self ):
      # link: https://unix.stackexchange.com/questions/46077/where-to-download-linux-kernel-source-code-of-a-specific-version
      # Variant 1:
      #    git clone git://git.kernel.org/pub/scm/linux/kernel/git/stable/linux-stable.git
      #    cd linux-stable
      #    git checkout v2.6.36.2
      #    git fetch
      # Variant 2:
      #    git clone --depth 1 --single-branch --branch v4.5  git://git.launchpad.net/~ubuntu-kernel-test/ubuntu/+source/linux/+git/mainline-crack


      command = f"git clone"
      if None != self.__version:
         command += f" -b v{self.__version}"
      command += f" {self.__url_git} {self.__directories.source( )}"
      pfw.shell.run_and_wait_with_status( command, output = pfw.shell.eOutput.PTY )

      # repo = git.Repo.clone_from(
      #            self.__url_git
      #          , os.path.join( self.__directories.source( ), "linux-stable" )
      #          , branch="v" + self.__version
      #          , progress = pfw.git.CloneProgress( )
      #       )
   # def clone

   def sync( self, **kwargs ):
      self.download( )
      self.extract( )
   # def sync

   def configure( self, **kwargs ):
      kw_options = kwargs.get( "options", [ ] )

      command = "./configure"

      for option in kw_options:
         command += f" {option}"

      pfw.shell.run_and_wait_with_status( command, print = False, collect = False, cwd = self.__directories.source( ) )
   # def configure

   def build( self, **kwargs ):
      kw_targets = kwargs.get( "targets", ["dist-xen"] )

      if None == kw_targets or 0 == len(kw_targets):
         kw_targets = ["dist-xen"]

      targets: str = ""
      for target in kw_targets:
         targets += f"{target} "

      command = "make"
      command += f" XEN_TARGET_ARCH={self.__config.arch( )}"
      command += f" CROSS_COMPILE={self.__config.compiler( )}"
      command += f" -j{self.__config.cores( )}"

      pfw.shell.run_and_wait_with_status( command, targets, output = pfw.shell.eOutput.PTY, cwd = self.__directories.source( ) )

      # xen does not allowed to change build directory, so we should manually copy all built artifacts
      # to build directory for compatibility with other projects
      command = f"cp -r {self.__directories.source( 'dist/install/*' )} {self.__directories.build( )}"
      pfw.shell.run_and_wait_with_status( command, output = pfw.shell.eOutput.PTY )
   # def build

   def clean( self, **kwargs ):
      kw_targets = kwargs.get( "targets", ["mrproper"] )

      if None == kw_targets or 0 == len(kw_targets):
         kw_targets = ["mrproper"]

      targets: str = ""
      for target in kw_targets:
         targets += f"{target} "

      command = "make"
      command += f" XEN_TARGET_ARCH={self.__config.arch( )}"
      command += f" CROSS_COMPILE={self.__config.compiler( )}"

      pfw.shell.run_and_wait_with_status( command, targets, output = pfw.shell.eOutput.PTY )
   # def clean

   def deploy( self, **kwargs ):
      deploy_path = kwargs.get( "deploy_path", self.__directories.deploy( ) )

      command = f"cp -r {self.__directories.source( 'dist/install/*' )} {deploy_path}"
      pfw.shell.run_and_wait_with_status( command, output = pfw.shell.eOutput.PTY )

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
# class Xen
