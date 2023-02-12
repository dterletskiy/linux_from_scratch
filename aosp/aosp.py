import os
import re
import git
import time
from enum import Enum

import pfw.base
import pfw.console
import pfw.shell

import base
import configuration
import qemu
import ramdisk
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



class AOSP:
   def __init__( self, configuration: aosp.base.Configuration, root_dir: str, **kwargs ):
      self.reset( )
      self.__tag = kwargs.get( "tag", None )
      self.__name = self.__tag
      self.__config = configuration
      self.__directories = aosp.base.Directories( root_dir, self.__name, self.__config )
      self.__repo = Repo( self.__directories.source( ) )

      self.__config_cmd_line = f"export OUT_DIR_COMMON_BASE={self.__directories.build( '..' )};"
      self.__config_cmd_line += f" source build/envsetup.sh;"
      self.__config_cmd_line += f" lunch {self.__config.lunch( )};"
   # def __init__

   def __del__( self ):
      pass
   # def __del__

   def __setattr__( self, attr, value ):
      attr_list = [ i for i in AOSP.__dict__.keys( ) ]
      if attr in attr_list:
         self.__dict__[ attr ] = value
         return
      raise AttributeError
   # def __setattr__

   def __str__( self ):
      attr_list = [ i for i in AOSP.__dict__.keys( ) if i[:2] != pfw.base.class_ignore_field ]
      vector = [ ]
      for attr in attr_list:
         vector.append( str( attr ) + " = " + str( self.__dict__.get( attr ) ) )
      name = "AOSP { " + ", ".join( vector ) + " }"
      return name
   # def __str__

   def info( self, **kwargs ):
      tabulations: int = kwargs.get( "tabulations", 0 )
      pfw.console.debug.info( self.__class__.__name__, ":", tabs = ( tabulations + 0 ) )
      pfw.console.debug.info( "tag:             \'", self.__tag, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "name:            \'", self.__name, "\'", tabs = ( tabulations + 1 ) )
      self.__directories.info( tabulations + 1 )
   # def info

   def reset( self ):
      pass
   # def reset

   def sync( self, **kwargs ):
      self.__repo.install( )
      self.__repo.init( self.__tag )
      self.__repo.sync( )
   # def sync

   def configure( self, **kwargs ):
      pass
   # def configure

   def build( self, **kwargs ):
      target = kwargs.get( "target", "" )

      self.__execute( "make showcommands " + target, output = pfw.shell.eOutput.PIPE )
   # def build

   def clean( self, **kwargs ):
      self.__execute( "make clean" )
   # def clean

   def deploy( self, **kwargs ):
      pass
   # def deploy

   def simg_to_img( self, sparse_file, raw_file, **kwargs ):
      if False == os.path.exists( sparse_file ):
         pfw.console.debug.error( "Original '%s' file does not exist" % ( sparse_file ) )
         return False

      if True == os.path.exists( raw_file ):
         if os.path.getmtime( raw_file ) >= os.path.getmtime( sparse_file ):
            pfw.console.debug.warning( "Raw file '%s' is newer then original '%s' file" % ( raw_file, sparse_file ) )
            return True

      # pfw.console.debug.trace( "last modified: %s" % time.ctime( os.path.getmtime( sparse_file ) ) )
      # pfw.console.debug.trace( "created: %s" % time.ctime( os.path.getctime( sparse_file ) ) )

      command = f"simg2img {sparse_file} {raw_file}"
      self.__execute( command )

      return True
   # def simg_to_img

   def extract_android_boot_image( self, **kwargs ):
      kw_boot_img = kwargs.get( "boot_img", self.__directories.product( "boot.img" ) )
      kw_out = kwargs.get( "out", self.__directories.experimental( "boot" ) )
      kw_format = kwargs.get( "format", "mkbootimg" ) # info,mkbootimg

      command: str = f"mkdir -p {kw_out};"
      command += f" unpack_bootimg"
      command += f" --boot_img {kw_boot_img}"
      command += f" --out {kw_out}"
      command += f" --format {kw_format}"

      self.__execute( command )
   # def extract_android_boot_image

   def create_android_boot_image( self, **kwargs ):
      kw_header_version = kwargs.get( "header_version", "2" )
      kw_os_version = kwargs.get( "os_version", "12.0.0" )
      kw_os_patch_level = kwargs.get( "os_patch_level", "2022-06" )
      kw_out = kwargs.get( "out", self.__directories.experimental( "boot.img" ) )
      kw_kernel = kwargs.get( "kernel", None )
      kw_ramdisk = kwargs.get( "ramdisk", None )
      kw_dtb = kwargs.get( "dtb", None )
      kw_cmdline = kwargs.get( "cmdline", None )
      kw_base = kwargs.get( "base", None )
      kw_kernel_offset = kwargs.get( "kernel_offset", None )
      kw_ramdisk_offset = kwargs.get( "ramdisk_offset", None )
      kw_dtb_offset = kwargs.get( "dtb_offset", None )

      command: str = self.__directories.build( "host/linux-x86/bin/mkbootimg" )
      command += f" --header_version {kw_header_version}"
      command += f" --os_version {kw_os_version}"
      command += f" --os_patch_level {kw_os_patch_level}"
      command += f" --kernel {kw_kernel}"
      command += f" --ramdisk {kw_ramdisk}"
      command += f" --dtb {kw_dtb}" if kw_dtb else ""
      command += f" --cmdline \"{kw_cmdline}\"" if kw_cmdline else ""
      command += f" --base {kw_base}" if kw_base else ""
      command += f" --kernel_offset {kw_kernel_offset}" if kw_kernel_offset else ""
      command += f" --ramdisk_offset {kw_ramdisk_offset}" if kw_ramdisk_offset else ""
      command += f" --dtb_offset {kw_dtb_offset}" if kw_dtb_offset else ""
      command += f" --out {kw_out}"

      self.__execute( command )
   # def create_android_boot_image

   def build_ramdisk( self, **kwargs ):
      kw_bootconfig = kwargs.get( "bootconfig", None )

      EXPERIMENTAL_RAMDISK_DIR = self.__directories.experimental( "ramdisk" )
      EXPERIMENTAL_RAMDISK_IMAGE = self.__directories.experimental( "ramdisk.img" )

      ANDROID_PRODUCT_RAMDISK_DIR = self.__directories.product( "ramdisk" )
      ANDROID_RAMDISK_IMAGE = self.__directories.product( "ramdisk.img" )

      ANDROID_PRODUCT_VENDOR_RAMDISK_DIR = self.__directories.product( "vendor_ramdisk" )
      ANDROID_VENDOR_RAMDISK_IMAGE = self.__directories.product( "vendor_ramdisk.img" )

      command: str = ""
      command += f" rm -r {EXPERIMENTAL_RAMDISK_DIR};"
      command += f" mkdir -p {EXPERIMENTAL_RAMDISK_DIR};"
      command += f" cp -R {ANDROID_PRODUCT_RAMDISK_DIR}/* {EXPERIMENTAL_RAMDISK_DIR};"
      command += f" cp -R {ANDROID_PRODUCT_VENDOR_RAMDISK_DIR}/* {EXPERIMENTAL_RAMDISK_DIR};"
      # command += f" rm -r {EXPERIMENTAL_RAMDISK_DIR}/lib/modules/*; cp -R /mnt/dev/android/deploy/kernel/common-android14-6.1/virtual_device_aarch64/extracted/initramfs.img/lib/modules/6.1.8-maybe-dirty/* {EXPERIMENTAL_RAMDISK_DIR}/lib/modules;"
      self.__execute( command )

      # ramdisk.pack( source = EXPERIMENTAL_RAMDISK_DIR, destination = EXPERIMENTAL_RAMDISK_IMAGE, bootconfig = kw_bootconfig )
      ramdisk.pack( source = EXPERIMENTAL_RAMDISK_DIR, destination = EXPERIMENTAL_RAMDISK_IMAGE, bootconfig = None )
   # def build_ramdisk

   def run( self, **kwargs ):
      pass
   # def run

   def action( self, actions: list, **kwargs ):
      for _action in actions:
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
         elif base.eAction.run_gdb == _action:
            self.run( gdb = True, **kwargs )
         elif base.eAction.info == _action:
            self.info( **kwargs )
         elif base.eAction.none == _action:
            pass
         else:
            pfw.console.debug.warning( "unsuported action: ", _action )
   # def action

   def __execute( self, command: str = "", **kwargs ):
      kw_output = kwargs.get( "output", pfw.shell.eOutput.PTY )

      result_code = pfw.shell.execute( f"{self.__config_cmd_line} {command}", cwd = self.__directories.source( ), output = kw_output )["code"]
   # def __execute



   def tag( self ):
      return self.__tag
   # def tag

   def name( self ):
      return self.__name
   # def name

   def dirs( self ):
      return self.__directories
   # def dirs

   def config( self ):
      return self.__config
   # def config



   __tag: str = None
   __name: str = None
   __directories: aosp.base.Directories = None
   __repo: Repo = None
   __config: aosp.base.Configuration = None
   __config_cmd_line: str = None
# class AOSP
