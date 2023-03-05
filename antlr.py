#!/usr/bin/python3

import os
import sys

import pfw.console
import pfw.shell



ANTLR_JAR: str = ""

def init( antlr_jar: str = None ):
   global ANTLR_JAR
   ANTLR_JAR = antlr_jar
# def init

def antlr( **kwargs ):
   kw_antlr_jar = kwargs.get( "antlr_jar", None )

   if None == kw_antlr_jar:
      kw_antlr_jar = ANTLR_JAR

   return kw_antlr_jar
# def antlr



def gen_grammar( **kwargs ):
   kw_lexers = kwargs.get( "lexers", [ ] )
   kw_parsers = kwargs.get( "parsers", [ ] )
   kw_outdir = kwargs.get( "outdir", "/tmp/antlr_gen" )
   kw_extend_path = kwargs.get( "extend_path", True )

   os.makedirs( kw_outdir, exist_ok = True )

   g4_files = kw_lexers + kw_parsers
   for g4_file in g4_files:
      command = f"java -jar"
      command += f" {antlr( )}"
      command += f" -Dlanguage=Python3"
      command += f" {g4_file}"
      command += f" -o {kw_outdir}"
      command += f" -listener"
      command += f" -visitor"
      pfw.shell.execute( command )

   if True == kw_extend_path:
      sys.path.insert( 0, kw_outdir )

   return kw_outdir
# def antlr_gen
