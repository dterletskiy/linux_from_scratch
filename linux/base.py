import os
import inspect
from enum import IntEnum

import pfw.base
import pfw.console
import pfw.shell

import base



class Configuration:
   def __init__( self, arch: str, compiler: str, compiler_path: str, machine: str, cores: str ):
      self.__arch = arch
      self.__compiler = compiler
      self.__compiler_path = compiler_path
      self.__machine = machine
      self.__cores = cores
   # def __init__

   def __del__( self ):
      pass
   # def __del__

   def __setattr__( self, attr, value ):
      attr_list = [ i for i in Configuration.__dict__.keys( ) ]
      if attr in attr_list:
         self.__dict__[ attr ] = value
         return
      raise AttributeError
   # def __setattr__

   def __str__( self ):
      attr_list = [ i for i in Configuration.__dict__.keys( ) if i[:2] != pfw.base.class_ignore_field ]
      vector = [ ]
      for attr in attr_list:
         vector.append( str( attr ) + " = " + str( self.__dict__.get( attr ) ) )
      name = "Configuration { " + ", ".join( vector ) + " }"
      return name
   # def __str__

   def info( self, tabulations: int = 0 ):
      pfw.console.debug.info( self.__class__.__name__, ":", tabs = ( tabulations + 0 ) )
      pfw.console.debug.info( "arch:            \'", self.__arch, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "compiler:        \'", self.__compiler, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "compiler_path:   \'", self.__compiler_path, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "machine:         \'", self.__machine, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "cores:           \'", self.__cores, "\'", tabs = ( tabulations + 1 ) )
   # def info



   def arch( self ):
      return self.__arch
   # def arch

   def compiler( self ):
      return self.__compiler
   # def arch

   def compiler_path( self, sub_path ):
      return os.path.join( self.__compiler_path, sub_path )
   # def arch

   def machine( self ):
      return self.__machine
   # def arch

   def cores( self ):
      return self.__cores
   # def arch

   __arch: str = None
   __compiler: str = None
   __compiler_path: str = None
   __machine: str = None
   __cores: str = None
# class Configuration

config: dict = {
   "arm": Configuration(
           arch = "arm"
         , compiler = "arm-linux-gnueabi-"
         , compiler_path = "/usr/arm-linux-gnueabi"
         , machine = "vexpress"
         , cores = "8"
      ),
   "arm64": Configuration(
           arch = "arm64"
         , compiler = "aarch64-linux-gnu-"
         , compiler_path = "/usr/arm-linux-gnueabi"
         , machine = "vexpress"
         , cores = "8"
      ),
   "aarch64": Configuration(
           arch = "aarch64"
         , compiler = "aarch64-linux-gnu-"
         , compiler_path = "/usr/arm-linux-gnueabi"
         , machine = "vexpress"
         , cores = "8"
      ),
   "x86": Configuration(
           arch = "x86"
         , compiler = "to_do"
         , compiler_path = "to_do"
         , machine = "to_do"
         , cores = "8"
      )
}



class Directories:
   # download directory will be set to /<root_dir>/download/<name>
   # source directory will be set to /<root_dir>/source/<name>
   # build directory will be set to /<root_dir>/build/<arch>/<name>
   # product directory will be set to /<root_dir>/build/<arch>/<name>/<product_subdir>
   # deploy directory will be set to /<root_dir>/deploy/<arch>/<name>
   def __init__( self, config: Configuration, root_dir: str, name: str, **kwargs ):
      download = kwargs.get( "download_dir", os.path.join( root_dir, "download", name ) )
      source = kwargs.get( "source_dir", os.path.join( root_dir, "source", name ) )
      build = kwargs.get( "build_dir", os.path.join( root_dir, "build", config.arch( ), name ) )
      product = os.path.join( build, kwargs.get( "product_subdir", "" ) )
      deploy = kwargs.get( "deploy_dir", os.path.join( root_dir, "deploy", config.arch( ), name ) )

      self.__root = root_dir
      self.__download = download
      self.__source = source
      self.__build = build
      self.__product = product
      self.__deploy = deploy

      pfw.shell.run_and_wait_with_status( "mkdir", "-p", self.__download )
      pfw.shell.run_and_wait_with_status( "mkdir", "-p", self.__source )
      pfw.shell.run_and_wait_with_status( "mkdir", "-p", self.__build )
      pfw.shell.run_and_wait_with_status( "mkdir", "-p", self.__deploy )
   # def __init__

   def __del__( self ):
      pass
   # def __del__

   def __setattr__( self, attr, value ):
      attr_list = [ i for i in Directories.__dict__.keys( ) ]
      if attr in attr_list:
         self.__dict__[ attr ] = value
         return
      raise AttributeError
   # def __setattr__

   def __str__( self ):
      attr_list = [ i for i in Directories.__dict__.keys( ) if i[:2] != pfw.base.class_ignore_field ]
      vector = [ ]
      for attr in attr_list:
         vector.append( str( attr ) + " = " + str( self.__dict__.get( attr ) ) )
      name = "Directories { " + ", ".join( vector ) + " }"
      return name
   # def __str__

   def info( self, tabulations: int = 0 ):
      pfw.console.debug.info( self.__class__.__name__, ":", tabs = ( tabulations + 0 ) )
      pfw.console.debug.info( "root:         \'", self.__root, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "download:     \'", self.__download, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "source:       \'", self.__source, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "build:        \'", self.__build, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "product:      \'", self.__product, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "deploy:       \'", self.__deploy, "\'", tabs = ( tabulations + 1 ) )
   # def info



   def root( self, sub_path: str = "" ):
      return os.path.join( self.__root, sub_path )
   # def root

   def download( self, sub_path: str = "" ):
      return os.path.join( self.__download, sub_path )
   # def download

   def source( self, sub_path: str = "" ):
      return os.path.join( self.__source, sub_path )
   # def source

   def build( self, sub_path: str = "" ):
      return os.path.join( self.__build, sub_path )
   # def build

   def product( self, sub_path: str = "" ):
      return os.path.join( self.__product, sub_path )
   # def product

   def deploy( self, sub_path: str = "" ):
      return os.path.join( self.__deploy, sub_path )
   # def deploy

   __root: str = None
   __download: str = None
   __source: str = None
   __build: str = None
   __product: str = None
   __deploy: str = None
# class Directories



class Build:
   def __init__( self, config: Configuration, root_dir: str ):
      self.reset( )
      self.__config = config
      self.__name = "u-boot"
      self.__url_git = UBOOT_GITHUB_REPO
      self.__directories = Directories( self.__config, root_dir, self.__name, "" )
   # def __init__

   def __del__( self ):
      pass
   # def __del__

   def __setattr__( self, attr, value ):
      attr_list = [ i for i in Build.__dict__.keys( ) ]
      if attr in attr_list:
         self.__dict__[ attr ] = value
         return
      raise AttributeError
   # def __setattr__

   def __str__( self ):
      attr_list = [ i for i in Build.__dict__.keys( ) if i[:2] != pfw.base.class_ignore_field ]
      vector = [ ]
      for attr in attr_list:
         vector.append( str( attr ) + " = " + str( self.__dict__.get( attr ) ) )
      name = "Build { " + ", ".join( vector ) + " }"
      return name
   # def __str__

   def info( self, **kwargs ):
      tabulations: int = kwargs.get( "tabulations", 0 )
      pfw.console.debug.info( self.__class__.__name__, ":", tabs = ( tabulations + 0 ) )
      pfw.console.debug.info( "name:            \'", self.__name, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "git repo:        \'", self.__url_git, "\'", tabs = ( tabulations + 1 ) )
      self.__directories.info( tabulations + 1 )
   # def info

   def reset( self ):
      pass
   # def reset

   def clone( self ):
      pass
   # def clone

   def sync( self, **kwargs ):
      pass
   # def sync

   def default_config( self ):
      pass
   # def default_config

   def configure( self, **kwargs ):
      pass
   # def configure

   def build( self, **kwargs ):
      pass
   # def build

   def clean( self, **kwargs ):
      pass
   # def clean

   def deploy( self, **kwargs ):
      pass
   # def deploy

   def run( self ):
      pass
   # def run

   def action( self, actions: list, **kwargs ):
      for _action in actions:
         if eAction.sync == _action:
            self.sync( **kwargs )
         elif eAction.clean == _action:
            self.clean( **kwargs )
         elif eAction.config == _action:
            self.configure( **kwargs )
         elif eAction.build == _action:
            self.build( **kwargs )
         elif eAction.deploy == _action:
            self.deploy( **kwargs )
         elif base.eAction.run == _action:
            self.run( **kwargs )
         elif eAction.info == _action:
            self.info( **kwargs )
         else:
            self.info( **kwargs )
   # def action

   def dirs( self ):
      return self.__directories
   # def dirs




# class Build
