import git
from git import RemoteProgress
from tqdm import tqdm

import pfw.console



class CloneProgress( RemoteProgress ):
   def __init__( self ):
      super( ).__init__( )
      self.pbar = tqdm( )

   def updat( self, op_code, cur_count, max_count=None, message='' ):
      self.updat1( op_code, cur_count, max_count, message )

   def updat1( self, op_code, cur_count, max_count=None, message='' ):
      if message:
         pfw.console.debug.info( message )

   def updat2( self, op_code, cur_count, max_count=None, message='' ):
      if message:
         pfw.console.debug.info( 'update(%s, %s, %s, %s)' % (op_code, cur_count, max_count, message) )

   def updat3( self, op_code, cur_count, max_count=None, message='' ):
      pfw.console.debug.info( op_code, cur_count, max_count, cur_count / (max_count or 100.0), message or "NO MESSAGE" )

   def update4( self, op_code, cur_count, max_count=None, message='' ):
      self.pbar.total = max_count
      self.pbar.n = cur_count
      self.pbar.refresh( )

   def update5( self, op_code, cur_count, max_count=None, message='' ):
      pbar = tqdm( total=max_count )
      pbar.update( cur_count )
# class CloneProgress
