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

  _SHPDriver = ogr.GetDriverByName('ESRI Shapefile')

  def __init__(self,inputPath,outputPath,extrArgs):
    self._inputPath = inputPath
    self._outputPath = outputPath
    self._extraArgs = extrArgs

    self._APData = dict()
    self._GUData = dict()
    self._REData = dict()
    self._RSData = dict()
    self._SUData = dict()

    self._APFile = 'AP.shp'
    self._GUFile = 'GU.shp'
    self._REFile = 'RE.shp'
    self._RSFile = 'RS.shp'
    self._SUFile = 'SU.shp'

    self._InputREFields = {'OFLD_ID': 'Integer64', 'OFLD_CHILD': 'String', 'OFLD_PSORD': 'Integer64',
                           'areamax': 'Real', 'inivolume': 'Real', 'volumemax': 'Real', 'drainarea': 'Real',
                           'xposition': 'Real', 'yposition': 'Real' }
    self._InputRSFields = {'OFLD_ID': 'Integer64','OFLD_TO': 'String',  'OFLD_CHILD': 'String',
                           'slope': 'Real', 'length': 'Real', 'width': 'Real', 'height': 'Real', 'drainarea': 'Real', 
                           'xposition': 'Real', 'yposition': 'Real', 'GUconnect': 'Integer'}
    self._InputSUFields = {'OFLD_ID': 'Integer64','OFLD_TO': 'String','OFLD_PSORD': 'Integer64',
                           'slope': 'Real', 'area': 'Real', 'xposition': 'Real', 'yposition': 'Real', 'flowdist': 'Real', 'SCSlanduse': 'Integer64', 'SCSsoil': 'String',
                           'AWC': 'String', 'clay': 'String', 'soilbulkd': 'String', 'zsoillayer': 'String', 'nmanning': 'Real', 'Ksat': 'String', 'zrootmax': 'Real', 
                           'soilcode': 'String', 'equipment': 'String', 'pRHt_ini': 'Real', 'rotation': 'String', 'FROM_AP': 'String'}

    self._RESource = None
    self._RSSource = None
    self._SUSource = None


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


  @staticmethod
  def _checkLayerFieldsTypes(DataSource,ExpectedFields):
    FoundFields = dict()
    
    LayerDefn = DataSource.GetLayer().GetLayerDefn()

    for i in range(LayerDefn.GetFieldCount()):
      FoundFields[LayerDefn.GetFieldDefn(i).GetName()] = LayerDefn.GetFieldDefn(i).GetFieldTypeName(LayerDefn.GetFieldDefn(i).GetType())

    for k,v in ExpectedFields.items():
      BoogieScape._printActionStarted("Checking field {}".format(k))
      if k in FoundFields:
        if ExpectedFields[k] == FoundFields[k]:
          BoogieScape._printActionDone()
        else:
          BoogieScape._printActionFailed("Failed (wrong type : {} expected, {} found)".format(ExpectedFields[k],FoundFields[k]))
      else:
        BoogieScape._printActionFailed("Failed (not found)")


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


  @staticmethod
  def _loadShapefile(FilePath,ExpectedFields,UnitsClass):

    BoogieScape._printActionStarted("Opening input {} file".format(UnitsClass))
    Source = BoogieScape._SHPDriver.Open(FilePath, 0) # 0 means read-only. 1 means writeable.
    if Source is None:
      BoogieScape._printActionFailed("Failed (could not open {})".format(self.getInputPath(self._RSFile)))
    else:
      BoogieScape._printActionDone()

    BoogieScape._checkLayerFieldsTypes(Source,ExpectedFields)

    UnitsData = dict()

    Layer = Source.GetLayer(0)
    Layer.ResetReading()

    for Feature in Layer:
      Unit = Data.SpatialUnit()
      Unit.Geometry = ogr.CreateGeometryFromWkb(Feature.GetGeometryRef().ExportToWkb())
      
      for Field,Type in ExpectedFields.items():
        if Field == "OFLD_ID":
          Unit.Id = Feature.GetField(Field)
        elif Field == "OFLD_PSORD":
          Unit.PcsOrd = Feature.GetField(Field)
        elif Field == "OFLD_TO":
          ToStrList = Feature.GetField(Field)
          if ToStrList:
            Unit.To =  BoogieScape.splitUnitsStrList(ToStrList)
        elif Field == "OFLD_CHILD":
          ChildStrList = Feature.GetField(Field)
          if ChildStrList:
            Unit.Child =  BoogieScape.splitUnitsStrList(ChildStrList)
        else:
          Unit.Attributes[Field] = Feature.GetField(Field)

      UnitsData[Unit.Id] = Unit

    return UnitsData


  ######################################################

  
  @staticmethod
  def _createShapefile(FilePath):

    BoogieScape._printActionStarted("Creating output {}".format(os.path.basename(FilePath)))
    if os.path.exists(FilePath):
      BoogieScape._SHPDriver.DeleteDataSource(FilePath)
    Source = BoogieScape._SHPDriver.CreateDataSource(FilePath)

    if Source is None:
      BoogieScape._printActionFailed("Failed (could not create {})".format(APFilePath))
    else:
      BoogieScape._printActionDone()

    return Source


  ######################################################


  def _prepare(self):
    BoogieScape._printStage("Preparing")
    
    BoogieScape._printActionStarted("Checking input directory {}".format(self._inputPath))
    if os.path.isdir(self._inputPath):
      BoogieScape._printActionDone()
    else:
      BoogieScape._printActionFailed(Fatal=1)

    BoogieScape._printActionStarted("Creating output directory {}".format(self._outputPath))
    if os.path.isdir(self._outputPath):
      if "overwrite" in self._extraArgs:
        shutil.rmtree(self._outputPath, ignore_errors=True)
      else:
        BoogieScape._printActionFailed(Text="Failed (already exists)",Fatal=1)
    os.makedirs(self._outputPath)
    BoogieScape._printActionDone()

    ## Opening RS file
    self._RSData = BoogieScape._loadShapefile(self.getInputPath(self._RSFile),self._InputRSFields,"RS")

    ## Opening SU file
    self._SUData = BoogieScape._loadShapefile(self.getInputPath(self._SUFile),self._InputSUFields,"SU")

    ## Opening RE file
    self._REData = BoogieScape._loadShapefile(self.getInputPath(self._REFile),self._InputREFields,"RE")


  ######################################################


  def _appendAPFromSource(self,OtherData,OtherClass,PcsOrd):

    for k,OtherUnit in OtherData.items():
      for Child in OtherUnit.Child:
        if Child[0] == "AP":
          BoogieScape._printActionStarted("Creating AP#{} from {}#{}".format(Child[1],OtherClass,OtherUnit.Id))
          Unit = Data.SpatialUnit()
          Unit.Geometry = OtherUnit.Geometry.Centroid()

          SUList = list()
          for k,SUUnit in self._SUData.items():
            FromAP = int(SUUnit.Attributes["FROM_AP"])
            if FromAP == int(Child[1]):
              SUList.append(["SU",SUUnit.Id])
          
          Unit.Id = Child[1]
          Unit.PcsOrd = int(PcsOrd)
          Unit.To = SUList
          self._APData[Unit.Id] = Unit
          BoogieScape._printActionDone()


  ######################################################


  def _createAP(self):
    BoogieScape._printStage("Creating AP")

    self._appendAPFromSource(self._RSData,"RS",1)
    self._appendAPFromSource(self._REData,"RE",2)


  ######################################################


  def _createGU(self):

    BoogieScape._printStage("Creating GU")

    G = networkx.DiGraph()

    BoogieScape._printActionStarted("Adding RS to graph")
    for k,RSUnit in self._RSData.items():
      G.add_node("RS#{}".format(RSUnit.Id),data=RSUnit)
    BoogieScape._printActionDone("done")
    
    BoogieScape._printActionStarted("Adding SU to graph")
    for k,SUUnit in self._SUData.items():
      G.add_node("SU#{}".format(SUUnit.Id),data=SUUnit)
    BoogieScape._printActionDone("done")

    BoogieScape._printActionStarted("Adding RE to graph")
    for k,REUnit in self._REData.items():
      G.add_node("RE#{}".format(REUnit.Id),data=REUnit)
    BoogieScape._printActionDone("done")


    BoogieScape._printActionStarted("Adding connections to graph")

    for FromNode in list(G.nodes):
      ToList = G.nodes[FromNode]['data'].To
      for ToUnit in ToList:
        ToNode = "{}#{}".format(ToUnit[0],ToUnit[1])
      
      # do not connect source RS (GUconnect=1) to downstream
      if FromNode.startswith("RS") and G.nodes[FromNode]['data'].Attributes["GUconnect"] :
        pass
      else :
        G.add_edge(FromNode,ToNode)

    BoogieScape._printActionDone()


    BoogieScape._printActionStarted("Printing graph to file")
    pos = graphviz_layout(G, prog='dot')
    plt.figure(figsize=(20, 20))
    networkx.draw(G, pos, node_size=300, alpha=0.5, node_color="blue", with_labels=True)
    plt.axis('equal')
    plt.savefig(self.getOutputPath("graph.pdf"))
    BoogieScape._printActionDone("done")
    

    GUId = 1

    for k,RSUnit in self._RSData.items():
      if int(RSUnit.Attributes["GUconnect"]) > 0:
        UnitStr = "RS#{}".format(RSUnit.Id)
        BoogieScape._printActionStarted("Creating GU#{} from {}".format(GUId,UnitStr))
        
        MultiPolygon = ogr.Geometry(ogr.wkbMultiPolygon)
        Area = 0
        for UpUnit in list(networkx.ancestors(G,UnitStr)):
          if "area" in G.node[UpUnit]['data'].Attributes:
            Area += G.node[UpUnit]['data'].Attributes['area']
            MultiPolygon.AddGeometry(G.node[UpUnit]['data'].Geometry)
         
        if Area > 0 : 
          Unit = Data.SpatialUnit()
          Unit.Id = GUId
          Unit.PcsOrd = 1
          Unit.To.append(["RS",RSUnit.Id])
          Unit.Attributes["area"] = Area
          Unit.Geometry = MultiPolygon
          self._GUData[Unit.Id] = Unit
          GUId += 1
          BoogieScape._printActionDone()
        else:
          BoogieScape._printActionDone("ignored")


  ######################################################


  def _writeOutputFiles(self):
    BoogieScape._printStage("Writing output GIS files")

    ##### AP

    APSource = BoogieScape._createShapefile(self.getOutputPath(self._APFile))

    BoogieScape._printActionStarted("Populating AP.shp ")

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

    for k,SpatialUnit in self._APData.items():
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

    BoogieScape._printActionDone()


    ##### GU

    GUSource = BoogieScape._createShapefile(self.getOutputPath(self._GUFile))
    
    BoogieScape._printActionStarted("Populating GU.shp ")

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


    for k,GUUnit in self._GUData.items():
      GUFeature = ogr.Feature(GULayerDefn)

      GUFeature.SetField("OFLD_ID",GUUnit.Id)
      GUFeature.SetField("OFLD_PSORD",GUUnit.PcsOrd)

      RSList = list()
      for ToUnit in GUUnit.To:
        RSList.append("{}#{}".format(ToUnit[0],ToUnit[1]))
      GUFeature.SetField("OFLD_TO",";".join(RSList))
      
      GUFeature.SetField("area",GUUnit.Attributes["area"])
      GUFeature.SetField("xposition",GUUnit.Geometry.Centroid().GetX())
      GUFeature.SetField("yposition",GUUnit.Geometry.Centroid().GetY())
      GUFeature.SetGeometry(GUUnit.Geometry)
      GULayer.CreateFeature(GUFeature)
      GUFeature = None 

    BoogieScape._printActionDone()


    BoogieScape._printStage("Writing output FluidX files")
    BoogieScape._printActionStarted("Creating domain.fluidx file")
    BoogieScape._printActionDone("not done")


######################################################


  def _cleanup(self):
    BoogieScape._printStage("Cleanup")


  ######################################################


  def getInputPath(self,relPath=None):
    if relPath:
      return os.path.join(self._inputPath,relPath)
    else:
      return self._inputPath


  ######################################################


  def run(self):
    self._prepare()
    self._createAP()
    self._createGU()
    self._writeOutputFiles()
    self._cleanup()