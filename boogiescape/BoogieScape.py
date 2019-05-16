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
import matplotlib.pyplot as plt

try:
    from osgeo import ogr, osr, gdal
except:
    sys.exit('ERROR: cannot find GDAL/OGR modules')

try:
    import pygraphviz
    from networkx.drawing.nx_agraph import graphviz_layout
except ImportError:
    try:
        import pydot
        from networkx.drawing.nx_pydot import graphviz_layout
    except ImportError:
        raise ImportError("Needs Graphviz and either PyGraphviz or pydot")

from . import Data


######################################################
######################################################


class BoogieScape():

  def __init__(self,inputPath,outputPath,extrArgs):
    self._inputPath = inputPath
    self._outputPath = outputPath
    self._extraArgs = extrArgs

    self._APData = list()
    self._GUData = list()

    self._APFile = 'AP.shp'
    self._GUFile = 'GU.shp'
    self._REFile = 'RE.shp'
    self._RSFile = 'RS.shp'
    self._SUFile = 'SU.shp'

    self._InputREFields = {'OFLD_ID': 'Integer64', 'OFLD_CHILD': 'String'}
    self._InputRSFields = {'OFLD_ID': 'Integer64','OFLD_TO': 'String','OFLD_PSORD': 'Integer64', 'OFLD_CHILD': 'String',
                           'slope': 'Real', 'length': 'Real', 'width': 'Real', 'height': 'Real', 'drainarea': 'Real', 'xposition': 'Real', 'yposition': 'Real',
                           'GUconnect': 'Integer'}
    self._InputSUFields = {'OFLD_ID': 'Integer64','OFLD_TO': 'String','OFLD_PSORD': 'Integer64',
                           'slope': 'Real', 'area': 'Real', 'xposition': 'Real', 'yposition': 'Real', 'flowdist': 'Real', 'SCSlanduse': 'Integer64', 'SCSsoil': 'String',
                           'AWC': 'String', 'clay': 'String', 'soilbulkd': 'String', 'zsoillayer': 'String', 'nmanning': 'Real', 'Ksat': 'String', 'zrootmax': 'Real', 
                           'soilcode': 'String', 'equipment': 'String', 'pRHt_ini': 'Real', 'rotation': 'String', 'FROM_AP': 'String'}

    self._SHPDriver = ogr.GetDriverByName('ESRI Shapefile')

    self._RESource = None
    self._RSSource = None
    self._SUSource = None


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

  @staticmethod
  def splitUnitsStrList(StrList):
    Ret = list()
    ClassUnitsList = list(filter(None,StrList.split(';')))
    for CUStr in ClassUnitsList:
      CUStr = CUStr.split("#")
      if len(CUStr) == 2:
        Ret.append(CUStr)

    return Ret

  ######################################################


  def _createOutputShapefile(self,Filename):

    self._printActionStarted("Creating output {}".format(Filename))
    FilePath = self.getOutputPath(Filename)
    if os.path.exists(FilePath):
      self._SHPDriver.DeleteDataSource(FilePath)
    Source = self._SHPDriver.CreateDataSource(FilePath)

    if Source is None:
      self._printActionFailed("Failed (could not create {})".format(APFilePath))
    else:
      self._printActionDone()

    return Source


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

    ## Opening RS file
    self._printActionStarted("Opening input RS file")
    self._RSSource = self._SHPDriver.Open(self.getInputPath(self._RSFile), 0) # 0 means read-only. 1 means writeable.
    if self._RSSource is None:
      self._printActionFailed("Failed (could not open {})".format(self.getInputPath(self._RSFile)))
    else:
      self._printActionDone()

    self._checkLayerFieldsTypes(self._RSSource,self._InputRSFields)

    ## Opening SU file
    self._printActionStarted("Opening input SU file")
    self._SUSource = self._SHPDriver.Open(self.getInputPath(self._SUFile), 0) # 0 means read-only. 1 means writeable.
    if self._SUSource is None:
      self._printActionFailed("Failed (could not open {})".format(self.getInputPath(self._SUFile)))
    else:
      self._printActionDone()
    
    self._checkLayerFieldsTypes(self._SUSource,self._InputSUFields)

   ## Opening RE file
    self._printActionStarted("Opening input RE file")
    self._RESource = self._SHPDriver.Open(self.getInputPath(self._REFile), 0) # 0 means read-only. 1 means writeable.
    if self._RESource is None:
      self._printActionFailed("Failed (could not open {})".format(self.getInputPath(self._REFile)))
    else:
      self._printActionDone()
    
    self._checkLayerFieldsTypes(self._RESource,self._InputREFields)


  ######################################################


  def _appendAPFromSource(self,OtherSource,OtherClass,PcsOrd):

    OtherLayer = OtherSource.GetLayer(0)
    OtherLayer.ResetReading()

    for OtherFeature in OtherLayer:
      OtherID = OtherFeature.GetField("OFLD_ID")
      ChildStr = OtherFeature.GetField("OFLD_CHILD")
      if ChildStr:
        Children = self.splitUnitsStrList(ChildStr)
        for CUStr in Children:
          if CUStr[0] == "AP":
            self._printActionStarted("Creating AP#{} from {}#{}".format(CUStr[1],OtherClass,OtherID))
            OtherCentroid = OtherFeature.GetGeometryRef().Centroid()

            Unit = Data.SpatialUnit()
            Unit.Geometry = OtherCentroid

            SUList = list()
            if self._SUSource:
              SULayer = self._SUSource.GetLayer(0)
              SULayer.ResetReading()

              for SUFeature in SULayer:
                FromAP = int(SUFeature.GetField("FROM_AP"))
                if FromAP == int(CUStr[1]):
                  SUList.append(["SU",int(SUFeature.GetField("OFLD_ID"))])

            Unit.Id = int(CUStr[1])
            Unit.PcsOrd = int(PcsOrd)
            Unit.To = SUList
            self._APData.append(Unit)
            self._printActionDone()


  ######################################################


  def _createAP(self):
    self._printStage("Creating AP")

    self._appendAPFromSource(self._RSSource,"RS",1)
    self._appendAPFromSource(self._RESource,"RE",2)


  ######################################################


  def _createGU(self):

    self._printStage("Creating GU")

    RSLayer = self._RSSource.GetLayer(0)
    RELayer = self._RESource.GetLayer(0)
    SULayer = self._SUSource.GetLayer(0)


    G = networkx.DiGraph()

    self._printActionStarted("Adding RS to graph")

    RSLayer.ResetReading()
    for RSFeature in RSLayer:
      Id = int(RSFeature.GetField("OFLD_ID"))
      Unit = Data.SpatialUnit()
      Unit.Id = Id
      ToList = RSFeature.GetField("OFLD_TO")
      if ToList:
        Unit.To =  self.splitUnitsStrList(ToList)
      
      Unit.Attributes["GUconnect"] = (RSFeature.GetField("GUconnect") > 0)

      G.add_node("RS#{}".format(Id),data=Unit)

    self._printActionDone("not done")
    

    self._printActionStarted("Adding SU to graph")

    SULayer.ResetReading()
    for SUFeature in SULayer:
      Id = int(SUFeature.GetField("OFLD_ID"))
      Unit = Data.SpatialUnit()
      Unit.Id = Id
      ToList = SUFeature.GetField("OFLD_TO")
      if ToList:
        Unit.To =  self.splitUnitsStrList(ToList)

      G.add_node("SU#{}".format(Id),data=Unit)

    self._printActionDone("not done")


    self._printActionStarted("Adding RE to graph")

    RELayer.ResetReading()
    for REFeature in RELayer:
      Id = int(REFeature.GetField("OFLD_ID"))
      Unit = Data.SpatialUnit()
      Unit.Id = Id
      ToList = REFeature.GetField("OFLD_TO")
      if ToList:
        Unit.To =  self.splitUnitsStrList(ToList)

      G.add_node("RE#{}".format(Id),data=Unit)

    self._printActionDone("not done")


    self._printActionStarted("Adding connections to graph")

    for FromNode in list(G.nodes):
      ToList = G.nodes[FromNode]['data'].To
      for ToUnit in ToList:
        ToNode = "{}#{}".format(ToUnit[0],ToUnit[1])
      
      # do not connect source RS (GUconnect=1) to downstream
      if FromNode.startswith("RS") and G.nodes[FromNode]['data'].Attributes["GUconnect"] :
        pass
      else :
        G.add_edge(FromNode,ToNode)

    self._printActionDone("not done")


    self._printActionStarted("Printing graph to file")
    pos = graphviz_layout(G, prog='dot')
    plt.figure(figsize=(20, 20))
    networkx.draw(G, pos, node_size=300, alpha=0.5, node_color="blue", with_labels=True)
    plt.axis('equal')
    plt.savefig(self.getOutputPath("graph.pdf"))
    self._printActionDone("done")


    # To be reviewed and rewritten (mixed?) from here ...
    
    GUId = 0
    RSLayer.ResetReading()

    for RSFeature in RSLayer:
      if int(RSFeature.GetField("GUconnect")):
        GUId += 1
        RSId = int(RSFeature.GetField("OFLD_ID"))
        self._printActionStarted("Creating GU#{} from RS#{}".format(GUId,RSId))

        Unit = Data.SpatialUnit()
        Unit.Id = GUId
        Unit.PcsOrd = 1
        Unit.To.append(["RS",RSId])
        self._GUData.append(Unit)
        self._printActionDone("not done")


    self._printActionStarted("Building GU")
    for Node in list(G.nodes):
      if not len(list(G.successors(Node))):
        print(Node,list(networkx.ancestors(G,Node)))

    self._printActionDone("not done")

    # ... to here


  ######################################################


  def _writeOutputFiles(self):
    self._printStage("Writing output GIS files")

    ##### AP

    APSource = self._createOutputShapefile(self._APFile)

    self._printActionStarted("Populating AP.shp ")

    APLayer = APSource.CreateLayer("AP",None,ogr.wkbPoint)
    APLayerDefn = APLayer.GetLayerDefn()

    FieldDefn = ogr.FieldDefn("OFLD_ID",ogr.OFTInteger)
    APLayer.CreateField(FieldDefn)
    FieldDefn = ogr.FieldDefn("OFLD_PSORD",ogr.OFTInteger)
    APLayer.CreateField(FieldDefn)
    FieldDefn = ogr.FieldDefn("OFLD_TO",ogr.OFTString)
    FieldDefn.SetWidth(254)
    APLayer.CreateField(FieldDefn)
    FieldDefn = ogr.FieldDefn("xposition",ogr.OFTReal)
    APLayer.CreateField(FieldDefn)
    FieldDefn = ogr.FieldDefn("yposition",ogr.OFTReal)
    APLayer.CreateField(FieldDefn)

    for SpatialUnit in self._APData:
      APFeature = ogr.Feature(APLayerDefn)

      APFeature.SetField("OFLD_ID",SpatialUnit.Id)
      APFeature.SetField("OFLD_PSORD",SpatialUnit.PcsOrd)
      
      SUList = list()
      for ToUnit in SpatialUnit.To:
        SUList.append("{}#{}".format(ToUnit[0],ToUnit[1]))
      APFeature.SetField("OFLD_TO",";".join(SUList))
      
      APFeature.SetField("xposition",SpatialUnit.Geometry.GetX())
      APFeature.SetField("yposition",SpatialUnit.Geometry.GetY())
      APFeature.SetGeometry(SpatialUnit.Geometry)
      APLayer.CreateFeature(APFeature)
      APFeature = None 

    self._printActionDone()


    ##### GU

    GUSource = self._createOutputShapefile(self._GUFile)
    
    self._printActionStarted("Populating GU.shp ")

    GULayer = GUSource.CreateLayer("GU",None,ogr.wkbMultiPolygon)
    GULayerDefn = GULayer.GetLayerDefn()

    FieldDefn = ogr.FieldDefn("OFLD_ID",ogr.OFTInteger)
    GULayer.CreateField(FieldDefn)
    FieldDefn = ogr.FieldDefn("OFLD_PSORD",ogr.OFTInteger)
    GULayer.CreateField(FieldDefn)
    FieldDefn = ogr.FieldDefn("OFLD_TO",ogr.OFTString)
    FieldDefn.SetWidth(254)
    GULayer.CreateField(FieldDefn)
    FieldDefn = ogr.FieldDefn("xposition",ogr.OFTReal)
    GULayer.CreateField(FieldDefn)
    FieldDefn = ogr.FieldDefn("yposition",ogr.OFTReal)
    GULayer.CreateField(FieldDefn)
    FieldDefn = ogr.FieldDefn("area",ogr.OFTReal)
    GULayer.CreateField(FieldDefn)


    for SpatialUnit in self._GUData:
      GUFeature = ogr.Feature(GULayerDefn)

      GUFeature.SetField("OFLD_ID",SpatialUnit.Id)
      GUFeature.SetField("OFLD_PSORD",SpatialUnit.PcsOrd)

      RSList = list()
      for ToUnit in SpatialUnit.To:
        RSList.append("{}#{}".format(ToUnit[0],ToUnit[1]))
      GUFeature.SetField("OFLD_TO",";".join(RSList))
      
      #GUFeature.SetField("xposition",SpatialUnit.Geometry.GetX())
      #GUFeature.SetField("yposition",SpatialUnit.Geometry.GetY())
      #GUFeature.SetGeometry(SpatialUnit.Geometry)
      GULayer.CreateFeature(GUFeature)
      GUFeature = None 

    self._printActionDone("not done")


    self._printStage("Writing output FluidX files")
    self._printActionStarted("Creating domain.fluidx file")
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
    self._createAP()
    self._createGU()
    self._writeOutputFiles()
    self._cleanup()