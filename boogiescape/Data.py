#! /usr/bin/env python3
# -*- coding: utf-8 -*-


__license__ = "GPLv3"
__author__ = "Jean-Christophe Fabre <jean-christophe.fabre@inra.fr>"
__email__ = "jean-christophe.fabre@inra.fr"


######################################################
######################################################


class SpatialUnit():

  def __init__(self):
    self.Id = None

    self.PcsOrd = None
    self.To = list()
    self.Child = list()

    self.Attributes = dict()

    self.Geometry = None