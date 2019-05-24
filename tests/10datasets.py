# -*- coding: utf-8 -*-

__author__  = "Jean-Christophe Fabre"
__email__   = "jean-christophe.fabre@inra.fr"
__license__ = "see LICENSE file"


import os
import unittest

from boogiescape import BoogieScape


######################################################
######################################################


class MainTest(unittest.TestCase):

  @staticmethod
  def _getInput(DatasetName):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)),'datasets',DatasetName)

  ######################################################

  @staticmethod
  def _getOutput(DatasetName):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)),'_outputs',DatasetName)


  ######################################################


  def testZone0(self):
    BS = BoogieScape.BoogieScape(self._getInput('zone0'),self._getOutput('zone0'),
                                 {'overwrite' : True,'export_graph_view' : True})
    BS.run()


######################################################
######################################################


if __name__ == '__main__':
  unittest.main()