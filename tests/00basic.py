# -*- coding: utf-8 -*-

__author__  = "Jean-Christophe Fabre"
__email__   = "jean-christophe.fabre@inra.fr"
__license__ = "see LICENSE file"


import sys
import unittest

from boogiescape import BoogieScape


######################################################
######################################################


class MainTest(unittest.TestCase):

  def testConstructor(self):
    BS = BoogieScape.BoogieScape('','',{})
    self.assertEqual(BS.getInputPath(),'')
    self.assertEqual(BS.getOutputPath(),'')
    self.assertEqual(BS.getExtraArgs(),{})
    
    BS = BoogieScape.BoogieScape('/path/input/path','/path/output/path',{'arg1' : 'value1','arg2' : 'value2'})
    self.assertEqual(BS.getInputPath(),'/path/input/path')
    self.assertEqual(BS.getOutputPath(),'/path/output/path')
    self.assertEqual(BS.getExtraArgs(),{'arg1' : 'value1','arg2' : 'value2'})


  ######################################################


  def testPaths(self):
    BS = BoogieScape.BoogieScape('/path/input/path','/path/output/path',{})
    self.assertEqual(BS.getInputPath('X.shp'),'/path/input/path/X.shp')
    self.assertEqual(BS.getOutputPath('Y.shp'),'/path/output/path/Y.shp')


  ######################################################


  def testUnitsClassSplit(self):
    Res = BoogieScape.BoogieScape.splitUnitsStrList("")
    print(Res)
    self.assertEqual(len(Res),0)
    Res = BoogieScape.BoogieScape.splitUnitsStrList("TU#99")
    print(Res)
    self.assertEqual(len(Res),1)
    Res = BoogieScape.BoogieScape.splitUnitsStrList("TU#99;UT#101")
    print(Res)
    self.assertEqual(len(Res),2)
    Res = BoogieScape.BoogieScape.splitUnitsStrList("TU#99;UT#101;TT#13")
    print(Res)
    self.assertEqual(len(Res),3)


######################################################
######################################################


if __name__ == '__main__':
  unittest.main()