#! /usr/bin/env python3
# -*- coding: utf-8 -*-


__license__ = "GPLv3"
__author__ = "Jean-Christophe Fabre <jean-christophe.fabre@inra.fr>"
__email__ = "jean-christophe.fabre@inra.fr"


######################################################
######################################################


import os
import shutil

try:
    from osgeo import ogr, osr, gdal
except:
    sys.exit('ERROR: cannot find GDAL/OGR modules')


######################################################
######################################################


class BoogieScape():

  def __init__(self,inputPath,outputPath,extrArgs):
    self._inputPath = inputPath
    self._outputPath = outputPath
    self._extraArgs = extrArgs

    self._APFile = 'AP.shp'
    self._GUFile = 'GU.shp'
    self._REFile = 'RE.shp'
    self._RSFile = 'RS.shp'
    self._SUFile = 'SU.shp'    


  ######################################################


  @staticmethod
  def _printStage(Text):
    print("######",Text)


  ######################################################


  @staticmethod
  def _printActionStarted(Text):
    print("--",Text+"... ",end='')


  ######################################################


  @staticmethod
  def _printActionDone(Text):
    print(Text)


  ######################################################


  def _prepare(self):
    self._printStage("Preparing")
    self._printActionStarted("Checking input directory")
    self._printActionDone("not done")


  ######################################################


  def _createGU(self):
    self._printStage("Creating GU")
    self._printActionStarted("Checking input files")
    self._printActionDone("not done")


  ######################################################


  def _createAP(self):
    self._printStage("Creating AP")
    self._printActionStarted("Checking input files")
    self._printActionDone("not done")


  ######################################################


  def _cleanup(self):
    self._printStage("Cleanup")


  ######################################################


  def getInputPath(self,relPath=None):
    if relPath:
      return os.path.join(self._inputPath,relPath)
    else:
      return self._inputPath


  ######################################################


  def getOutputPath(self,relPath=None):
    if relPath:
      return os.path.join(self._outputPath,relPath)
    else:
      return self._outputPath


  ######################################################


  def getExtraArgs(self):
    return self._extraArgs


  ######################################################


  def run(self):
    self._prepare()
    self._createGU()
    self._cleanup()