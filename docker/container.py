#!/usr/bin/python3

import os
import subprocess
import re

import pfw.console
import pfw.shell
import pfw.docker
import pfw.password

import configuration



def create( **kwargs ):
   kw_name = kwargs.get( "name", None )
   kw_image = kwargs.get( "image", None )
   kw_user = kwargs.get( "user", "builder" )
   kw_volume_mapping = [
            pfw.docker.Container.Mapping( f"/mnt/docker/{kw_name}", f"/mnt/host" ),
            pfw.docker.Container.Mapping( f"~/.ssh", f"/home/{kw_user}/.ssh" ),
            pfw.docker.Container.Mapping( f"~/.gitconfig", f"/home/{kw_user}/.gitconfig" ),
         ]
   kw_port_mapping = [
            pfw.docker.Container.Mapping( "5000", "5000" ),
         ]

   container: pfw.docker.Container = pfw.docker.Container(
         name = f"{kw_name}",
         hostname = "host",
         image = kw_image,
         volume_mapping = kw_volume_mapping,
         port_mapping = kw_port_mapping
      )
   container.create( )

   return container
# def create

def init( container: pfw.docker.Container, **kwargs ):
   kw_packages = kwargs.get( "packages", [ ] )
   kw_user = kwargs.get( "user", "builder" )
   kw_pwd = kwargs.get( "pwd", "builder" )
   kw_pwd_hashed = pfw.password.build_hashed_password( {kw_pwd}, "tda" ) if kw_pwd else None

   container.exec( "apt update" )
   container.exec( "apt upgrade" )
   container.exec( "ln -snf /usr/share/zoneinfo/UTC /etc/localtime && echo UTC > /etc/timezone" )
   for package in kw_packages:
      container.exec( f"apt install -y {package}" )
   container.exec( "apt install --reinstall -y ca-certificates" )
   container.exec( "apt clean all" )
   container.exec( "rm -rf /tmp/* /var/tmp/*" )
   container.exec( "locale-gen en_US.UTF-8" )
   container.exec( "update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 LANGUAGE=en_US" )
   # container.exec( "dpkg-reconfigure locales" )
   if None != kw_user:
      command = "useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash -G adm,sudo"
      command += f" -p {kw_pwd_hashed}" if kw_pwd_hashed else ""
      command += " {kw_user}"
# def init

def start( container: pfw.docker.Container, **kwargs ):
   container.start( )
# def start

def stop( container: pfw.docker.Container, **kwargs ):
   container.stop( )
# def stop

def commit( container: pfw.docker.Container, **kwargs ):
   kw_image = kwargs.get( "image", None )
   kw_user = kwargs.get( "user", "builder" )

   container.commit(
         image = kw_image,
         change = { "USER": {kw_user}, "ENV": [ "PATH ~/.local/bin:\${PATH}" ] }
      )
# def stop

def build( **kwargs ):
   container: pfw.docker.Container = create( **kwargs )
   start( container, **kwargs )
   init( container, **kwargs )
   stop( container, **kwargs )

   return container
# def build
