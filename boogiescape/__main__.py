#! /usr/bin/env python3
# -*- coding: utf-8 -*-


__license__ = "GPLv3"
__author__ = "Jean-Christophe Fabre <jean-christophe.fabre@inra.fr>"
__email__ = "jean-christophe.fabre@inra.fr"


######################################################
######################################################


import argparse

from . import BoogieScape


######################################################
######################################################


def main():

  Parser = argparse.ArgumentParser(description="Tool for adjusting spatial representation of agricultural landscapes for OpenFLUID modelling platform")

  Parser.add_argument('INPUTPATH', type=str, nargs=1,help='Input path')
  Parser.add_argument('OUTPUTPATH', type=str, nargs=1,help='Output path')
  Parser.add_argument('--overwrite',action='store_true',help='Overwrite outputs')

  Args = vars(Parser.parse_args())
  #print(Args)

  InPath = Args['INPUTPATH']
  Args.pop('INPUTPATH')
  OutPath = Args['OUTPUTPATH']
  Args.pop('OUTPUTPATH')

  BS = BoogieScape.BoogieScape(InPath,OutPath,Args)
  BS.run()
