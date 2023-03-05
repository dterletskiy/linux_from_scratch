import os

import pfw.base.struct
import pfw.console



class Configuration:
   def __init__( self, **kwargs ):
      self.__device = kwargs.get( "device", "trout" )
      self.__arch = kwargs.get( "arch", "x86" )
      self.__variant = kwargs.get( "variant", "userdebug" )

      self.__product_device = kwargs.get( "product_device", f"{self.__device}_{self.__arch}" )
      self.__product_name = kwargs.get( "product_name", f"aosp_{self.__product_device}" )
      self.__lunch = kwargs.get( "lunch", f"{self.__product_name}-{self.__variant}" )
   # def __init__

   def device( self ):
      return self.__device
   # def device

   def arch( self ):
      return self.__arch
   # def arch

   def variant( self ):
      return self.__variant
   # def variant

   def product_device( self ):
      return self.__product_device
   # def product_device

   def product_name( self ):
      return self.__product_name
   # def product_name

   def lunch( self ):
      return self.__lunch
   # def lunch

   __device = None
   __arch = None
   __variant = None
   __product_device = None
   __product_name = None
   __lunch = None
# class Configuration

TROUT_X86_USERDEBUG = Configuration( device = "trout", arch = "x86", variant = "userdebug" )
TROUT_ARM64_USERDEBUG = Configuration( device = "trout", arch = "arm64", variant = "userdebug" )

config: dict = {
   "x86": TROUT_X86_USERDEBUG,
   "x86_64": TROUT_X86_USERDEBUG,
   "arm64": TROUT_ARM64_USERDEBUG,
   "aarch64": TROUT_ARM64_USERDEBUG
}



class Directories:
   def __init__( self, root_dir: str, name: str, config: Configuration, **kwargs ):
      download = kwargs.get( "download_dir", os.path.join( root_dir, "download", name ) )
      source = kwargs.get( "source_dir", os.path.join( root_dir, "source", name ) )
      build = kwargs.get( "build_dir", os.path.join( root_dir, "build", name ) )
      deploy = kwargs.get( "deploy_dir", os.path.join( root_dir, "deploy", name ) )
      logs = kwargs.get( "logs_dir", os.path.join( root_dir, "logs", name ) )
      product = kwargs.get( "product_dir", os.path.join( build, "target/product", config.product_device( ) ) )
      experimental = kwargs.get( "exp_dir", os.path.join( product, "experimental" ) )

      self.__root = root_dir
      self.__download = download
      self.__source = source
      self.__build = build
      self.__deploy = deploy
      self.__logs = logs
      self.__product = product
      self.__experimental = experimental

      pfw.shell.execute( "mkdir", "-p", self.__download )
      pfw.shell.execute( "mkdir", "-p", self.__source )
      pfw.shell.execute( "mkdir", "-p", self.__build )
      pfw.shell.execute( "mkdir", "-p", self.__deploy )
      pfw.shell.execute( "mkdir", "-p", self.__logs )
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
      attr_list = [ i for i in Directories.__dict__.keys( ) if i[:2] != pfw.base.struct.ignore_field
 ]
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
      pfw.console.debug.info( "deploy:       \'", self.__deploy, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "logs:         \'", self.__logs, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "product:      \'", self.__product, "\'", tabs = ( tabulations + 1 ) )
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

   def deploy( self, sub_path: str = "" ):
      return os.path.join( self.__deploy, sub_path )
   # def deploy

   def logs( self, sub_path: str = "" ):
      return os.path.join( self.__logs, sub_path )
   # def product

   def product( self, sub_path: str = "" ):
      return os.path.join( self.__product, sub_path )
   # def product

   def experimental( self, sub_path: str = "" ):
      return os.path.join( self.__experimental, sub_path )
   # def experimental

   __root: str = None
   __download: str = None
   __source: str = None
   __build: str = None
   __deploy: str = None
   __product: str = None
   __experimental: str = None
   __logs: str = None
# class Directories
