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


def indentCRStr(Indent,Str):
  return "{}{}\n".format("  "*Indent,Str)


######################################################
######################################################


class BoogieScape():

  _SHPDriver = ogr.GetDriverByName('ESRI Shapefile')
  _GeoJSONDriver = ogr.GetDriverByName('GeoJSON')

  _ResourcesDir = os.path.join(os.path.dirname(os.path.abspath(__file__)),"resources")

  def __init__(self,inputPath,outputPath,extrArgs):
    self._inputPath = inputPath
    self._outputPath = outputPath
    self._extraArgs = extrArgs

    self._APData = dict()
    self._GUData = dict()
    self._REData = dict()
    self._RSData = dict()
    self._SUData = dict()

    self._APFileShp = 'AP.shp'
    self._APFileJson = 'AP.geojson'
    self._GUFileShp = 'GU.shp'
    self._GUFileJson = 'GU.geojson'
    self._REFileShp = 'RE.shp'
    self._REFileJson = 'RE.geojson'
    self._RSFileShp = 'RS.shp'
    self._RSFileJson = 'RS.geojson'
    self._SUFileShp = 'SU.shp'
    self._SUFileJson = 'SU.geojson'

    self._DomainFluidXFile = "domain.fluidx"
    self._DatastoreFluidXFile = "datastore.fluidx"

    self._InputREFields = {'OFLD_ID': ogr.OFTInteger64, 'OFLD_PSORD': ogr.OFTInteger64,
                           'OFLD_TO': ogr.OFTString, 'OFLD_CHILD': ogr.OFTString,
                           'areamax': ogr.OFTReal, 'inivolume': ogr.OFTReal, 'volumemax': ogr.OFTReal, 
                           'drainarea': ogr.OFTReal, 'slope': ogr.OFTReal,
                           'xposition': ogr.OFTReal, 'yposition': ogr.OFTReal }
    self._InputRSFields = {'OFLD_ID': ogr.OFTInteger64, 'OFLD_PSORD': ogr.OFTInteger64,
                           'OFLD_TO': ogr.OFTString,
                           'slope': ogr.OFTReal, 'length': ogr.OFTReal, 'width': ogr.OFTReal, 'height': ogr.OFTReal, 
                           'drainarea': ogr.OFTReal, 'nmanning' : ogr.OFTReal,
                           'xposition': ogr.OFTReal, 'yposition': ogr.OFTReal, 'GUconnect': ogr.OFTInteger64 }
    self._InputSUFields = {'OFLD_ID': ogr.OFTInteger64,'OFLD_TO': ogr.OFTString,'OFLD_PSORD': ogr.OFTInteger64,
                           'slope': ogr.OFTReal, 'area': ogr.OFTReal, 'xposition': ogr.OFTReal, 'yposition': ogr.OFTReal, 
                           'flowdist': ogr.OFTReal, 'SCSlanduse': ogr.OFTInteger64, 'SCSsoil': ogr.OFTString,
                           'AWC': ogr.OFTString, 'clay': ogr.OFTString, 'soilbulkd': ogr.OFTString, 
                           'zsoillayer': ogr.OFTString, 'nmanning': ogr.OFTReal, 'Ksat': ogr.OFTString, 
                           'zrootmax': ogr.OFTReal, 'soilcode': ogr.OFTString, 'equipment': ogr.OFTString, 
                           'pRHt_ini': ogr.OFTReal, 'rotation': ogr.OFTString, 'FROM_AP': ogr.OFTString }

    self._OutputAPAttributes = { 'xposition': ogr.OFTReal, 'yposition': ogr.OFTReal }
    self._OutputGUAttributes = { 'xposition': ogr.OFTReal, 'yposition': ogr.OFTReal, 
                                 'area': ogr.OFTReal }
    self._OutputRSAttributes = { 'xposition': ogr.OFTReal, 'yposition': ogr.OFTReal,
                                 'slope': ogr.OFTReal, 'length': ogr.OFTReal, 'width': ogr.OFTReal, 'height': ogr.OFTReal, 
                                 'drainarea': ogr.OFTReal, 'nmanning' : ogr.OFTReal }
    self._OutputREAttributes = { 'xposition': ogr.OFTReal, 'yposition': ogr.OFTReal,
                                 'areamax': ogr.OFTReal, 'inivolume': ogr.OFTReal, 'volumemax': ogr.OFTReal, 
                                 'drainarea': ogr.OFTReal, 'slope': ogr.OFTReal}
    self._OutputSUAttributes = { 'xposition': ogr.OFTReal, 'yposition': ogr.OFTReal,
                                 'slope': ogr.OFTReal, 'area': ogr.OFTReal,
                                 'flowdist': ogr.OFTReal, 'SCSlanduse': ogr.OFTInteger64, 'SCSsoil': ogr.OFTString,
                                 'AWC': ogr.OFTString, 'clay': ogr.OFTString, 'soilbulkd': ogr.OFTString, 
                                 'zsoillayer': ogr.OFTString, 'nmanning': ogr.OFTReal, 'Ksat': ogr.OFTString, 
                                 'zrootmax': ogr.OFTReal, 'soilcode': ogr.OFTString, 'equipment': ogr.OFTString, 
                                 'pRHt_ini': ogr.OFTReal, 'rotation': ogr.OFTString }

    self._RESource = None
    self._RSSource = None
    self._SUSource = None


  ######################################################


  def getExtraArgs(self):
    return self._extraArgs


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
      FoundFields[LayerDefn.GetFieldDefn(i).GetName()] = LayerDefn.GetFieldDefn(i).GetType()

    for k,v in ExpectedFields.items():
      BoogieScape._printActionStarted("Checking field {}".format(k))
      if k in FoundFields:
        if FoundFields[k] == ExpectedFields[k]:
          BoogieScape._printActionDone()
        else:
          BoogieScape._printActionFailed("Failed (wrong type : {} expected, {} found)".format(ExpectedFields[k],FoundFields[k]))
      else:
        BoogieScape._printActionFailed("Failed (not found)")


  ######################################################


  @staticmethod
  def splitUnitsStr(Str):
    Ret = Str.split("#")
    if len(Ret) == 2:
      return Ret

    return None


  ######################################################


  @staticmethod
  def splitUnitsStrList(StrList):
    Ret = list()
    ClassUnitsList = list(filter(None,StrList.split(';')))
    for CUStr in ClassUnitsList:
      Ret.append(BoogieScape.splitUnitsStr(CUStr))

    return Ret


  ######################################################


  @staticmethod
  def _loadShapefile(FilePath,ExpectedFields,UnitsClass):

    BoogieScape._printActionStarted("Opening input {} file".format(UnitsClass))
    Source = BoogieScape._SHPDriver.Open(FilePath, 0) # 0 means read-only. 1 means writeable.
    if Source is None:
      BoogieScape._printActionFailed("Failed (could not open {})".format(FilePath))
    else:
      BoogieScape._printActionDone()

    BoogieScape._checkLayerFieldsTypes(Source,ExpectedFields)

    BoogieScape._printActionStarted("Loading input {} file".format(UnitsClass))

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

      if Unit.Id is None:
        BoogieScape._printActionFailed("Failed (empty OFLD_ID field)")


      UnitsData[Unit.Id] = Unit

    BoogieScape._printActionDone()

    return UnitsData


  ######################################################

  
  @staticmethod
  def _createGISfile(Driver,FilePath):

    BoogieScape._printActionStarted("Creating GIS file {}".format(os.path.basename(FilePath)))
    if os.path.exists(FilePath):
      Driver.DeleteDataSource(FilePath)
    Source = Driver.CreateDataSource(FilePath)

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
      if self._extraArgs["overwrite"]:
        shutil.rmtree(self._outputPath, ignore_errors=True)
      else:
        BoogieScape._printActionFailed(Text="Failed (directory already exists)",Fatal=1)
    os.makedirs(self._outputPath)
    BoogieScape._printActionDone()

    ## Opening RS file
    self._RSData = BoogieScape._loadShapefile(self.getInputPath(self._RSFileShp),self._InputRSFields,"RS")

    ## Opening SU file
    self._SUData = BoogieScape._loadShapefile(self.getInputPath(self._SUFileShp),self._InputSUFields,"SU")

    ## Opening RE file
    self._REData = BoogieScape._loadShapefile(self.getInputPath(self._REFileShp),self._InputREFields,"RE")


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
          Unit.Attributes['xposition'] = Unit.Geometry.GetX()
          Unit.Attributes['yposition'] = Unit.Geometry.GetY()
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

    BoogieScape._printActionStarted("Adding RS to GU graph view")
    for k,RSUnit in self._RSData.items():
      G.add_node("RS#{}".format(RSUnit.Id),data=RSUnit)
    BoogieScape._printActionDone("done")
    
    BoogieScape._printActionStarted("Adding SU to GU graph view")
    for k,SUUnit in self._SUData.items():
      G.add_node("SU#{}".format(SUUnit.Id),data=SUUnit)
    BoogieScape._printActionDone("done")

    BoogieScape._printActionStarted("Adding RE to GU graph view")
    for k,REUnit in self._REData.items():
      G.add_node("RE#{}".format(REUnit.Id),data=REUnit)
    BoogieScape._printActionDone("done")


    BoogieScape._printActionStarted("Building connections in GU graph view")

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

    if self._extraArgs["export_graph_view"] :
      BoogieScape._printActionStarted("Printing GU graph view to file")
      pos = graphviz_layout(G, prog='dot')
      plt.figure(figsize=(20, 20))
      networkx.draw(G, pos, node_size=300, alpha=0.5, node_color="blue", with_labels=True)
      plt.axis('equal')
      plt.savefig(self.getOutputPath("GU_graph_view.pdf"))
      BoogieScape._printActionDone("done")
    

    GUId = 1

    for k,RSUnit in self._RSData.items():
      if int(RSUnit.Attributes["GUconnect"]) > 0:
        UnitStr = "RS#{}".format(RSUnit.Id)
        BoogieScape._printActionStarted("Creating GU#{} from {}".format(GUId,UnitStr))
        
        MultiPolygon = ogr.Geometry(ogr.wkbMultiPolygon)
        Area = 0
        Ancestors = list(networkx.ancestors(G,UnitStr))
        for UpUnit in Ancestors:
          if "area" in G.node[UpUnit]['data'].Attributes:
            Area += G.node[UpUnit]['data'].Attributes['area']
            MultiPolygon.AddGeometry(G.node[UpUnit]['data'].Geometry)
         
        if Area > 0 : 
          Unit = Data.SpatialUnit()
          Unit.Id = GUId
          Unit.PcsOrd = 1
          Unit.To.append(["RS",RSUnit.Id])
          Unit.Attributes["area"] = Area
          Unit.Attributes["xposition"] = MultiPolygon.Centroid().GetX()
          Unit.Attributes["yposition"] = MultiPolygon.Centroid().GetY()
          Unit.Geometry = MultiPolygon
          self._GUData[Unit.Id] = Unit

          for FromUnitStr in Ancestors:
            FromUnit = BoogieScape.splitUnitsStr(FromUnitStr)
            if FromUnit[0] == "SU":
              self._SUData[int(FromUnit[1])].To.append(["GU",Unit.Id])
            elif FromUnit[0] == "RE":
              self._REData[int(FromUnit[1])].To.append(["GU",Unit.Id])

          GUId += 1
          BoogieScape._printActionDone()
        else:
          BoogieScape._printActionDone("ignored")


  ######################################################


  @staticmethod
  def _writeGISfile(Driver,FilePath,GeometryType,AttributesDef,Data):
    
    if not len(Data):
      return

    Source = BoogieScape._createGISfile(Driver,FilePath)

    LayerName = os.path.splitext(os.path.basename(FilePath))[0]
    Layer =  Source.CreateLayer(LayerName,None,GeometryType)
    LayerDefn = Layer.GetLayerDefn()

    FieldDefn = ogr.FieldDefn("OFLD_ID",ogr.OFTInteger)
    Layer.CreateField(FieldDefn)
    FieldDefn = ogr.FieldDefn("OFLD_PSORD",ogr.OFTInteger)
    Layer.CreateField(FieldDefn)
    FieldDefn = ogr.FieldDefn("OFLD_TO",ogr.OFTString)
    Layer.CreateField(FieldDefn)
    FieldDefn = ogr.FieldDefn("OFLD_CHILD",ogr.OFTString)
    Layer.CreateField(FieldDefn)

    for AttrName,Type in AttributesDef.items():
      FieldDefn = ogr.FieldDefn(AttrName,Type)
      Layer.CreateField(FieldDefn)

    for k,Unit in Data.items():
      Feature = ogr.Feature(LayerDefn)

      Feature.SetField("OFLD_ID",Unit.Id)
      Feature.SetField("OFLD_PSORD",Unit.PcsOrd)
      
      UnitsList = list()
      for LinkedUnit in Unit.To:
        UnitsList.append("{}#{}".format(LinkedUnit[0],LinkedUnit[1]))
      Feature.SetField("OFLD_TO",";".join(UnitsList))
      
      UnitsList = list()
      for LinkedUnit in Unit.Child:
        UnitsList.append("{}#{}".format(LinkedUnit[0],LinkedUnit[1]))
      Feature.SetField("OFLD_CHILD",";".join(UnitsList))

      for AttrName,Type in AttributesDef.items():
        Feature.SetField(AttrName,Unit.Attributes[AttrName])

      Feature.SetGeometry(Unit.Geometry)
      Layer.CreateFeature(Feature)
      Feature = None 


  ######################################################


  def _writeFluidXDefinition(self,File,Data,UnitsClass):
    for Id,Unit in Data.items():
      File.write(indentCRStr(3,'<unit class="{}" ID="{}" pcsorder="{}">'.format(UnitsClass,Unit.Id,Unit.PcsOrd)))
      
      for ToUnit in Unit.To:
        File.write(indentCRStr(4,'<to class="{}" ID="{}" />'.format(ToUnit[0],ToUnit[1])))
      for ChildUnit in Unit.Child:
        File.write(indentCRStr(4,'<childof class="{}" ID="{}" />'.format(ChildUnit[0],ChildUnit[1])))
      
      File.write(indentCRStr(3,'</unit>'))


  ######################################################


  def _writeFluidXAttributes(self,File,Data,UnitsClass,ColOrder):
    
    File.write(indentCRStr(2,'<attributes unitsclass="{}" colorder="{}">'.format(UnitsClass,";".join(ColOrder))))
    
    for Id,Unit in Data.items():
      File.write("{} ".format(Unit.Id))

      ValuesList = list()
      for Name in ColOrder:
        ValuesList.append(str(Unit.Attributes[Name]))

      File.write(" ".join(ValuesList))
      File.write("\n")
    
    File.write(indentCRStr(2,'</attributes>'))


  ######################################################


  def _writeFluidXfiles(self):
    BoogieScape._printActionStarted("Creating domain.fluidx file")
   
    FXFile = open(self.getOutputPath(self._DomainFluidXFile),'w')
    FXFile.write(indentCRStr(0,'<?xml version="1.0" standalone="yes"?>'))
    FXFile.write(indentCRStr(0,'<openfluid>'))
    FXFile.write(indentCRStr(1,'<domain>'))

    FXFile.write(indentCRStr(2,'<definition>'))

    self._writeFluidXDefinition(FXFile,self._APData,"AP")
    self._writeFluidXDefinition(FXFile,self._GUData,"GU")
    self._writeFluidXDefinition(FXFile,self._REData,"RE")
    self._writeFluidXDefinition(FXFile,self._RSData,"RS")
    self._writeFluidXDefinition(FXFile,self._SUData,"SU")

    FXFile.write(indentCRStr(2,'</definition>'))

    self._writeFluidXAttributes(FXFile,self._APData,"AP",self._OutputAPAttributes.keys())
    self._writeFluidXAttributes(FXFile,self._GUData,"GU",self._OutputGUAttributes.keys())
    self._writeFluidXAttributes(FXFile,self._REData,"RE",self._OutputREAttributes.keys())
    self._writeFluidXAttributes(FXFile,self._RSData,"RS",self._OutputRSAttributes.keys())
    self._writeFluidXAttributes(FXFile,self._SUData,"SU",self._OutputSUAttributes.keys())

    FXFile.write(indentCRStr(1,'</domain>'))
    FXFile.write(indentCRStr(0,'</openfluid>'))

    FXFile.close()

    BoogieScape._printActionDone()


    BoogieScape._printActionStarted("Creating datastore.fluidx file")

    FXFile = open(self.getOutputPath(self._DatastoreFluidXFile),'w')
 
    FXFile.write(indentCRStr(0,'<?xml version="1.0" standalone="yes"?>'))
    FXFile.write(indentCRStr(0,'<openfluid>'))
    FXFile.write(indentCRStr(1,'<datastore>'))

    FXFile.write(indentCRStr(2,'<dataitem id="AP" type="geovector" source="AP.shp" unitclass="AP" />'))
    FXFile.write(indentCRStr(2,'<dataitem id="GU" type="geovector" source="GU.shp" unitclass="GU" />'))
    FXFile.write(indentCRStr(2,'<dataitem id="RE" type="geovector" source="RE.shp" unitclass="RE" />'))
    FXFile.write(indentCRStr(2,'<dataitem id="RS" type="geovector" source="RS.shp" unitclass="RS" />'))
    FXFile.write(indentCRStr(2,'<dataitem id="SU" type="geovector" source="SU.shp" unitclass="SU" />'))

    FXFile.write(indentCRStr(1,'</datastore>'))
    FXFile.write(indentCRStr(0,'</openfluid>'))

    FXFile.close()


    BoogieScape._printActionDone()



  ######################################################


  def _writeOutputFiles(self):
    BoogieScape._printStage("Writing output GIS files")

    ##### AP
    BoogieScape._writeGISfile(BoogieScape._SHPDriver,self.getOutputPath(self._APFileShp),
                              ogr.wkbPoint,self._OutputAPAttributes,self._APData)
    BoogieScape._writeGISfile(BoogieScape._GeoJSONDriver,self.getOutputPath(self._APFileJson),
                              ogr.wkbPoint,self._OutputAPAttributes,self._APData)
    
    ##### GU
    BoogieScape._writeGISfile(BoogieScape._SHPDriver,self.getOutputPath(self._GUFileShp),
                              ogr.wkbMultiPolygon,self._OutputGUAttributes,self._GUData)
    BoogieScape._writeGISfile(BoogieScape._GeoJSONDriver,self.getOutputPath(self._GUFileJson),
                              ogr.wkbMultiPolygon,self._OutputGUAttributes,self._GUData)

    
    ##### RE
    BoogieScape._writeGISfile(BoogieScape._SHPDriver,self.getOutputPath(self._REFileShp),
                              ogr.wkbPoint,self._OutputREAttributes,self._REData)
    BoogieScape._writeGISfile(BoogieScape._GeoJSONDriver,self.getOutputPath(self._REFileJson),
                              ogr.wkbPoint,self._OutputREAttributes,self._REData)

    ##### RS
    BoogieScape._writeGISfile(BoogieScape._SHPDriver,self.getOutputPath(self._RSFileShp),
                              ogr.wkbMultiLineString,self._OutputRSAttributes,self._RSData)
    BoogieScape._writeGISfile(BoogieScape._GeoJSONDriver,self.getOutputPath(self._RSFileJson),
                              ogr.wkbMultiLineString,self._OutputRSAttributes,self._RSData)

    ##### SU
    BoogieScape._writeGISfile(BoogieScape._SHPDriver,self.getOutputPath(self._SUFileShp),
                              ogr.wkbPolygon,self._OutputSUAttributes,self._SUData)
    BoogieScape._writeGISfile(BoogieScape._GeoJSONDriver,self.getOutputPath(self._SUFileJson),
                              ogr.wkbPolygon,self._OutputSUAttributes,self._SUData)

    
    shutil.copyfile(os.path.join(BoogieScape._ResourcesDir,"outputs.qgs"), self.getOutputPath("outputs.qgs"))


    BoogieScape._printStage("Writing output FluidX files")
    self._writeFluidXfiles()


######################################################


  def _cleanup(self):
    BoogieScape._printStage("Cleanup")

    BoogieScape._printActionStarted("Converting RE slope values")
    for Key in self._REData.keys():
      self._REData[Key].Attributes['slope'] = self._REData[Key].Attributes['slope'] / 100
    BoogieScape._printActionDone()

    BoogieScape._printActionStarted("Converting RS slope values")
    for Key in self._RSData.keys():
      self._RSData[Key].Attributes['slope'] = self._RSData[Key].Attributes['slope'] / 100
    BoogieScape._printActionDone()

    BoogieScape._printActionStarted("Converting SU slope values")
    for Key in self._SUData.keys():
      self._SUData[Key].Attributes['slope'] = self._SUData[Key].Attributes['slope'] / 100
    BoogieScape._printActionDone()


  ######################################################


  def run(self):
    self._prepare()
    self._createAP()
    self._createGU()
    self._cleanup()
    self._writeOutputFiles()
