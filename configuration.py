import os
import sys
import copy
import re
import getopt
import argparse



class ConfigurationData:
   def __init__( self, name: str, required: bool, destination: str ):
      self.__name = copy.deepcopy( name )
      self.__required = copy.deepcopy( required )
      self.__description = copy.deepcopy( destination )
      self.__values = [ ]
   # def __init__

   def __del__( self ):
      pass
   # def __del__

   def __setattr__( self, attr, value ):
      attr_list = [ i for i in ConfigurationData.__dict__.keys( ) ]
      if attr in attr_list:
         self.__dict__[ attr ] = value
         return
      raise AttributeError
   # def __setattr__

   def __str__( self ):
      attr_list = [ i for i in ConfigurationData.__dict__.keys( ) if i[:2] != "__" ]
      vector = [ ]
      for attr in attr_list:
         vector.append( str( attr ) + " = " + str( self.__dict__.get( attr ) ) )
      name = "ConfigurationData { " + ", ".join( vector ) + " }"
      return name
   # def __str__

   def __gt__( self, other ):
      return self.__name > other.__name
   # def __gt__

   def __lt__( self, other ):
      return self.__name < other.__name
   # def __lt__

   def __eq__( self, other ):
      return self.__name == other.__name if None != other else False
   # def __eq__

   def info( self, **kwargs ):
      print( self.__class__.__name__, ":" )
      print( "name:         \'", self.__name, "\'" )
      print( "values:       \'", self.__values, "\'" )
      print( "required:     \'", self.__required, "\'" )
      print( "description:  \'", self.__description, "\'" )
   # def info



   def get_name( self ):
      return self.__name
   # def get_name

   def get_value( self, index: int = 0 ):
      return self.__values[ index ] if index < len( self.__values ) else None
   # def get_value

   def get_values( self ):
      return self.__values
   # def get_values

   def set_value( self, value ):
      if None == value:
         return

      values_to_add: list = [ ]
      if isinstance( value, list ) or isinstance( value, tuple ):
         values_to_add = value
      elif isinstance( value, dict ) or isinstance( value, set ):
         return
      else:
         values_to_add = [ value ]

      self.__values.extend( values_to_add )
   # def set_value

   def reset_value( self, value = None ):
      self.__values.clear( )
      self.set_value( value )
   # def reset_value

   def test_value( self, value ):
      if None == value:
         return False

      values_to_test: list = [ ]
      if isinstance( value, list ) or isinstance( value, tuple ):
         values_to_test = value
      elif isinstance( value, dict ) or isinstance( value, set ):
         return
      else:
         values_to_test = [ value ]

      for value_to_test in values_to_test:
         if not ( value_to_test in self.__values ):
            return False

      return True
   # def test_value

   def get_required( self ):
      return self.__required
   # def get_required

   def get_description( self ):
      return self.__description
   # def get_description

   def is_satisfy( self ):
      result: bool = 0 < len( self.__values ) if self.__required else True

      if False == result:
         print( "configuration variable '%s' is not defined in command line paramenters and configuration file" % ( self.__name ) )
         print( "configuration variable '%s': '%s'" % ( self.__name, self.__description ) )

      return result
   # def is_satisfy



   __name: str = None
   __values: list = [ ]
   __required: bool = False
   __description: str = None
# class ConfigurationData



class ConfigurationContainer:
   def __init__( self, data_list: list = [ ], **kwargs ):
      self.__list = copy.deepcopy( data_list )
   # def __init__

   def __del__( self ):
      pass
   # def __del__

   def __setattr__( self, attr, value ):
      attr_list = [ i for i in ConfigurationContainer.__dict__.keys( ) ]
      if attr in attr_list:
         self.__dict__[ attr ] = value
         return
      raise AttributeError
   # def __setattr__

   def __str__( self ):
      attr_list = [ i for i in ConfigurationContainer.__dict__.keys( ) if i[:2] != "__" ]
      vector = [ ]
      for attr in attr_list:
         vector.append( str( attr ) + " = " + str( self.__dict__.get( attr ) ) )
      name = "ConfigurationContainer { " + ", ".join( vector ) + " }"
      return name
   # def __str__

   def info( self, **kwargs ):
      print( self.__class__.__name__, ":" )
      for data in self.__list: data.info( )
   # def info



   def set_data( self, name: str, data: ConfigurationData ):
      self.__list.append( data )
   # def set_data

   def get_data( self, name: str ):
      for data in self.__list:
         if data.get_name( ) == name:
            return data

      return None
   # def get_data

   def test( self, name: str ):
      return None != self.get_data( name )
   # def test

   def delete_data( self, name: str ):
      for index in range( len( self.__list ) ):
         if self.__list[ index ].get_name( ) == name:
            del self.__list[ index ]
   # def delete_data

   def set_value( self, name: str, value ):
      data = self.get_data( name )
      if None == data:
         data = ConfigurationData( name, False, "" )
         self.__list.append( data )

      data.set_value( value )
   # def set_value

   def get_values( self, name: str ):
      data = self.get_data( name )
      return data.get_values( ) if None != data else [ ]
   # def get_values

   def get_value( self, name: str, index: int = 0 ):
      data = self.get_data( name )
      return data.get_value( index ) if None != data else None
   # def get_value

   def get_description( self, name: str ):
      data = self.get_data( name )
      return data.get_description( ) if None != data else None
   # def get_description

   def get_required( self, name: str ):
      data = self.get_data( name )
      return data.get_required( ) if None != data else None
   # def get_required

   def is_complete( self ):
      for data in self.__list:
         if False == data.is_satisfy( ):
            return False

      return True
   # def is_complete



   __list: list = [ ]
# class ConfigurationContainer



def add_config( app_data, name, value ):
   app_data.set_value( name, value )

   if "antlr_outdir" == name:
      app_data.set_value( "include", value )
# def add_config



def process_cmdline( app_data, argv ):
   print( "Number of arguments:", len(sys.argv) )
   print( "Argument List:", str(sys.argv) )

   parser = argparse.ArgumentParser( description = 'App description' )

   parser.add_argument( "--version", action = "version", version = '%(prog)s 2.0' )

   parser.add_argument( "--config", dest = "config", type = str, action = "append", required = False, help = app_data.get_description( "config" ) )

   parser.add_argument( "--include", dest = "include", type = str, action = "append", help = app_data.get_description( "include" ) )

   parser.add_argument( "--arch", dest = "arch", type = str, action = "store", required = False, help = app_data.get_description( "arch" ) )
   parser.add_argument( "--action", dest = "action", type = str, action = "store", required = False, help = app_data.get_description( "action" ) )
   parser.add_argument( "--project", dest = "project", type = str, action = "store", required = False, help = app_data.get_description( "project" ) )
   parser.add_argument( "--target", dest = "target", type = str, action = "append", required = False, help = app_data.get_description( "target" ) )

   parser.add_argument( "--antlr_jar", dest = "antlr_jar", type = str, action = "store", help = app_data.get_description( "antlr_jar" ) )
   parser.add_argument( "--antlr_outdir", dest = "antlr_outdir", type = str, action = "store", help = app_data.get_description( "antlr_outdir" ) )
   parser.add_argument( "--antlr_lexer", dest = "antlr_lexer", type = str, action = "append", help = app_data.get_description( "antlr_lexer" ) )
   parser.add_argument( "--antlr_parser", dest = "antlr_parser", type = str, action = "append", help = app_data.get_description( "antlr_parser" ) )

   # parser.print_help( )
   try:
      argument = parser.parse_args( )
   except argparse.ArgumentError:
      print( 'Catching an ArgumentError' )

   for key in argument.__dict__:
      add_config( app_data, key, argument.__dict__[ key ] )
# def process_cmdline



def process_config_file( app_data ):
   pattern: str = r"^\s*(.*)\s*:\s*(.*)\s*$"

   for config_file in app_data.get_values( "config" ):
      config_file_h = open( config_file, "r" )
      for line in config_file_h:
         match = re.match( pattern, line )
         if match:
            add_config( app_data, match.group( 1 ), match.group( 2 ) )
      config_file_h.close( )
# def process_config_file



def process_configuration( app_data, argv ):
   process_cmdline( app_data, argv )
   process_config_file( app_data )
   app_data.info( )
   if False == app_data.is_complete( ):
      sys.exit( 1 )

   for path in reversed( app_data.get_values( "include" ) ):
      sys.path.insert( 0, path )
# def process_configuration



config: ConfigurationContainer = ConfigurationContainer(
      [
         ConfigurationData( "config"                      , True  , "Path to configuration file" ),
         ConfigurationData( "pdl"                         , True  , "Path to project description language configuration file" ),

         ConfigurationData( "tmp_path"                    , True  , "Directory for temporary files and artifacts" ),
         ConfigurationData( "include"                     , True  , "Additional directory to search import packages" ),
         ConfigurationData( "arch"                        , False , "Architecture" ),
         ConfigurationData( "action"                      , False , "Action" ),
         ConfigurationData( "project"                     , False , "Project" ),
         ConfigurationData( "target"                      , False , "Target" ),

         ConfigurationData( "antlr_jar"                   , True  , "Path to antlr jar file" ),
         ConfigurationData( "antlr_outdir"                , True  , "Output directory for generated lexer, parser, listener and visitor files." ),
         ConfigurationData( "antlr_lexer"                 , True  , "Path to lexer grammer files" ),
         ConfigurationData( "antlr_parser"                , True  , "Path to parser grammer files" ),

         ConfigurationData( "qemu_path"                   , True  , "Directory with qemu binaries" ),



         ConfigurationData( "uboot_script"                , True  , "u-boot script what will be used for booting" ),
         ConfigurationData( "uboot_script_source"         , True  , "u-boot source script file what will parsed and used for generating final u-boot script file" ),
         ConfigurationData( "syslinux_script"             , True  , "" ),
         ConfigurationData( "dtb_export_path"             , True  , "" ),
         ConfigurationData( "dtb_dump_path"               , True  , "" ),

         ConfigurationData( "android_bootconfig_x86"      , True  , "" ),
         ConfigurationData( "android_bootconfig_arm64"    , True  , "" ),
      ]
   )



def values( name: str ):
   return config.get_values( name )
# def values

def value( name: str, index: int = 0 ):
   return config.get_value( name, index )
# def value



def configure( argv ):
   process_configuration( config, sys.argv[1:] )
# def configure
