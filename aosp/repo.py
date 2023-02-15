import os

import pfw.base
import pfw.console
import pfw.shell

import base
import aosp.base



REPO_TOOL_URL = "https://storage.googleapis.com/git-repo-downloads/repo"
ANDROID_MANIFEST_URL = "https://android.googlesource.com/platform/manifest"



class Repo:
   def __init__( self, destination: str, **kwargs ):
      kw_manifest: int = kwargs.get( "manifest", ANDROID_MANIFEST_URL )

      self.__repo_tool = os.path.join( destination, "repo" )
      self.__source_dir = destination
      self.__manifest = kw_manifest
   # def __init__

   def __del__( self ):
      pass
   # def __del__

   def __setattr__( self, attr, value ):
      attr_list = [ i for i in Repo.__dict__.keys( ) ]
      if attr in attr_list:
         self.__dict__[ attr ] = value
         return
      raise AttributeError
   # def __setattr__

   def __str__( self ):
      attr_list = [ i for i in Repo.__dict__.keys( ) if i[:2] != pfw.base.class_ignore_field ]
      vector = [ ]
      for attr in attr_list:
         vector.append( str( attr ) + " = " + str( self.__dict__.get( attr ) ) )
      name = "Repo { " + ", ".join( vector ) + " }"
      return name
   # def __str__

   def info( self, **kwargs ):
      tabulations: int = kwargs.get( "tabulations", 0 )
      pfw.console.debug.info( self.__class__.__name__, ":", tabs = ( tabulations + 0 ) )
      pfw.console.debug.info( "repo tool:         \'", self.__repo_tool, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "source dir:        \'", self.__source_dir, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "branch:            \'", self.__branch, "\'", tabs = ( tabulations + 1 ) )

      if None == self.__source_dir:
         return

      # https://stackoverflow.com/questions/14402425/how-do-i-know-the-current-version-in-an-android-repo
      manifest_git_path = os.path.join( self.__source_dir, ".repo/manifests.git" )
      pfw.shell.execute( f"git --git-dir {manifest_git_path} log default" )
      pfw.shell.execute( f"git --git-dir {manifest_git_path} tag" )
      pfw.shell.execute( f"git --git-dir {manifest_git_path} branch -a" )
   # def info

   def install( self ):
      pfw.base.download( self.__url, self.__source_dir )
      pfw.shell.execute( f"chmod a+x {self.__repo_tool}" )
   # def install

   def init( self, branch: str, **kwargs ):
      kw_depth: int = kwargs.get( "depth", 1 )

      command: str = f"{self.__repo_tool} init"
      command += f" -u {self.__manifest}"
      command += f" -b {branch}"
      command += f" --depth={kw_depth}"
      result_code = pfw.shell.execute( command, cwd = self.__source_dir, output = pfw.shell.eOutput.PTY )["code"]

      if 0 != result_code:
         pfw.console.debug.error( "repo init error: ", result_code )
         return False

      self.__branch = branch

      return True
   # def init

   def sync( self ):
      command: str = f"{self.__repo_tool} sync"
      command += f" --current-branch"
      command += f" --no-clone-bundle"
      command += f" --no-tags"
      result_code = pfw.shell.execute( command, cwd = self.__source_dir, output = pfw.shell.eOutput.PTY )["code"]

      if 0 != result_code:
         pfw.console.debug.error( "repo sync error: ", result_code )
         return False

      return True
   # def sync

   def status( self ):
      command: str = f"{self.__repo_tool} status"
      result_code = pfw.shell.execute( command, cwd = self.__source_dir, output = pfw.shell.eOutput.PTY )["code"]

      if 0 != result_code:
         pfw.console.debug.error( "repo status error: ", result_code )
         return False

      return True
   # def status

   def revert( self ):

      command: str = f"{self.__repo_tool} forall -vc \"git reset --hard\""
      result_code = pfw.shell.execute( command, cwd = self.__source_dir )["code"]

      if 0 != result_code:
         pfw.console.debug.error( "repo revert error: ", result_code )
         return False

      return True
   # def revert



   __url: str = REPO_TOOL_URL
   __repo_tool: str = None
   __source_dir: str = None
   __branch: str = None
   __manifest: str = None
# class Repo
