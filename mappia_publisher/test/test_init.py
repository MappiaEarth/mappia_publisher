# coding=utf-8

import re
import os
import random
import tempfile
import webbrowser
from concurrent import futures

import requests
import time
import json
import glob
import platform
import subprocess
from http import HTTPStatus
from requests import request
from datetime import datetime
from time import sleep

isDinamica = False
try:
    dinamica.package("os")
    isDinamica = True
except:
    isDinamica = False

try:
    from UTILS import UTILS
    from QMessageBox import QMessageBox
except:
    pass  # Not in Dinamica Code

try:
    from .UTILS import UTILS
    from qgis.PyQt.QtWidgets import QMessageBox
except:
    pass  # Not in QGIS

try:
    from qgis.PyQt.QtGui import QImage, QColor, QPainter
    from qgis.PyQt.QtCore import QCoreApplication, QSize, Qt, QVariant
    from qgis.core import (
                           QgsField,
                           QgsMapSettings,
                           QgsRasterLayer,
                           QgsRenderContext,
                           QgsMapRendererParallelJob,
                           QgsCoordinateReferenceSystem,
                           QgsVectorFileWriter,
                           QgsMapRendererCustomPainterJob)
except:
    pass  # In QGIS


import math
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from qgis.core import QgsApplication, QgsProject, QgsMapLayer, QgsProcessingContext, QgsProcessingFeedback
from mappia_publisher.OperationType import OperationType
from MockingUtils import MockingUtils, TypeUtils, setMockingParameters, MockParameters, overwriteProcessingFeedback


import traceback
import requests
import csv
import re
from datetime import date
import json
from pathlib import Path
import platform
import webbrowser
import tempfile
import subprocess
from mappia_publisher.FeedbackWrapper import FeedbackWrapper
from mappia_publisher.WMSCapabilities import WMSCapabilities
from mappia_publisher.OptionsCfg import OptionsCfg
from mappia_publisher.GitHub import GitHub
from mappia_publisher.UTILS import UTILS
from mappia_publisher.UTILS import UserInterrupted
from mappia_publisher.mappia_publisher_algorithm import MappiaPublisherAlgorithm
from qgis.core import QgsApplication, QgsProject
from mappia_publisher.test.QgisLoaderHelper import QgisHelper
from mappia_publisher.DirectoryWriter import DirectoryWriter


#Depends on some environment variables, configure and run: ..\..\scripts\setEnvironments.bat

def testBigGeneratingLayerTilesAtGivenZoom():
    qgis, feedback, context = QgisHelper().initQgisRelatedVariables()

    with open("default_test_parameters.json", "r") as file:
        parameters = json.load(file)
    mappiaPlugin, parameters = setMockingParameters(MappiaPublisherAlgorithm(), parameters, {'INCLUDE_DOWNLOAD': False})
    is_tms = False
    writer = DirectoryWriter(parameters['OUTPUT_DIRECTORY'], is_tms)
    start_full_time = time.time()  # Record start time
    with MockingUtils.mockFunctionWithReturn(GitHub, 'publishTilesToGitHub', None):
        with MockingUtils.mockFunctionWithReturn(webbrowser, 'open_new', None):
            #mappiaPlugin.findGithubUserName(parameters)
            mappiaPlugin.prepareAlgorithm(parameters, context, feedback)
            mappiaPlugin.generate(writer, parameters, context, feedback)
    elapsed_full_time = time.time() - start_full_time
    minZoom = 0
    maxZoom = mappiaPlugin.parameterAsInt(parameters, mappiaPlugin.ZOOM_MAX, context)
    print(f"Finished generating and drawing tiles between {minZoom} to {maxZoom}: ({elapsed_full_time:.2f} s)")


def testSmallGeneratingLayerTilesAtGivenZoom():
    qgis, feedback, context = QgisHelper().initQgisRelatedVariables()
    mappiaPlugin, parameters = setMockingParameters(MappiaPublisherAlgorithm(), json.load(open("default_test_parameters.json", "r")),
        {'INCLUDE_DOWNLOAD': False})
    is_tms = False
    writer = DirectoryWriter(parameters['OUTPUT_DIRECTORY'], is_tms)
    start_full_time = time.time()  # Record start time
    with MockingUtils.mockFunctionWithReturn(GitHub, 'publishTilesToGitHub', None):
        with MockingUtils.mockFunctionWithReturn(webbrowser, 'open_new', None):
            mappiaPlugin.findGithubUserName(parameters)
            mappiaPlugin.prepareAlgorithm(parameters, context, feedback)
            mappiaPlugin.generate(writer, parameters, context, feedback)
    elapsed_full_time = time.time() - start_full_time
    minZoom = 0
    maxZoom = mappiaPlugin.parameterAsInt(parameters, mappiaPlugin.ZOOM_MAX, context)
    print(f"Finished generating and drawing tiles between {minZoom} to {maxZoom}: ({elapsed_full_time:.2f} s)")

def testSmallMetatileGeneration():
    import time
    parameters = {}
    with open("default_test_parameters.json", "r") as file:
        parameters = json.load(file)

    min_zoom = 0
    max_zoom = 13
    wgs_crs = QgsCoordinateReferenceSystem('EPSG:4326')
    layer = TypeUtils.getShapeFrom(parameters["LAYERS"][0])
    metatilesize = 4
    mapExtentReprojected = UTILS.getMapExtent(layer, wgs_crs)
    start_full_time = time.time()  # Record start time
    for iZoom in range(min_zoom, max_zoom+1):
        start_time = time.time()  # Record start time
        metaTiles = UTILS.get_metatiles(mapExtentReprojected, iZoom, metatilesize)
        end_time = time.time()  # Record end time
        elapsed_time = end_time - start_time  # Calculate elapsed time
        print(f"MetaTiles zoom: {iZoom} QntTiles: {len(metaTiles)}  ({elapsed_time:.2f} s)")
    elapsed_full_time = time.time() - start_full_time
    print(f"Generated the Metatiles Only the MetaTiles between {min_zoom} to {max_zoom}: ({elapsed_full_time:.2f} s)")

def testSmallRenderingMetaTiles():
    import time
    qgis, feedback, context = QgisHelper().initQgisRelatedVariables()
    start_full_time = time.time()  # Record start time
    is_tms = True
    parameters = {}
    with open("default_test_parameters.json", "r") as file:
        parameters = json.load(file)
    writer = DirectoryWriter(parameters['OUTPUT_DIRECTORY'], is_tms)
    WIDTH = 256
    HEIGHT = 256
    layer = TypeUtils.getShapeFrom(parameters["LAYERS"][2])
    layerTitle = layer.name()
    metatilesize = 32 #always a potency of two
    layerAttr = "1"
    wgsCrs = QgsCoordinateReferenceSystem('EPSG:4326')
    destCrs = QgsCoordinateReferenceSystem('EPSG:3857')
    mapOperation = OperationType.RGBA
    outputFormat = QImage.Format_ARGB32
    mapExtentReprojected = UTILS.getMapExtent(layer, wgsCrs)
    zoomLevel = 7
    layerRenderSettings = MappiaPublisherAlgorithm.createLayerRenderSettings(layer, destCrs, outputFormat, feedback)
    transformContext = context.transformContext()
    for metatile in UTILS.get_metatiles(mapExtentReprojected, zoomLevel, metatilesize):
        mapRendered = MappiaPublisherAlgorithm.renderMetatile(metatile, destCrs, layerRenderSettings, transformContext, wgsCrs, WIDTH, HEIGHT)
        for r, c, tile in metatile.tiles:
            tile_img = mapRendered.copy(WIDTH * r, HEIGHT * c, WIDTH, HEIGHT)
            writer.write_tile(tile, tile_img, mapOperation.getName(), layerTitle, layerAttr)
    #TODO must check if generated tiles are correct.
    elapsed_full_time = time.time() - start_full_time
    print(f"Generated the RenderedTiles for zoomLvl {zoomLevel} in ({elapsed_full_time:.2f} s)")

def testBigLayerRenderingAllTiles():
    import time
    qgis, feedback, context = QgisHelper().initQgisRelatedVariables()
    start_full_time = time.time()  # Record start time
    is_tms = True
    parameters = {}
    with open("default_test_parameters.json", "r") as file:
        parameters = json.load(file)
    writer = DirectoryWriter(parameters['OUTPUT_DIRECTORY'], is_tms)
    print("saving to folder: " + writer.folder)
    WIDTH = 256
    HEIGHT = 256
    layer = TypeUtils.getShapeFrom(parameters["LAYERS"][3])
    layerTitle = layer.name()
    metatilesize = 32 #always a potency of two
    layerAttr = "1"
    wgsCrs = QgsCoordinateReferenceSystem('EPSG:4326')
    destCrs = QgsCoordinateReferenceSystem('EPSG:3857')
    mapOperation = OperationType.RGBA
    outputFormat = QImage.Format_ARGB32
    mapExtentReprojected = UTILS.getMapExtent(layer, wgsCrs)
    min_zoom = 0
    maxZoom = 7
    renderedTiles = 0
    with futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        jobs = []
        for zoomLevel in range(min_zoom, maxZoom + 1):
            UTILS.checkForCanceled(feedback)
            feedback.pushConsoleInfo('Generating tiles for zoom level: %s' % zoomLevel)
            for metatile in UTILS.get_metatiles(mapExtentReprojected, zoomLevel, metatilesize):
                if feedback.isCanceled():
                    break
                #self.drawMetatileToFile(mapOperation, layerAttr, layerTitle, metatile, layer, outputFormat, wgs_crs, dest_crs, feedback, context, writer)
                jobs.append(executor.submit(MappiaPublisherAlgorithm.drawMetatileToFile, mapOperation, layerAttr, layerTitle, metatile, layer, outputFormat, wgsCrs, destCrs, feedback, context, writer))
        for completed_job in futures.as_completed(jobs):
            result = completed_job.result()
            renderedTiles = renderedTiles + 1
            print(f"Tile rendered {renderedTiles}")
    # for zoomLevel in range(0, maxZoom + 1):
    #     for metatile in UTILS.get_metatiles(mapExtentReprojected, zoomLevel, metatilesize):
    #         mapRendered = MappiaPublisherAlgorithm.renderMetatile(metatile, destCrs, layerRenderSettings, transformContext, wgsCrs, WIDTH, HEIGHT)
    #         for r, c, tile in metatile.tiles:
    #             tile_img = mapRendered.copy(WIDTH * r, HEIGHT * c, WIDTH, HEIGHT)
    #             writer.write_tile(tile, tile_img, mapOperation.getName(), layerTitle, layerAttr)
    #TODO must check if generated tiles are correct.
    elapsed_full_time = time.time() - start_full_time
    print(f"Generated the RenderedTiles for a BigArea from zoom 0 to {maxZoom} in ({elapsed_full_time:.2f} s)")

def testBigLayerPublishGithub():
    import time
    qgis, feedback, context = QgisHelper().initQgisRelatedVariables()
    mappiaPlugin, parameters = setMockingParameters(MappiaPublisherAlgorithm(), json.load(open("default_test_parameters.json", "r")),
                                                    {'INCLUDE_DOWNLOAD': False})
    start_full_time = time.time()  # Record start time
    is_tms = True
    parameters = {}
    with open("default_test_parameters.json", "r") as file:
        parameters = json.load(file)
    writer = DirectoryWriter(parameters['OUTPUT_DIRECTORY'], is_tms)
    mappiaPlugin.findGithubUserName(parameters)
    GitHub.publishTilesToGitHub(writer.folder, parameters["GITHUB_USER"], parameters["GITHUB_REPOSITORY"], feedback, MappiaPublisherAlgorithm.version, mappiaPlugin.ghPassword)

def testCreatingRepository():
    import time
    qgis, feedback, context = QgisHelper().initQgisRelatedVariables()
    mappiaPlugin, parameters = setMockingParameters(MappiaPublisherAlgorithm(), json.load(open("default_test_parameters.json", "r")),
                                                    {'INCLUDE_DOWNLOAD': False})
    start_full_time = time.time()  # Record start time
    parameters = {}
    with open("default_test_parameters.json", "r") as file:
        parameters = json.load(file)

    ghRepository = mappiaPlugin.parameterAsString(parameters, mappiaPlugin.GITHUB_REPOSITORY, context)
    ghRepository = ghRepository + "_a"
    ghUser = mappiaPlugin.parameterAsString(parameters, mappiaPlugin.GITHUB_USER, context)
    OUTPUT_DIR_TMP = mappiaPlugin.parameterAsString(parameters, mappiaPlugin.OUTPUT_DIRECTORY, context)
    mappiaPlugin.findGithubUserName(parameters)
    GitHub.createRepo(ghRepository, ghUser, mappiaPlugin.ghPassword, OUTPUT_DIR_TMP, feedback)

#testCreatingRepository()
#testSmallMetatileGeneration()
#testSmallRenderingMetaTiles()
#testSmallGeneratingLayerTilesAtGivenZoom()
#testBigGeneratingLayerTilesAtGivenZoom()
#testBigLayerRenderingAllTiles()
#testBigLayerPublishGithub()





# """Tests QGIS plugin init."""
#
# __author__ = 'Tim Sutton <tim@linfiniti.com>'
# __revision__ = '$Format:%H$'
# __date__ = '17/10/2010'
# __license__ = "GPL"
# __copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
# __copyright__ += 'Disaster Reduction'
#
# import os
# import unittest
# import logging
# import configparser
#
# LOGGER = logging.getLogger('QGIS')
#
#
# class TestInit(unittest.TestCase):
#     """Test that the plugin init is usable for QGIS.
#
#     Based heavily on the validator class by Alessandro
#     Passoti available here:
#
#     http://github.com/qgis/qgis-django/blob/master/qgis-app/
#              plugins/validator.py
#
#     """
#
#     def test_read_init(self):
#         """Test that the plugin __init__ will validate on plugins.qgis.org."""
#
#         # You should update this list according to the latest in
#         # https://github.com/qgis/qgis-django/blob/master/qgis-app/
#         #        plugins/validator.py
#
#         required_metadata = [
#             'name',
#             'description',
#             'version',
#             'qgisMinimumVersion',
#             'email',
#             'author']
#
#         file_path = os.path.abspath(os.path.join(
#             os.path.dirname(__file__), os.pardir,
#             'metadata.txt'))
#         LOGGER.info(file_path)
#         metadata = []
#         parser = configparser.ConfigParser()
#         parser.optionxform = str
#         parser.read(file_path)
#         message = 'Cannot find a section named "general" in %s' % file_path
#         assert parser.has_section('general'), message
#         metadata.extend(parser.items('general'))
#
#         for expectation in required_metadata:
#             message = ('Cannot find metadata "%s" in metadata source (%s).' % (
#                 expectation, file_path))
#
#             self.assertIn(expectation, dict(metadata), message)
#
# if __name__ == '__main__':
#     unittest.main()
