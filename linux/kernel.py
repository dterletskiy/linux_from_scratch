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
import tools
import linux.base



KERNEL_LINK_PATTERN = "https://cdn.kernel.org/pub/linux/kernel/vEPOCH.x/linux-VERSION.tar.xz"
KERNEL_NAME_PATTERN = "linux-VERSION"
KERNEL_ARCHIVE_PATTERN = "linux-VERSION.tar.xz"
KERNEL_GIT_REPO = "git://git.kernel.org/pub/scm/linux/kernel/git/stable/linux-stable.git"



class Kernel:
   class eTarget( Enum ):
      kernel = 1
      modules = 2
      modules_install = 3
      dtbs = 4
      uimage = 5
      all = 6
   # class eTarget

   def __init__( self, config: linux.base.Configuration, root_dir: str, **kwargs ):
      self.reset( )
      self.__config = config
      self.__version = kwargs.get( "version", "master" )
      self.__name = KERNEL_NAME_PATTERN.replace( "VERSION", self.__version )
      self.__url = KERNEL_LINK_PATTERN.replace( "EPOCH", self.__version[0] ).replace( "VERSION", self.__version )
      self.__url_git = KERNEL_GIT_REPO
      self.__archive_name = KERNEL_ARCHIVE_PATTERN.replace( "VERSION", self.__version )
      self.__directories = linux.base.Directories( self.__config, root_dir, self.__name, product_subdir = "arch/" + self.__config.arch( ) + "/boot" )
   # def __init__

   def __del__( self ):
      pass
   # def __del__

   def __setattr__( self, attr, value ):
      attr_list = [ i for i in Kernel.__dict__.keys( ) ]
      if attr in attr_list:
         self.__dict__[ attr ] = value
         return
      raise AttributeError
   # def __setattr__

   def __str__( self ):
      attr_list = [ i for i in Kernel.__dict__.keys( ) if i[:2] != pfw.base.class_ignore_field ]
      vector = [ ]
      for attr in attr_list:
         vector.append( str( attr ) + " = " + str( self.__dict__.get( attr ) ) )
      name = "Kernel { " + ", ".join( vector ) + " }"
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

   def default_config( self ):
      config: str = None
      if "arm" == self.__config.arch( ):
         config = "vexpress_defconfig"
      elif "arm64" == self.__config.arch( ) or "aarch64" == self.__config.arch( ):
         config = "defconfig"
      else:
         config = "defconfig"

      return config
   # def default_config

   def configure( self, **kwargs ):
      kw_targets = kwargs.get( "targets", ["default", "menuconfig"] )
      kw_configs = kwargs.get( "configs", { } )

      if 0 == len(kw_targets):
         kw_targets = ["default", "menuconfig"]

      command = "make"
      command += f" O={self.__directories.build( )}"
      command += f" -C {self.__directories.source( )}"
      command += f" ARCH={self.__config.arch( )}"
      command += f" CROSS_COMPILE={self.__config.compiler( )}"

      for target in kw_targets:
         if "default" == target:
            target = self.default_config( )
         pfw.shell.run_and_wait_with_status( command, target, print = False, collect = False )



      if 0 != len( kw_configs ):
         config_file = open( os.path.join( self.__directories.build( ), ".config" ), "r" )
         lines: str = ""
         for line in config_file:
            # Remove config in case it is present to be added from parameter
            for config_key, config_value in kw_configs.items( ):
               pattern: str = r"^(.*)" + config_key + "=\"(.*)\"(.*)$"
               if re.match( pattern, line ):
                  pfw.console.debug.error( "regexp pattern: ", pattern )
                  line = ""
                  break
            lines += line
         # Add all kw_configs from parameter
         for config_key, config_value in kw_configs.items( ):
            lines += config_key + "=" + config_value + "\n"
         config_file.close( )
         config_file = open( os.path.join( self.__directories.build( ), ".config" ), "w" )
         config_file.write( lines )
         config_file.close( )
   # def configure

   def build( self, **kwargs ):
      kw_targets = kwargs.get( "targets", ["all"] )

      targets: str = ""
      for target in kw_targets:
         targets += f"{target} "

      command = "make"
      command += f" O={self.__directories.build( )}"
      command += f" -C {self.__directories.source( )}"
      command += f" ARCH={self.__config.arch( )}"
      command += f" CROSS_COMPILE={self.__config.compiler( )}"
      command += f" -j{self.__config.cores( )}"

      if "modules_install" in targets:
         # https://www.kernel.org/doc/Documentation/kbuild/modules.txt
         command += f" INSTALL_MOD_PATH={self.__directories.product( )}"
      elif "uImage" in targets:
         command += f" LOADADDR=0x10000"

      pfw.shell.run_and_wait_with_status( command, targets, output = pfw.shell.eOutput.PTY )
   # def build

   def clean( self, **kwargs ):
      kw_targets = kwargs.get( "targets", ["distclean"] )

      targets: str = ""
      for target in kw_targets:
         targets += f"{target} "

      command = "make"
      command += f" O={self.__directories.build( )}"
      command += f" -C {self.__directories.source( )}"
      command += f" ARCH={self.__config.arch( )}"
      command += f" CROSS_COMPILE={self.__config.compiler( )}"

      pfw.shell.run_and_wait_with_status( command, targets, output = pfw.shell.eOutput.PTY )
   # def clean

   def deploy( self, **kwargs ):
      deploy_path = kwargs.get( "deploy_path", None )
      is_create_structure = kwargs.get( "is_create_structure", False )

      if None == deploy_path:
         deploy_path = self.__directories.deploy( )
      else:
         if True != os.path.isdir( deploy_path ):
            pfw.console.debug.error( "deploy path does noe exist: ", deploy_path )
            return None

         if True == is_create_structure:
            deploy_path = os.path.join( deploy_path, self.__config.arch( ), self.__name )
            pfw.shell.run_and_wait_with_status( f"mkdir -p {deploy_path}" )
      pfw.console.debug.info( "deploy -> ", deploy_path )
      pfw.shell.run_and_wait_with_status( f"rm -r {deploy_path}" )
      pfw.shell.run_and_wait_with_status( f"mkdir -p {deploy_path}" )

      files_list: list = [
            os.path.join( self.__directories.product( ), "Image" ),
            os.path.join( self.__directories.product( ), "zImage" ),
            os.path.join( self.__directories.product( ), "Image.gz" ),
            os.path.join( self.__directories.product( ), "compressed/vmlinux" )
         ]

      for file in files_list:
         pfw.console.debug.trace( "file: '%s' ->\n     '%s'" % ( file, deploy_path ) )
         pfw.shell.run_and_wait_with_status( f"cp {file} {deploy_path}" )

      directories_list: list = [ 
            os.path.join( self.__directories.product( ), "dts" )
         ]

      for directory in directories_list:
         pfw.console.debug.trace( "directory: '%s' ->\n     '%s'" % ( directory, deploy_path ) )
         pfw.shell.run_and_wait_with_status( f"cp -r {directory} {deploy_path}" )

      return deploy_path
   # def deploy

   def run( self, **kwargs ):
      command: str = ""

      if "arm" == self.__config.arch( ):
         command += f" -machine virt"
         # command += f" -machine vexpress-a9"
         command += f" -cpu cortex-a15"
         dtb = self.__directories.product( "dts/vexpress-v2p-ca9.dtb" )
         kernel = self.__directories.product( "zImage" )
      elif "arm64" == self.__config.arch( ) or "aarch64" == self.__config.arch( ):
         command += f" -machine virt"
         command += f" -cpu cortex-a53"
         kernel = self.__directories.product( "Image" )

      command += f" -smp cores=1"
      command += f" -m 512M"
      command += f" -nographic"
      command += f" -serial mon:stdio"
      command += f" -no-reboot"
      command += f" -d guest_errors"

      tools.run_qemu(
            command,
            arch = self.__config.arch( ),
            kernel = kernel,
            append = "root=/dev/ram rw console=ttyAMA0",
            **kwargs
         )
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



   __version: str = None
   __name: str = None
   __url: str = None
   __url_git: str = None
   __archive_name: str = None
   __directories: linux.base.Directories = None
   __config: linux.base.Configuration = None
# class Kernel