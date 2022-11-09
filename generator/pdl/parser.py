#!/usr/bin/python3

import io

from antlr4 import *
from antlr4.error.ErrorListener import *

from PdlLexer import PdlLexer
from PdlParser import PdlParser
from PdlParserListener import PdlParserListener

import pfw.base
import pfw.console
import pfw.shell

import linux.base
import linux.uboot
import linux.buildroot
import linux.busybox
import linux.kernel
import linux.xen
import linux.qemu
import aosp.base
import aosp.aosp



def create_project( project_type: str, **kwargs ):
   kw_arch = kwargs.get( "arch", None )
   kw_root_dir = kwargs.get( "root_dir", None )
   kw_version = kwargs.get( "version", None )
   kw_defconfig = kwargs.get( "defconfig", None )
   kw_lunch = kwargs.get( "lunch", None )
   kw_variant = kwargs.get( "variant", None )
   kw_product_name = kwargs.get( "product_name", None )
   kw_product_device = kwargs.get( "product_device", None )

   project = None
   if None == project_type:
      pass
   elif "uboot" == project_type:
      project = linux.uboot.UBoot(
            linux.base.config[ kw_arch ],
            kw_root_dir,
            version = kw_version,
            defconfig = kw_defconfig
         )
   elif "buildroot" == project_type:
      project = linux.buildroot.BuildRoot(
            linux.base.config[ kw_arch ],
            kw_root_dir,
            version = kw_version,
            defconfig = kw_defconfig
         )
   elif "busybox" == project_type:
      project = linux.busybox.BusyBox(
            linux.base.config[ kw_arch ],
            kw_root_dir,
            version = kw_version,
            defconfig = kw_defconfig
         )
   elif "kernel" == project_type:
      project = linux.kernel.Kernel(
            linux.base.config[ kw_arch ],
            kw_root_dir,
            version = kw_version,
            defconfig = kw_defconfig
         )
   elif "xen" == project_type:
      project = linux.xen.Xen(
            linux.base.config[ kw_arch ],
            kw_root_dir,
            version = kw_version,
            defconfig = kw_defconfig
         )
   elif "qemu" == project_type:
      project = linux.qemu.Qemu(
            linux.base.config[ kw_arch ],
            kw_root_dir,
            version = kw_version,
            defconfig = kw_defconfig
         )
   elif "android" == project_type:
      project = aosp.aosp.AOSP(
            aosp.base.Configuration(
                    lunch = kw_lunch
                  , variant = kw_variant
                  , product_name = kw_product_name
                  , product_device = kw_product_device
               ),
            kw_root_dir,
            tag = kw_version,
         )
   else:
      pfw.console.debug.error( "Undefined project type" )

   return project
# def create_project



class PdlListener( PdlParserListener ):
   def __init__( self, output ):
      self.output = output
      self.__project_map = { }


   def enterElement( self, ctx: PdlParser.ElementContext ):
      pfw.console.debug.trace( "enterElement" )
      pass

   def exitElement( self, ctx: PdlParser.ElementContext ):
      pfw.console.debug.trace( "exitElement" )
      pass


   def enterAuthor( self, ctx: PdlParser.AuthorContext ):
      pfw.console.debug.trace( "enterAuthor" )
      pass

   def exitAuthor( self, ctx: PdlParser.AuthorContext ):
      pfw.console.debug.trace( "exitAuthor" )
      pass


   def enterVersion( self, ctx: PdlParser.VersionContext ):
      pfw.console.debug.trace( "enterVersion" )
      pass

   def exitVersion( self, ctx: PdlParser.VersionContext ):
      pfw.console.debug.trace( "exitVersion" )
      pass


   def enterProject( self, ctx: PdlParser.ProjectContext ):
      pfw.console.debug.trace( "enterProject" )

      name: str = ctx.IDENTIFIER( ).getText( )

      type_: str = ctx.type_( 0 ).IDENTIFIER( ).getText( )

      version: str = None
      for version_number in [ ctx.version( 0 ).version_number( ), ctx.version( 0 ).version_number_ext( ) ]:
         if None != version_number:
            version = version_number.getText( )

      root_dir: str = ctx.root_dir( 0 ).MODE_PATH_PATH( ).getText( )

      arch: str = ctx.arch( 0 ).IDENTIFIER( ).getText( ) if ctx.arch( ) else None

      defconfig: str = ctx.defconfig( 0 ).IDENTIFIER( ).getText( ) if ctx.defconfig( ) else None

      lunch: str = ctx.lunch( 0 ).IDENTIFIER( ).getText( ) if ctx.lunch( ) else None

      variant: str = ctx.variant( 0 ).IDENTIFIER( ).getText( ) if ctx.variant( ) else None

      product_name: str = ctx.product_name( 0 ).IDENTIFIER( ).getText( ) if ctx.product_name( ) else None

      product_device: str = ctx.product_device( 0 ).IDENTIFIER( ).getText( ) if ctx.product_device( ) else None

      pfw.console.debug.info( "type: ", type_ )
      pfw.console.debug.info( "name: ", name )
      pfw.console.debug.info( "version: ", version )
      pfw.console.debug.info( "root_dir: ", root_dir )
      pfw.console.debug.info( "arch: ", arch )
      pfw.console.debug.info( "defconfig: ", defconfig )
      pfw.console.debug.info( "lunch: ", lunch )
      pfw.console.debug.info( "variant: ", variant )
      pfw.console.debug.info( "product_name: ", product_name )
      pfw.console.debug.info( "product_device: ", product_device )

      self.__project_map[name] = create_project(
              type_
            , version = version
            , root_dir = root_dir
            , arch = arch
            , defconfig = defconfig
            , lunch = lunch
            , variant = variant
            , product_name = product_name
            , product_device = product_device
         )

   def exitProject( self, ctx: PdlParser.ProjectContext ):
      pfw.console.debug.trace( "exitProject" )
      pass



   def project_map( self ):
      return self.__project_map
   # def project_map



   __project_map: dict = { }
# class PdlListener



class PdlErrorListener( ErrorListener ):
   def __init__( self, output ):
      self.output = output        
      self._symbol = ''

   def syntaxError( self, recognizer, offendingSymbol, line, column, msg, e ):
      pfw.console.debug.error( "syntaxError -->" )
      pfw.console.debug.error( "   ", line, ":", column, "->" )
      pfw.console.debug.error( "   ", "msg: ", msg )
      pfw.console.debug.error( "   ", "recognizer: ", recognizer )
      pfw.console.debug.error( "   ", "offendingSymbol: ", offendingSymbol )
      pfw.console.debug.error( "   ", "e: ", e )
      self.output.write( msg )
      self._symbol = offendingSymbol.text
      pfw.console.debug.error( "syntaxError <--" )

   @property        
   def symbol( self ):
      pfw.console.debug.error( "symbol" )
      return self._symbol

# class PdlErrorListener



def parse( source_file: str ):
   input = FileStream( source_file )


   listener = PdlListener( io.StringIO( ) )
   error_listener = PdlErrorListener( io.StringIO( ) )

   lexer = PdlLexer( input )
   stream = CommonTokenStream( lexer )
   parser = PdlParser( stream )
   parser.removeErrorListeners( )        
   parser.addErrorListener( error_listener )
   tree = parser.content( )

   walker = ParseTreeWalker( )
   walker.walk( listener, tree )

   return listener.project_map( )
# def parse

def generate( source_file: str ):
   return parse( source_file )
# def generate
