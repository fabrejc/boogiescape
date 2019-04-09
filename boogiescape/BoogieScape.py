#! /usr/bin/env python3
# -*- coding: utf-8 -*-


__license__ = "GPLv3"
__author__ = "Jean-Christophe Fabre <jean-christophe.fabre@inra.fr>"
__email__ = "jean-christophe.fabre@inra.fr"


######################################################
######################################################


import os
import shutil
import sys
import networkx

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

    self._InputREFields = {'OFLD_ID': 'Integer64'}
    self._InputRSFields = {'OFLD_ID': 'Integer64','OFLD_TO': 'String','OFLD_PSORD': 'Integer64',
                           'slope': 'Real', 'length': 'Real', 'width': 'Real', 'height': 'Real', 'drainarea': 'Real', 'xposition': 'Real', 'yposition': 'Real',
                           'GUconnect': 'Integer'}
    self._InputSUFields = {'OFLD_ID': 'Integer64','OFLD_TO': 'String','OFLD_PSORD': 'Integer64',
                           'slope': 'Real', 'area': 'Real', 'xposition': 'Real', 'yposition': 'Real', 'flowdist': 'Real', 'SCSlanduse': 'Integer64', 'SCSsoil': 'String',
                           'AWC': 'String', 'clay': 'String', 'soilbulkd': 'String', 'zsoillayer': 'String', 'nmanning': 'Real', 'Ksat': 'String', 'zrootmax': 'Real', 
                           'soilcode': 'String', 'equipment': 'String', 'pRHt_ini': 'Real', 'rotation': 'String', 'FROM_AP': 'String'}

    self._SHPDriver = ogr.GetDriverByName('ESRI Shapefile')


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
  def _printActionDone(Text="Done"):
    print(Text)


  ######################################################


  @staticmethod
  def _printActionFailed(Text="Failed",Fatal=1):
    print(Text)

    if Fatal:
      sys.exit(Fatal)


  ######################################################


  def _checkLayerFieldsTypes(self,DataSource,ExpectedFields):
    FoundFields = dict()
    
    LayerDefn = DataSource.GetLayer().GetLayerDefn()

    for i in range(LayerDefn.GetFieldCount()):
      FoundFields[LayerDefn.GetFieldDefn(i).GetName()] = LayerDefn.GetFieldDefn(i).GetFieldTypeName(LayerDefn.GetFieldDefn(i).GetType())

    #print(FoundFields)

    for k,v in ExpectedFields.items():
      self._printActionStarted("Checking field {}".format(k))
      if k in FoundFields:
        if ExpectedFields[k] == FoundFields[k]:
          self._printActionDone()
        else:
          self._printActionFailed("Failed (wrong type : {} expected, {} found)".format(ExpectedFields[k],FoundFields[k]))
      else:
        self._printActionFailed("Failed (not found)")


  ######################################################


  def _prepare(self):
    self._printStage("Preparing")
    
    self._printActionStarted("Checking input directory {}".format(self._inputPath))
    if os.path.isdir(self._inputPath):
      self._printActionDone()
    else:
      self._printActionFailed(Fatal=1)

    self._printActionStarted("Creating output directory {}".format(self._outputPath))
    if os.path.isdir(self._outputPath):
      if "overwrite" in self._extraArgs:
        shutil.rmtree(self._outputPath, ignore_errors=True)
      else:
        self._printActionFailed(Text="Failed (already exists)",Fatal=1)
    os.makedirs(self._outputPath)
    self._printActionDone()


  ######################################################


  def _createGU(self):
    self._printStage("Creating GU")
    
    self._printActionStarted("Opening input RS file")
    RSSource = self._SHPDriver.Open(self.getInputPath(self._RSFile), 0) # 0 means read-only. 1 means writeable.
    if RSSource is None:
      self._printActionFailed("Failed (could not open {})".format(self.getInputPath(self._RSFile)))
    else:
      self._printActionDone()

    self._checkLayerFieldsTypes(RSSource,self._InputRSFields)


    self._printActionStarted("Opening input SU file")
    SUSource = self._SHPDriver.Open(self.getInputPath(self._SUFile), 0) # 0 means read-only. 1 means writeable.
    if SUSource is None:
      self._printActionFailed("Failed (could not open {})".format(self.getInputPath(self._SUFile)))
    else:
      self._printActionDone()
    
    self._checkLayerFieldsTypes(SUSource,self._InputSUFields)

    G = networkx.DiGraph()

    self._printActionStarted("Adding RS to graph")
    self._printActionDone("not done")
    
    self._printActionStarted("Adding SU to graph")
    self._printActionDone("not done")

    self._printActionStarted("Adding connections to graph")
    self._printActionDone("not done")

    self._printActionStarted("Printing graph to file")
    # print graph using dot
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
    #self._createAP()
    self._createGU()
    self._cleanup()