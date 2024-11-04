import os
import json
import os
from pathlib import Path

try:
    from qgis.PyQt.QtCore import QCoreApplication, QSize, Qt, QVariant
    from qgis.PyQt.QtGui import QImage, QPainter, QColor
    from qgis.core import (QgsProject,
                           QgsPointXY,
                           QgsLogger,
                           QgsField,
                           QgsProcessing,
                           QgsMessageLog,
                           QgsRectangle,
                           QgsMapSettings,
                           QgsRasterLayer,
                           QgsCoordinateTransform,
                           QgsRenderContext,
                           QgsMapRendererParallelJob,
                           QgsVectorFileWriter,
                           QgsVectorLayer,
                           QgsWkbTypes,
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
except:
    print("Error importing libraries")
    pass

try:
    from .UTILS import UTILS
except:
    print("Not in Dinamica Code")
    pass  # Not in Dinamica Code


try:
    from WMSCapabilities import WMSCapabilities
except:
    print("Not in Dinamica Code")
    pass  # Not in Dinamica Code

try:
    from .WMSCapabilities import WMSCapabilities
except:
    print("Not in Dinamica Code")
    pass  # Not in Dinamica Code


class DirectoryWriter:
    format = 'PNG'
    quality = -1

    def __init__(self, folder, is_tms):
        self.folder = folder
        self.is_tms = is_tms

    def getPathForMap(self, mapTitle='', mapAttr='', operation=''):
        mapAttr = UTILS.normalizeName(mapAttr)
        mapTitle = UTILS.normalizeName(mapTitle)
        operation = UTILS.normalizeName(operation.lower())
        path = os.path.join(self.folder, mapTitle)
        if len(mapAttr) > 0:
            path = os.path.join(path, mapAttr)
        if len(operation) > 0:
            path = os.path.join(path, operation)
        return path

    def processPointsLayer(self, feedback, layer, mapAttr, resultProj):
        feedback.setProgressText("Publishing map: " + UTILS.normalizeName(layer.name()))
        clonedLayer = layer.clone()
        layerRenderer = clonedLayer.renderer()
        renderContext = QgsRenderContext()
        renderContext.setUseAdvancedEffects(True)
        # renderContext.setFlags(QgsRenderContext.Flag.Antialiasing)
        imageList = list()
        iconField = QgsField('icon_url', QVariant.String, 'text') #Danilo não vou verificar se o mapa ja tem esse atributo
        feedback.setProgressText("Adding a column 'icon_url'")
        clonedLayer.startEditing()
        def removeIconUrlField():
            fields = clonedLayer.fields()
            foundInd = -1
            for i in range(len(fields)):
                if fields.at(i).name() == 'icon_url':
                    foundInd = i
                    break
            if foundInd != -1:
                clonedLayer.dataProvider().deleteAttributes([foundInd])
                clonedLayer.updateFields()
        removeIconUrlField()
        addedField = clonedLayer.addAttribute(iconField)
        clonedLayer.updateFields()
        if (addedField == False):
            feedback.pushConsoleInfo("Warning: " + layer.name() + " canceled failed to create a column to store the point symbol.")
            return False
        clonedLayer.commitChanges()
        clonedLayer.startEditing()
        feedback.setProgressText("Rendering symbologies")
        for feature in clonedLayer.getFeatures():
            layerRenderer.startRender(renderContext, clonedLayer.fields())
            symbol = layerRenderer.originalSymbolsForFeature(feature, renderContext)
            if len(symbol) <= 0:
                continue
            else:
                if len(symbol) > 1:
                    feedback.pushConsoleInfo("Warning: Only one symbol for symbology, the others will be ignored.")
                symbol = symbol[0]
            layerRenderer.stopRender(renderContext)
            curImage = symbol.asImage(QSize(24, 24))
            try:
                imgIndex = imageList.index(curImage)
            except Exception as e:
                imageList.append(curImage)
                imgIndex = len(imageList) - 1
            feature.setAttribute("icon_url", './' + str(imgIndex) + ".png")
            clonedLayer.updateFeature(feature)
        clonedLayer.commitChanges()

        layerCsvFolder = self.getPathForMap(layer.name(), mapAttr, 'csv') #TODO check if all map path names are ok.
        feedback.setProgressText("Saving results")
        os.makedirs(layerCsvFolder, exist_ok=True)
        savedCsv = QgsVectorFileWriter.writeAsVectorFormat(clonedLayer, os.path.join(layerCsvFolder, 'point_layer.csv'),
                                                'utf-8', resultProj, 'CSV', layerOptions=['GEOMETRY=AS_XY'])
        #Saving symbology
        for index in range(len(imageList)):
            imageList[index].save(os.path.join(layerCsvFolder, str(index) + '.png'))
        return savedCsv and len(imageList) > 0

    def write_tile(self, tile, image, operation, layerTitle, layerAttr):
        layerAttr = UTILS.normalizeName(layerAttr)
        layerTitle = UTILS.normalizeName(layerTitle)
        directory = os.path.join(self.getPathForMap(layerTitle, layerAttr.lower(), operation), str(tile.z))
        os.makedirs(directory, exist_ok=True)
        xtile = '{0:04d}'.format(tile.x)
        ytile = '{0:04d}'.format(tile.y)
        filename = xtile + "_" + ytile + "." + self.format.lower()
        path = os.path.join(directory, filename)
        image.save(path, self.format, self.quality)
        return path

    def write_custom_capabilities(self, layerTitle, layerAttr, operation):
        WMSCapabilities.updateCustomXML(self.folder, layerTitle, layerAttr, operation)

    def write_capabilities(self, layer, layerTitle, layerAttr, max_zoom, downloadLink):
        WMSCapabilities.updateXMLQGIS(self.folder, layer, layerTitle, layerAttr, max_zoom, downloadLink)

    def setCapabilitiesDefaultMaxZoom(self):
        WMSCapabilities.setCapabilitiesDefaultMaxZoom(self.folder)

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
        dpm = round(renderSettings.outputDpi() / 25.4 * 1000)
        image.setDotsPerMeterX(dpm)
        image.setDotsPerMeterY(dpm)
        painter = QPainter(image)
        job = QgsMapRendererCustomPainterJob(renderSettings, painter)
        job.renderSynchronously()
        painter.end()
        legendFolder = self.getPathForMap(mapTitle, mapAttr, operation)
        os.makedirs(legendFolder, exist_ok=True)
        image.save(os.path.join(legendFolder, 'thumbnail.png'), self.format, self.quality)

    def writeLegendPng(self, layer, mapTitle, mapAttr, operation):
        mapTitle = UTILS.normalizeName(mapTitle)
        mapAttr = UTILS.normalizeName(mapAttr)
        legendFolder = self.getPathForMap(mapTitle, mapAttr, operation)

        # e.g. vlayer = iface.activeLayer()
        options = QgsMapSettings()
        options.setLayers([layer])
        options.setBackgroundColor(QColor(255, 128, 255))
        options.setOutputSize(QSize(60, 60))
        options.setExtent(layer.extent())
        qgisRenderJob = QgsMapRendererParallelJob(options)
        def savePng():
            img = qgisRenderJob.renderedImage()
            # save the image; e.g. img.save("/Users/myuser/render.png","png")
            img.save(os.path.join(legendFolder, "legend.png"), "png")
        qgisRenderJob.finished.connect(savePng)
        qgisRenderJob.start()

    @staticmethod
    def writeLegendJson(legendPath, layer, mapTitle, mapAttr, operation):
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
        jsonFile = Path(os.path.join(legendPath, "legend.json"))
        jsonFile.write_text(json.dumps(result), encoding="utf-8")

    def close(self):
        pass
