import os
import re
import sys
import copy

import pfw.console



class ConfigurationValue:
   def __init__( self, name: str, value: str, destination: str ):
      self.__name = copy.deepcopy( name )
      self.__value = copy.deepcopy( value )
      self.__description = copy.deepcopy( destination )
   # def __init__

   def __del__( self ):
      pass
   # def __del__

   def __setattr__( self, attr, value ):
      attr_list = [ i for i in ConfigurationValue.__dict__.keys( ) ]
      if attr in attr_list:
         self.__dict__[ attr ] = value
         return
      raise AttributeError
   # def __setattr__

   def __str__( self ):
      attr_list = [ i for i in ConfigurationValue.__dict__.keys( ) if i[:2] != pfw.base.class_ignore_field ]
      vector = [ ]
      for attr in attr_list:
         vector.append( str( attr ) + " = " + str( self.__dict__.get( attr ) ) )
      name = "ConfigurationValue { " + ", ".join( vector ) + " }"
      return name
   # def __str__

   def info( self, tabulations: int = 0 ):
      pfw.console.debug.info( self.__class__.__name__, ":", tabs = ( tabulations + 0 ) )
      pfw.console.debug.info( "name:            \'", self.__name, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "value:           \'", self.__value, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "description:     \'", self.__description, "\'", tabs = ( tabulations + 1 ) )
   # def info

   def name( self ):
      return self.__name
   # def name

   def value( self ):
      return self.__value
   # def value

   def description( self ):
      return self.__description
   # def description



   __name: str = None
   __value: str = None
   __description: str = None
# class ConfigurationValue



# Next variables must be defined in configuration file:
g_required_configuration_variables: dict = [
   ConfigurationValue( "KERNEL_ROOT_DIR"              , None, "" ),
   ConfigurationValue( "KERNEL_VERSION"               , None, "" ),

   ConfigurationValue( "BUSYBOX_ROOT_DIR"             , None, "" ),
   ConfigurationValue( "BUSYBOX_VERSION"              , None, "" ),

   ConfigurationValue( "BUILDROOT_ROOT_DIR"           , None, "" ),
   ConfigurationValue( "BUILDROOT_VERSION"            , None, "" ),

   ConfigurationValue( "UBOOT_ROOT_DIR"               , None, "" ),
   ConfigurationValue( "UBOOT_VERSION"                , None, "" ),

   ConfigurationValue( "ANDROID_ROOT_DIR"             , None, "" ),
   ConfigurationValue( "ANDROID_VERSION"              , None, "" ),

   ConfigurationValue( "UBOOT_SCRIPT"                 , None, "" ),
   ConfigurationValue( "SYSLINUX_SCRIPT"              , None, "" ),
   ConfigurationValue( "DTB_PATH"                     , None, "" ),

   ConfigurationValue( "ANDROID_BOOTCONFIG_X86"       , None, "" ),
   ConfigurationValue( "ANDROID_BOOTCONFIG_ARM64"     , None, "" ),

   ConfigurationValue( "TMP_PATH"                     , None, "" ),
]



LINUX_IMAGE_PARTITION: pfw.image.Description = None
LINUX_IMAGE_DRIVE: pfw.image.Description = None



def init( variables: dict = { } ):
   global_variables = globals( )
   global_variables.update( variables )

   for required_config in g_required_configuration_variables:
      if required_config.name( ) in global_variables.keys( ):
         pass
      else:
         pfw.console.debug.error( "configuration variable '%s' is not defined in configuration file" % ( required_config.name( ) ) )
         pfw.console.debug.error( "configuration variable '%s': %s" % ( required_config.name( ), required_config.description( ) ) )
         sys.exit( 1 )

   global LINUX_IMAGE_PARTITION
   LINUX_IMAGE_PARTITION = pfw.image.Description(
           os.path.join( TMP_PATH, "partition.img" )
         , os.path.join( TMP_PATH, "partition" )
         , pfw.size.Size( 256, pfw.size.Size.eGran.M )
         , "ext2"
      )
   global LINUX_IMAGE_DRIVE
   LINUX_IMAGE_DRIVE = pfw.image.Description(
           os.path.join( TMP_PATH, "drive.img" )
         , os.path.join( TMP_PATH, "drive" )
         , pfw.size.Size( 256, pfw.size.Size.eGran.M )
         , "ext2"
      )

   info( )
   return True
# def init



def info( ):
   global_variables = globals( )
   for required_config in g_required_configuration_variables:
      pfw.console.debug.info( "%s: %s" % ( required_config.name( ), global_variables[ required_config.name( ) ] ) )
