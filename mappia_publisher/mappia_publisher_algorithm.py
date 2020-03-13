# -*- coding: utf-8 -*-

"""
/***************************************************************************
 MappiaPublisher
                                 A QGIS plugin
 Publish your maps easily
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-12-09
        copyright            : (C) 2019 by Danilo/CSR UFMG
        email                : danilo@csr.ufmg.br
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Danilo da Silveira Figueira / CSR UFMG'
__date__ = '2020-01-21'
__copyright__ = '(C) 2020 by Danilo da Silveira Figueira / CSR UFMG'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import math
import os
import csv
import io
import json
from pathlib import Path
import platform
import requests
import webbrowser
from time import sleep
import tempfile
import subprocess
from .WMSCapabilities import WMSCapabilities
from .OptionsCfg import OptionsCfg
from .GitHub import GitHub
from .UTILS import UTILS
from enum import Enum
from qgis.PyQt.QtCore import QCoreApplication, QSize, Qt, QVariant
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.PyQt.QtGui import QImage, QColor, QPainter
from qgis.core import (QgsProject,
                       QgsPointXY,
                       QgsLogger,
                       QgsProcessing,
                       QgsMessageLog,
                       QgsRectangle,
                       QgsMapSettings,
                       QgsRasterLayer,
                       QgsCoordinateTransform,
                       QgsMapRendererParallelJob,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterExtent,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterString,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsLabelingEngineSettings,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterFolderDestination,
                       QgsMapRendererCustomPainterJob,
                       QgsCoordinateReferenceSystem,
                       QgsProcessingParameterMapLayer,
                       QgsProcessingParameterMultipleLayers,
                       QgsProcessingParameterEnum,
                       QgsVectorSimplifyMethod,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)

# TMS functions taken from https://alastaira.wordpress.com/2011/07/06/converting-tms-tile-coordinates-to-googlebingosm-tile-coordinates/ #spellok
def tms(ytile, zoom):
    n = 2.0 ** zoom
    ytile = n - ytile - 1
    return int(ytile)


# Math functions taken from https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames #spellok
def deg2num(lat_deg, lon_deg, zoom):
    QgsMessageLog.logMessage(" e ".join([str(lat_deg), str(lon_deg), str(zoom)]), tag="Processing")
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)


# Math functions taken from https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames #spellok
def num2deg(xtile, ytile, zoom):
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)


# https://stackoverflow.com/questions/377017/test-if-executable-exists-in-python/12611523
def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

# From Tiles XYZ algorithm
class Tile:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def extent(self):
        lat1, lon1 = num2deg(self.x, self.y, self.z)
        lat2, lon2 = num2deg(self.x + 1, self.y + 1, self.z)
        return [lon1, lat2, lon2, lat1]

def get_metatiles(extent, zoom, size=4):
    #west_edge, south_edge, east_edge, north_edge = extent
    #[extent.xMinimum(), extent.yMinimum(), extent.xMaximum(), extent.yMaximum()]
    left_tile, top_tile = deg2num(extent.yMaximum(), extent.xMinimum(), zoom)
    right_tile, bottom_tile = deg2num(extent.yMinimum(), extent.xMaximum(), zoom)

    metatiles = {}
    for i, x in enumerate(range(left_tile, right_tile + 1)):
        for j, y in enumerate(range(top_tile, bottom_tile + 1)):
            meta_key = '{}:{}'.format(int(i / size), int(j / size))
            if meta_key not in metatiles:
                metatiles[meta_key] = MetaTile()
            metatile = metatiles[meta_key]
            metatile.add_tile(i % size, j % size, Tile(x, y, zoom))

    return list(metatiles.values())



# From Tiles XYZ algorithm
class MetaTile:
    def __init__(self):
        # list of tuple(row index, column index, Tile)
        self.tiles = []

    def add_tile(self, row, column, tile):
        self.tiles.append((row, column, tile))

    def rows(self):
        return max([r for r, _, _ in self.tiles]) + 1

    def columns(self):
        return max([c for _, c, _ in self.tiles]) + 1

    def extent(self):
        _, _, first = self.tiles[0]
        _, _, last = self.tiles[-1]
        lat1, lon1 = num2deg(first.x, first.y, first.z)
        lat2, lon2 = num2deg(last.x + 1, last.y + 1, first.z)
        return [lon1, lat2, lon2, lat1]


class DirectoryWriter:
    format = 'PNG'
    quality = 100

    def __init__(self, folder, is_tms):
        self.folder = folder
        self.is_tms = is_tms

    def write_tile(self, tile, image, operation, layerTitle, layerAttr):
        layerAttr = UTILS.normalizeName(layerAttr)
        layerTitle = UTILS.normalizeName(layerTitle)
        directory = os.path.join(self.folder, layerTitle, layerAttr.lower(), operation, str(tile.z))
        os.makedirs(directory, exist_ok=True)
        xtile = '{0:04d}'.format(tile.x)
        ytile = '{0:04d}'.format(tile.y)
        filename = xtile + "_" + ytile + "." + self.format.lower()
        path = os.path.join(directory, filename)
        image.save(path, self.format, self.quality)
        return path

    def write_capabilities(self, layer, layerTitle, layerAttr):#, extents, projection):
        WMSCapabilities.updateXML(self.folder, layer, layerTitle, layerAttr)#, extents, projection)

    def write_description(self, layerTitle, layerAttr, cellTypeName, nullValue, operation):
        layerTitle = UTILS.normalizeName(layerTitle)
        cellTypeName = UTILS.normalizeName(cellTypeName)
        directory = os.path.join(self.folder, layerTitle, layerAttr.lower())
        filecsv = "description.csv"
        csvPath = os.path.join(directory, filecsv)
        jsonPath = os.path.join(directory, "description.json")
        if os.path.isfile(csvPath):
            csvFile = open(csvPath, "r", encoding="utf-8")
        else:
            csvFile = io.StringIO("Key*, cell, null, operation, attr,\n-9999, \"\", -1, \"\", nenhuma, ")

        csv_reader = csv.DictReader(csvFile, delimiter=',')
        line_count = 0
        elements = [cellTypeName, str(nullValue), operation, layerAttr]
        for row in csv_reader:
            curEntry = {
                'cellType': row[' cell'].strip(),
                'nullValue': row[' null'].strip(),
                'operation': row[' operation'].strip(),
                'attribute': row[' attr'].strip()
            }
            if line_count > 0 and curEntry['operation'] != operation and curEntry['attribute'] != layerAttr:
                # Key *, cell, null, operation, attr,
                elements.append(curEntry['cellType'])
                elements.append(curEntry['nullValue'])
                elements.append(curEntry['operation'])
                elements.append(curEntry['attribute'])
            line_count += 1
        with open(jsonPath, "w", encoding="utf-8") as jsonFile:
            jsonFile.write(json.dumps(elements))
        csvFile.close()

    '''
    Desenha o thumbnail na projeção final do projeto.
    '''
    def writeThumbnail(self, mapDestExtent, mapTitle, mapAttr, operation, renderSettings):
        mapTitle = UTILS.normalizeName(mapTitle)
        mapAttr = UTILS.normalizeName(mapAttr)
        renderSettings.setExtent(mapDestExtent)
        size = QSize(180, 180)
        renderSettings.setOutputSize(size)
        image = QImage(size, QImage.Format_ARGB32_Premultiplied)
        image.fill(Qt.transparent)
        dpm = renderSettings.outputDpi() / 25.4 * 1000
        image.setDotsPerMeterX(dpm)
        image.setDotsPerMeterY(dpm)
        painter = QPainter(image)
        job = QgsMapRendererCustomPainterJob(renderSettings, painter)
        job.renderSynchronously()
        painter.end()
        legendFolder = os.path.join(self.folder, mapTitle, mapAttr, operation)
        os.makedirs(legendFolder, exist_ok=True)
        image.save(os.path.join(legendFolder, 'thumbnail.png'), self.format, self.quality)

    def writeLegendPng(self, layer, mapTitle, mapAttr, operation):
        mapTitle = UTILS.normalizeName(mapTitle)
        mapAttr = UTILS.normalizeName(mapAttr)
        legendFolder = os.path.join(self.folder, mapTitle, mapAttr, operation)

        # e.g. vlayer = iface.activeLayer()
        options = QgsMapSettings()
        options.setLayers([layer])
        options.setBackgroundColor(QColor(255, 128, 255))
        options.setOutputSize(QSize(60, 60))
        options.setExtent(layer.extent())
        render = QgsMapRendererParallelJob(options)

        def finished():
            img = render.renderedImage()
            # save the image; e.g. img.save("/Users/myuser/render.png","png")
            img.save(os.path.join(legendFolder, "legend.png"), "png")
            print("saved")
        render.finished.connect(finished)
        render.start()

    def writeLegendJson(self, layer, mapTitle, mapAttr, operation):
        mapTitle = UTILS.normalizeName(mapTitle)
        mapAttr = UTILS.normalizeName(mapAttr)
        result = []
        if isinstance(layer, QgsRasterLayer):
            for simbology in layer.legendSymbologyItems():
                label, color = simbology
                result.append({"color": [color.red(), color.green(), color.blue()], "title": label})
        elif layer.renderer().type() == 'categorizedSymbol':
            for symbology in layer.renderer().categories():
                label = symbology.label()
                color = symbology.symbol().color()
                result.append({"color": [color.red(), color.green(), color.blue()], "title": label})
        elif layer.renderer().type() == 'singleSymbol':
            color = layer.renderer().symbol().color()
            result.append({"color": [color.red(), color.green(), color.blue()], "title": mapTitle})
        elif layer.renderer().type() == 'RuleRenderer':
            for symbology in layer.renderer().legendSymbolItems():
                label = symbology.label()
                color = symbology.symbol().color()
                result.append({"color": [color.red(), color.green(), color.blue()], "title": label})
        jsonFile = Path(os.path.join(self.folder, mapTitle, mapAttr, operation, "legend.json"))
        jsonFile.write_text(json.dumps(result), encoding="utf-8")

    def close(self):
        pass



#Supported Operations
class OperationType(Enum):
    RAW = 0
    INTEGRAL = 1
    AREAINTEGRAL = 2
    MAX = 3
    AVERAGE = 4
    MIN = 5
    AREA = 6
    SUM = 7
    CELLS = 8
    RGBA = 9

    @staticmethod
    def getOptions():
        return [member for member in OperationType.__members__]

    def getName(self):
        return self.name.lower()

    def __str__(self):
        return self.name

def install_git():
    def userConfirmed():
        return QMessageBox.Yes == QMessageBox.question(None, "Git not automatically identified.",
                             "Click 'Yes' to automatically download extract and use the git executable, otherwise please find the executable manually.",
                             defaultButton=QMessageBox.Yes,
                             buttons=(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel))

    if (("Windows" in platform.system() or "CYGWIN_NT" in platform.system()) and userConfirmed()) == False:
        return ''
    def download_file(url, toDir):
        local_filename = os.path.join(toDir, url.split('/')[-1])
        # NOTE the stream=True parameter below
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        # f.flush()
        return local_filename

    tmpDir = tempfile.mkdtemp()
    #with tempfile.TemporaryDirectory() as tmpDir:
    gitUrl = "https://github.com/git-for-windows/git/releases/download/v2.25.1.windows.1/PortableGit-2.25.1-64-bit.7z.exe"
    selfExtractor = download_file(gitUrl, tmpDir)
    portableGit = os.path.join(tmpDir, "portablegit")
    subprocess.check_output([selfExtractor, '-o', portableGit, "-y"])
    return os.path.join(portableGit, 'mingw64', 'bin', 'git.exe')


class MappiaPublisherAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT = 'INPUT'
    LAYERS = 'LAYERS'
    OPERATION = 'OPERATION'
    OUTPUT_DIRECTORY = 'OUTPUT_DIRECTORY'
    ZOOM_MAX = 'ZOOM_MAX'
    EXTENT = 'EXTENT'
    LAYER_ATTRIBUTE = 'LAYER_ATTRIBUTE'

    GITHUB_KEY = 'GITHUB_KEY'
    GITHUB_REPOSITORY = 'GITHUB_REPOSITORY'
    GITHUB_USER = 'GITHUB_USER'
    GITHUB_PASS = 'GITHUB_PASS'
    GIT_EXECUTABLE = 'GIT_EXECUTABLE'
    SAVE_PASSWORD = 'SAVE_PASSWORD'

    # Default size of the WMS tiles.
    WIDTH = 256
    HEIGHT = 256

    found_git = ''


    # def flags(self):
    #     return super().flags() | QgsProcessingAlgorithm.FlagSupportsInPlaceEdits | QgsProcessingAlgorithm.FlagNoThreading

    def initAlgorithm(self, config):

        #super(MappiaPublisherAlgorithm, self).initAlgorithm()
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        options = OptionsCfg.read()


        #self.addParameter(
        #    QgsProcessingParameterEnum(
        #        self.OPERATION,
        #        self.tr('Operation Type'),
        #        options=[self.tr(curOption) for curOption in OperationType.getOptions()],
        #        defaultValue=9
        #    )
        #)


        #TODO Implement layer attribute later.
        # self.addParameter(
        #     QgsProcessingParameterString(
        #         self.LAYER_ATTRIBUTE,
        #         self.tr('Layer style name (Change to different style names only if interested in publishing multiple (layers or attributes) of the same file.)'),
        #         optional=False,
        #         defaultValue=options['attrName']
        #     )
        # )

        self.addParameter(
            QgsProcessingParameterString(
                self.GITHUB_REPOSITORY,
                self.tr('Repository name (or map group name)'),
                optional=False,
                defaultValue=options['gh_repository']
            )
        )

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                self.LAYERS,
                self.tr('Maps to display online'),
                QgsProcessing.TypeMapLayer
            )
        )


        maxZoomParameter = QgsProcessingParameterNumber(
            self.ZOOM_MAX,
            self.tr('Map max Zoom level [1 ~ 13] (lower is faster)'),
            minValue=1,
            maxValue=13,
            defaultValue=options["zoom_max"]
        )
        maxZoomParameter.setFlags(maxZoomParameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(maxZoomParameter)

        gitExeParameter = QgsProcessingParameterString(
            self.GIT_EXECUTABLE,
            self.tr('Git client executable path.'),
            optional=True,
            defaultValue=self.getGitDefault(options)
        )
        gitExeParameter.setFlags(gitExeParameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(gitExeParameter)

        ghUserParameter = QgsProcessingParameterString(
            self.GITHUB_USER,
            self.tr('Github USERNAME (Credentials for https://github.com)'),
            optional=True,
            defaultValue=options['gh_user']
        )
        ghUserParameter.setFlags(ghUserParameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(ghUserParameter)

        ghPassParameter = QgsProcessingParameterString(
            self.GITHUB_PASS,
            self.tr('Github Access Token'),
            optional=True,
            defaultValue=options['gh_pass']
        )
        ghPassParameter.setFlags(ghPassParameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(ghPassParameter)

        outputDirParameter = QgsProcessingParameterFolderDestination(
            self.OUTPUT_DIRECTORY,
            self.tr('Output directory'),
            optional=True,
            defaultValue=options["folder"]
        )
        outputDirParameter.setFlags(outputDirParameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(outputDirParameter)


    def getGitDefault(self, options):
        if options['git_exe'] and os.path.exists(options['git_exe']):
            return options['git_exe']
        elif which("git.exe") is not None:
            return which("git.exe")
        else:
            return ''

    #Create the metatiles to the given layer in given zoom levels
    def createLayerMetatiles(self, projection, layer, minZoom, maxZoom):
        mapExtentReprojected = UTILS.getMapExtent(layer, projection)
        metatiles_by_zoom = {}
        metatilesize = 4
        for zoom in range(minZoom, maxZoom + 1):
            metatiles = get_metatiles(mapExtentReprojected, zoom, metatilesize)
            metatiles_by_zoom[zoom] = metatiles
        return metatiles_by_zoom

    def getTotalTiles(self, wgs_crs, min_zoom, max_zoom, layers):
        total = 0
        for layer in layers:
            metatiles_by_zoom = self.createLayerMetatiles(wgs_crs, layer, min_zoom, max_zoom)
            for zoom in range(min_zoom, max_zoom + 1):
                total = total + len(metatiles_by_zoom[zoom])
        return total
        #sum([len(self.createLayerMetatiles(wgs_crs, layer, min_zoom, max_zoom)) for layer in layers])

    def generate(self, writer, parameters, context, feedback):
        feedback.setProgress(1)
        min_zoom = 0
        max_zoom = self.parameterAsInt(parameters, self.ZOOM_MAX, context)
        outputFormat = QImage.Format_ARGB32
        layerAttr = "1" #TODO self.parameterAsString(parameters, self.LAYER_ATTRIBUTE, context)
        cellType = 'int32'
        nullValue = -128
        ghUser = self.parameterAsString(parameters, self.GITHUB_USER, context)
        ghPassword = self.parameterAsString(parameters, self.GITHUB_PASS, context)
        parameters[self.GITHUB_PASS] = ghPassword
        ghRepository = self.parameterAsString(parameters, self.GITHUB_REPOSITORY, context)
        mapOperation = OperationType.RGBA #OperationType(self.parameterAsEnum(parameters, self.OPERATION, context))
        feedback.setProgressText("Operation: " + str(mapOperation))
        wgs_crs = QgsCoordinateReferenceSystem('EPSG:4326')
        dest_crs = QgsCoordinateReferenceSystem('EPSG:3857')
        layers = self.parameterAsLayerList(parameters, self.LAYERS, context)
        metatilesCount = self.getTotalTiles(wgs_crs, min_zoom, max_zoom, layers)
        progress = 0
        feedback.pushConsoleInfo("OPA 1")
        if self.getGitExe(parameters, context) and not GitHub.isOptionsOk(writer.folder, ghUser, ghRepository, feedback):
            feedback.setProgressText("Error : Invalid repository selected")
            return False
        for layer in layers:
            layerTitle = layer.name()
            feedback.setProgressText("Publishing map: " + layerTitle)
            layerRenderSettings = self.createLayerRenderSettings(layer, dest_crs, outputFormat)
            metatiles_by_zoom = self.createLayerMetatiles(wgs_crs, layer, min_zoom, max_zoom)
            for zoom in range(min_zoom, max_zoom + 1):
                feedback.pushConsoleInfo('Generating tiles for zoom level: %s' % zoom)
                for i, metatile in enumerate(metatiles_by_zoom[zoom]):
                    if feedback.isCanceled():
                        break
                    transformContext = context.transformContext()
                    mapRendered = self.renderMetatile(metatile, dest_crs, outputFormat, layerRenderSettings,
                                                      transformContext, wgs_crs)
                    for r, c, tile in metatile.tiles:
                        tile_img = mapRendered.copy(self.WIDTH * r, self.HEIGHT * c, self.WIDTH, self.HEIGHT)
                        writer.write_tile(tile, tile_img, mapOperation.getName(), layerTitle, layerAttr)
                    progress = progress + 1
                    feedback.setProgress(98 * (progress / metatilesCount))
            writer.writeLegendPng(layer, layerTitle, layerAttr, mapOperation.getName())
            writer.write_description(layerTitle, layerAttr, cellType, nullValue, mapOperation.getName())
            writer.write_capabilities(layer, layerTitle, layerAttr)
            writer.writeLegendJson(layer, layerTitle, layerAttr, mapOperation.getName())
            writer.writeThumbnail(UTILS.getMapExtent(layer, dest_crs), layerTitle, layerAttr, mapOperation.getName(), layerRenderSettings)
        feedback.pushConsoleInfo('Finished map tile generation.')
        createdTag = GitHub.publishTilesToGitHub(writer.folder, ghUser, ghRepository, feedback, ghPassword)
        giturl = GitHub.getGitUrl(ghUser, ghRepository)
        #FIXME Space in the map name will cause errors.
        storeUrl = giturl #+ "@" + createdTag + "/"
        feedback.pushConsoleInfo("All the maps in this repository:\n(Please only use maps with the same zoom level.)\n")
        allLayers = WMSCapabilities.getAllLayers(Path(os.path.join(writer.folder, "getCapabilities.xml")).read_text(), layerAttr)
        feedback.pushConsoleInfo("https://maps.csr.ufmg.br/calculator/?queryid=152&storeurl=" + storeUrl
            + "/&zoomlevels="+str(max_zoom)
            + "&remotemap=" + ",".join(allLayers) + "\n")
        feedback.pushConsoleInfo("Current published Maps:\n")
        generatedMaps = ["GH:" + UTILS.normalizeName(layer.name()) + ";" + layerAttr for layer in layers]
        curMapsUrl = "https://maps.csr.ufmg.br/calculator/?queryid=152&storeurl=" + storeUrl \
                     + "/&zoomlevels=" + str(max_zoom) + "&remotemap=" + ",".join(generatedMaps)
        feedback.setProgressText("Copy the link above in any browser to see your maps online.")
        feedback.setProgressText(curMapsUrl)
        feedback.setProgress(100)
        writer.close()
        webbrowser.open_new(curMapsUrl)
        #QMessageBox.warning(None, "Maps published online", "Congratulations your maps are now available online.\nThe shareable link was generated, and will be shown in your browser.")
        return {"MAPS_URL": curMapsUrl, 'PUBLISHED_MAPS': generatedMaps, 'REPOSITORY_MAPS': allLayers}

    #Return the rendered map (QImage) for the metatile zoom level.
    def renderMetatile(self, metatile, dest_crs, outputFormat, renderSettings, transformContext, sourceCrs):
        wgs_to_dest = QgsCoordinateTransform(sourceCrs, dest_crs, transformContext)
        renderSettings.setExtent(wgs_to_dest.transformBoundingBox(QgsRectangle(*metatile.extent())))
        size = QSize(self.WIDTH * metatile.rows(), self.HEIGHT * metatile.columns())
        renderSettings.setOutputSize(size)
        image = QImage(size, outputFormat)
        image.fill(Qt.transparent)
        dpm = renderSettings.outputDpi() / 25.4 * 1000
        image.setDotsPerMeterX(dpm)
        image.setDotsPerMeterY(dpm)
        painter = QPainter(image)
        job = QgsMapRendererCustomPainterJob(renderSettings, painter)
        job.renderSynchronously()
        painter.end()
        return image

    #Configure the rendering settings for the WMS tiles.
    def createLayerRenderSettings(self, layer, dest_crs, outputFormat):
        settings = QgsMapSettings()
        settings.setFlag(QgsMapSettings.Flag.Antialiasing, on=False)
        settings.setFlag(QgsMapSettings.Flag.UseRenderingOptimization, on=False)
        settings.setFlag(QgsMapSettings.Flag.UseAdvancedEffects, on=False)
        settings.setOutputImageFormat(outputFormat)
        settings.setDestinationCrs(dest_crs)
        # simplifyMethod = QgsVectorSimplifyMethod()
        # simplifyMethod.setSimplifyHints(QgsVectorSimplifyMethod.SimplifyHint.NoSimplification)
        # settings.setSimplifyMethod(simplifyMethod)
        settings.setLayers([layer])
        dpi = 256
        settings.setOutputDpi(dpi)
        canvas_red = QgsProject.instance().readNumEntry('Gui', '/CanvasColorRedPart', 255)[0]
        canvas_green = QgsProject.instance().readNumEntry('Gui', '/CanvasColorGreenPart', 255)[0]
        canvas_blue = QgsProject.instance().readNumEntry('Gui', '/CanvasColorBluePart', 255)[0]
        color = QColor(canvas_red, canvas_green, canvas_blue, 0)
        settings.setBackgroundColor(color)
        labeling_engine_settings = settings.labelingEngineSettings()
        labeling_engine_settings.setFlag(QgsLabelingEngineSettings.UsePartialCandidates, False)
        settings.setLabelingEngineSettings(labeling_engine_settings)
        try:
            layer.resampleFilter().setZoomedInResampler(None)
            layer.resampleFilter().setZoomedOutResampler(None)
            layer.resampleFilter().setOn(False)
        except:
            pass #Is not a raster
        return settings

    def getGitExe(self, parameters, context):
        gitExe = self.parameterAsString(parameters, self.GIT_EXECUTABLE, context)
        if (not gitExe or not os.path.isfile(gitExe)) and (not 'GIT_PYTHON_GIT_EXECUTABLE' in os.environ or not os.path.isfile(os.environ['GIT_PYTHON_GIT_EXECUTABLE'])) and (not self.found_git or os.path.isfile(self.found_git)):
            gitExe = install_git()
            parameters[self.GIT_EXECUTABLE] = gitExe
        return gitExe

    def createRepo(self, parameters, context):
        payload = {
            'name': self.parameterAsString(parameters, self.GITHUB_REPOSITORY, context),
            'description': 'Repository cointaining maps of the mappia publisher.',
            'auto_init': 'true'
        }
        token = self.parameterAsString(parameters, self.GITHUB_PASS, context)
        curUser = self.parameterAsString(parameters, self.GITHUB_USER, context)
        resp = requests.post('https://api.github.com/user/repos', auth=(curUser, token), data=json.dumps(payload))
        if resp.status_code == 201:
            sleep(1)
            return True
        else:
            return False


    def checkParameterValues(self, parameters, context):
        min_zoom = 0
        max_zoom = self.parameterAsInt(parameters, self.ZOOM_MAX, context)
        if max_zoom < min_zoom:
            return False, self.tr('Invalid zoom levels range.')
        if len(self.parameterAsLayerList(parameters, self.LAYERS, context)) <= 0:
            return False, self.tr("Please select one map or more.")
        gitRepository = self.parameterAsString(parameters, self.GITHUB_REPOSITORY, context)
        if ' ' in gitRepository:
            return False, self.tr("Error: Space is not allowed in Repository name (remote folder).")
        return super().checkParameterValues(parameters, context)


    def prepareAlgorithm(self, parameters, context, feedback):
        #project = context.project()
        #visible_layers = [item.layer() for item in project.layerTreeRoot().findLayers() if item.isVisible()]
        #self.layers = [l for l in project.layerTreeRoot().layerOrder() if l in visible_layers]

        state = UTILS.randomString()
        curUser = self.parameterAsString(parameters, self.GITHUB_USER, context)
        if (not curUser):
            curUser = ''
        curPass = self.parameterAsString(parameters, self.GITHUB_PASS, context)
        if curPass is None or (GitHub.testLogin(curUser, curPass) == False and QMessageBox.question(None, "Credentials required", "Invalid credentials, could we open login link for you?") == QMessageBox.Yes):
            webbrowser.open_new(
                'https://github.com/login/oauth/authorize?redirect_uri=https://csr.ufmg.br/imagery/get_key.php&client_id=10b28a388b0e66e87cee&login=' + curUser + '&scope=user%20repo&state=' + state)
            credentials = GitHub.getCredentials(state)
            tryCount = 0
            while not credentials:
                sleep(0.5)
                if tryCount % 10 == 0:
                    feedback.pushConsoleInfo("Waiting user finish the credentials validation in Github.")
                tryCount = tryCount + 1
                credentials = GitHub.getCredentials(state)
            feedback.pushConsoleInfo(json.dumps(credentials))
            parameters[self.GITHUB_PASS] = credentials['token']
            parameters[self.GITHUB_USER] = credentials['user']
            curUser = parameters[self.GITHUB_USER]
            curPass = parameters[self.GITHUB_PASS]
        if GitHub.testLogin(curUser, curPass) == False:
            feedback.pushConsoleInfo("Error: Invalid user or password. Please visit the link https://github.com/login and check your password.")
            return False
        # elif curPass and (GitHub.testLogin(curUser, curPass) == False):
        #     return False, self.tr(
        #         "Error: Invalid user or password. Please visit the link https://github.com/login and check your password.")

        # GitHub.testLogin(user, token)
        #
        #
        # if curUser and '@' in curUser:
        #     return False, self.tr("Please use your username instead of the email address.")
        # curPass = GitHub.getAccessToken(self.parameterAsString(parameters, self.GITHUB_USER, context), self.parameterAsString(parameters, self.GITHUB_PASS, context))
        #
        #
        #     return False, self.tr("Error: Invalid user or password. Please visit the link https://github.com/login and check your password.")

        gitRepository = self.parameterAsString(parameters, self.GITHUB_REPOSITORY, context)
        if not GitHub.existsRepository(curUser, gitRepository) and QMessageBox.Yes != QMessageBox.question(
                None,
                "Repository not found",
                "The repository was not found, want to create a new repository?",
                defaultButton=QMessageBox.Yes,
                buttons=(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)):
            feedback.pushConsoleInfo("Error: A valid repository is needed please enter a valid repository name or create a new one.")
            return False
        elif not GitHub.existsRepository(curUser, gitRepository) and not self.createRepo(parameters, context):
            if QMessageBox.question(
                    None,
                    "The creation have failed. Want to open the link https://github.com/new to create a new repository?",
                    defaultButton=QMessageBox.Yes) == QMessageBox.Yes:
                webbrowser.open_new("https://github.com/new")
            feedback.pushConsoleInfo("Error: Failed to create the repository, please create a one at: https://github.com/new")
            return False
        feedback.pushConsoleInfo("AEW2")
        gitExe = self.getGitExe(parameters, context)
        if not gitExe or not os.path.isfile(gitExe):
            feedback.pushConsoleInfo("Select your git executable program.\n" + str(
                gitExe) + "\nIt can be downloadable at: https://git-scm.com/downloads")
            return False
        if not self.parameterAsString(parameters, self.GITHUB_REPOSITORY, context):
            feedback.pushConsoleInfo("Please specify your repository name.\nYou can create one at: https://github.com/new")
            return False

        feedback.pushConsoleInfo("AEW 3")
        OptionsCfg.write(
            self.parameterAsInt(parameters, self.ZOOM_MAX, context),
            self.getGitExe(parameters, context),
            self.parameterAsString(parameters, self.LAYER_ATTRIBUTE, context),
            self.parameterAsString(parameters, self.GITHUB_USER, context),
            self.parameterAsString(parameters, self.GITHUB_REPOSITORY, context),
            self.parameterAsString(parameters, self.OUTPUT_DIRECTORY, context),
            self.parameterAsString(parameters, self.GITHUB_PASS, context)
        )
        return True

    def processAlgorithm(self, parameters, context, feedback):
        is_tms = False
        output_dir = self.parameterAsString(parameters, self.OUTPUT_DIRECTORY, context)
        if not output_dir:
            raise QgsProcessingException(self.tr('You need to specify output directory.'))
        writer = DirectoryWriter(output_dir, is_tms)
        feedback.pushConsoleInfo("AEW4")
        GitHub.prepareEnvironment(self.getGitExe(parameters, context))
        return self.generate(writer, parameters, context, feedback)

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Share'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Share your maps')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Online mapping'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return MappiaPublisherAlgorithm()