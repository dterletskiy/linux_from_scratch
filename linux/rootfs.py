import os
import sys
import signal
import re
import subprocess
import git
from enum import Enum

import pfw.base
import pfw.console
import pfw.archive
import pfw.shell
import pfw.file
import pfw.size
import pfw.image
import pfw.os.signal
import pfw.git

import base
import qemu
import ubuntu
import linux.base



UBUNTU_ARCHIVE_PATTERN="ubuntu-base-VERSION-base-ARCH.tar.gz"
UBUNTU_URL_PATTERN="http://cdimage.ubuntu.com/ubuntu-base/releases/VERSION/release/" + UBUNTU_ARCHIVE_PATTERN




def signal_handler( signum, frame, *args, **kwargs ):
   kw_object = kwargs.get( "object", None )

   pfw.console.debug.warning( f"signal: {signum}" )
   if signal.SIGINT == signum:
      kw_object.deinit( )
# def signal_handler

class Rootfs:
   def __init__( self, config: linux.base.Configuration, root_dir: str, **kwargs ):
      self.reset( )
      self.__config = config
      self.__version = kwargs.get( "version", None )
      self.__name = f"ubuntu-{self.__version}-{self.__config.arch( )}"
      self.__url = UBUNTU_URL_PATTERN.replace( "VERSION", self.__version ).replace( "ARCH", self.__config.arch( ) )
      self.__archive_name = UBUNTU_ARCHIVE_PATTERN.replace( "VERSION", self.__version ).replace( "ARCH", self.__config.arch( ) )
      self.__directories = linux.base.Directories( self.__config, root_dir, self.__name )

      description = pfw.image.Partition.Description(
           file = self.__directories.build( "rootfs.img" )
         , size = pfw.size.Size( 3, pfw.size.Size.eGran.G, align = pfw.size.Size.eGran.G )
         , fs = "ext4"
      )
      self.__image = pfw.image.Partition( description, build = True, force = False )
   # def __init__

   def __del__( self ):
      pass
   # def __del__

   def __setattr__( self, attr, value ):
      attr_list = [ i for i in Rootfs.__dict__.keys( ) ]
      if attr in attr_list:
         self.__dict__[ attr ] = value
         return
      raise AttributeError
   # def __setattr__

   def __str__( self ):
      attr_list = [ i for i in Rootfs.__dict__.keys( ) if i[:2] != pfw.base.class_ignore_field ]
      vector = [ ]
      for attr in attr_list:
         vector.append( str( attr ) + " = " + str( self.__dict__.get( attr ) ) )
      name = "Rootfs { " + ", ".join( vector ) + " }"
      return name
   # def __str__

   def info( self, **kwargs ):
      tabulations: int = kwargs.get( "tabulations", 0 )
      pfw.console.debug.info( self.__class__.__name__, ":", tabs = ( tabulations + 0 ) )
      pfw.console.debug.info( "version:         \'", self.__version, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "name:            \'", self.__name, "\'", tabs = ( tabulations + 1 ) )
      pfw.console.debug.info( "url:             \'", self.__url, "\'", tabs = ( tabulations + 1 ) )
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
      self.__image.mount( self.__directories.source( ), False )
      pfw.shell.execute(
              "sudo -S tar", "-xvf"
            , self.__directories.download( self.__archive_name )
            , "--checkpoint=100"
            , "--directory=" + self.__directories.source( )
         )
      self.__image.umount( )
   # def extract

   def sync( self, **kwargs ):
      # self.download( )
      self.extract( )
   # def sync

   def configure( self, **kwargs ):
      kw_directory = kwargs.get( "directory", self.__directories.source( ) )
      kw_hostname = kwargs.get( "hostname", "HOSTNAME" )
      # kw_user = kwargs.get( "user", { "name": "tda", "password": None, "hashed_password": "tdmKnqw7OFw2o" } )

      self.init( )

      # Setup /etc/hostname
      command = f"echo '{kw_hostname}' > /etc/hostname"
      pfw.shell.execute( command, chroot_bash = kw_directory, output = pfw.shell.eOutput.PTY )

      # Setup /etc/hosts
      command = f"echo '127.0.0.1   localhost' > /etc/hosts"
      pfw.shell.execute( command, chroot_bash = kw_directory, output = pfw.shell.eOutput.PTY )
      command = f"echo '127.0.1.1   {kw_hostname}' >> /etc/hosts"
      pfw.shell.execute( command, chroot_bash = kw_directory, output = pfw.shell.eOutput.PTY )
      command = f"echo '' >> /etc/hosts"
      pfw.shell.execute( command, chroot_bash = kw_directory, output = pfw.shell.eOutput.PTY )
      command = f"echo '# The following lines are desirable for IPv6 capable hosts' >> /etc/hosts"
      pfw.shell.execute( command, chroot_bash = kw_directory, output = pfw.shell.eOutput.PTY )
      command = f"echo '::1         ip6-localhost ip6-loopback' >> /etc/hosts"
      pfw.shell.execute( command, chroot_bash = kw_directory, output = pfw.shell.eOutput.PTY )
      command = f"echo 'fe00::0     ip6-localnet' >> /etc/hosts"
      pfw.shell.execute( command, chroot_bash = kw_directory, output = pfw.shell.eOutput.PTY )
      command = f"echo 'ff00::0     ip6-mcastprefix' >> /etc/hosts"
      pfw.shell.execute( command, chroot_bash = kw_directory, output = pfw.shell.eOutput.PTY )
      command = f"echo 'ff02::1     ip6-allnodes' >> /etc/hosts"
      pfw.shell.execute( command, chroot_bash = kw_directory, output = pfw.shell.eOutput.PTY )
      command = f"echo 'ff02::2     ip6-allrouters' >> /etc/hosts"
      pfw.shell.execute( command, chroot_bash = kw_directory, output = pfw.shell.eOutput.PTY )

      # Setup /etc/fstab
      command = f"echo 'proc        /proc       proc     defaults             0     0' > /etc/fstab"
      pfw.shell.execute( command, chroot_bash = kw_directory, output = pfw.shell.eOutput.PTY )
      command = f"echo '/dev/vda1   /boot       vfat     defaults             0     2' >> /etc/fstab"
      pfw.shell.execute( command, chroot_bash = kw_directory, output = pfw.shell.eOutput.PTY )
      command = f"echo '/dev/vda2   /           ext4     defaults,noatime     0     1' >> /etc/fstab"
      pfw.shell.execute( command, chroot_bash = kw_directory, output = pfw.shell.eOutput.PTY )

      # Setup /etc/resolv.conf
      # Setup internet connectivity in chroot
      # /etc/resolv.conf is required for internet connectivity in chroot.
      # It will get overwritten by dhcp, so don't get too attached to it.
      command = f"echo 'nameserver 8.8.8.8' > /etc/resolv.conf"
      pfw.shell.execute( command, chroot_bash = kw_directory, output = pfw.shell.eOutput.PTY )
      command = f"echo 'nameserver 2001:4860:4860::8888' >> /etc/resolv.conf"
      pfw.shell.execute( command, chroot_bash = kw_directory, output = pfw.shell.eOutput.PTY )

      # Setup /etc/apt/sources.list
      # Setup apt source list
      command = "sed -i -e \"s/# deb /deb /\" /etc/apt/sources.list"
      pfw.shell.execute( command, chroot = kw_directory, output = pfw.shell.eOutput.PTY )

      # Configure /tmp directory
      command = f"chmod 1777 /tmp"
      pfw.shell.execute( command, chroot = kw_directory, output = pfw.shell.eOutput.PTY )

      # Create user
      if None != kw_user:
         command = f"useradd -s /bin/bash -G adm,sudo -m"
         if None != kw_user['hashed_password']:
            command += f" -p {kw_user['hashed_password']}"
         elif None != kw_user['password']:
            pwd = pfw.password.build_hashed_password( kw_user['password'] )
            if None != pwd:
               command += f" -p {pwd}"
         command += f" {kw_user['name']}"
         self.execute( command )

      self.deinit( )
   # def configure

   def build( self, **kwargs ):
      kw_directory = kwargs.get( "directory", self.__directories.source( ) )
      kw_packages = kwargs.get( "packages", ubuntu.packages_all )

      self.init( )

      # Update and upgrade packages
      self.execute( f"apt update" )
      self.execute( f"apt -y upgrade" )
      self.execute( f"apt clean all" )

      # Install required packages
      for package in kw_packages:
         self.execute( f"apt install -y {package}", method = "system" )

      # self.execute( f"locale-gen en_US en_US.UTF-8" )
      # self.execute( f"dpkg-reconfigure locales" )
      # self.execute( f"update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8" )

      self.deinit( )
   # def build

   def install( self ):
      pass
   # def build

   def clean( self, **kwargs ):
      pfw.shell.execute( f"sudo -S rm -rf {self.__directories.source( )}", output = pfw.shell.eOutput.PTY )
      pfw.shell.execute( f"sudo -S rm -rf {self.__directories.build( )}", output = pfw.shell.eOutput.PTY )
   # def clean

   def deploy( self, **kwargs ):
      pass
   # def deploy

   def run( self, **kwargs ):
      self.init( )
      self.execute( f"bash", bash = False )
      self.deinit( )
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

   def init( self, **kwargs ):
      kw_directory = kwargs.get( "directory", self.__directories.source( ) )

      self.__image.mount( self.__directories.source( ), False )
      pfw.os.signal.add_handler( signal.SIGINT, signal_handler, object = self )

      # Mounting required host stuff
      pfw.shell.execute( f"sudo -S mount -o bind /proc {kw_directory}/proc", output = pfw.shell.eOutput.PTY )
      pfw.shell.execute( f"sudo -S mount -o bind /dev {kw_directory}/dev", output = pfw.shell.eOutput.PTY )
      pfw.shell.execute( f"sudo -S mount -o bind /dev/pts {kw_directory}/dev/pts", output = pfw.shell.eOutput.PTY )
      pfw.shell.execute( f"sudo -S mount -o bind /sys {kw_directory}/sys", output = pfw.shell.eOutput.PTY )
      pfw.shell.execute( f"sudo -S mount -o bind /tmp {kw_directory}/tmp", output = pfw.shell.eOutput.PTY )
   # def init

   def deinit( self, **kwargs ):
      kw_directory = kwargs.get( "directory", self.__directories.source( ) )

      # Unmounting required host stuff
      pfw.shell.execute( f"sudo -S umount {kw_directory}/tmp", output = pfw.shell.eOutput.PTY )
      pfw.shell.execute( f"sudo -S umount {kw_directory}/sys", output = pfw.shell.eOutput.PTY )
      pfw.shell.execute( f"sudo -S umount {kw_directory}/dev/pts", output = pfw.shell.eOutput.PTY )
      pfw.shell.execute( f"sudo -S umount {kw_directory}/dev", output = pfw.shell.eOutput.PTY )
      pfw.shell.execute( f"sudo -S umount {kw_directory}/proc", output = pfw.shell.eOutput.PTY )

      pfw.os.signal.remove_handler( signal.SIGINT, signal_handler )
      self.__image.umount( )
   # def deinit

   def execute( self, cmd: str, **kwargs ):
      kw_directory = kwargs.get( "directory", self.__directories.source( ) )
      kw_bash = kwargs.get( "bash",True )
      kw_method = kwargs.get( "method","subprocess" )

      command = f"bash -c \"{cmd}\"" if True == kw_bash else cmd         
      pfw.shell.execute( command, chroot = kw_directory, method = kw_method, output = pfw.shell.eOutput.PTY )
   # def execute



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
   __archive_name: str = None
   __image: pfw.image.Partition = None
   __directories: linux.base.Directories = None
   __config: linux.base.Configuration = None
# class Rootfs
