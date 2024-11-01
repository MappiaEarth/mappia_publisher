from mappia_publisher.test.MockingUtils import overwriteProcessingFeedback
from qgis.core import QgsApplication, QgsVectorLayer, QgsProject, QgsProcessingFeedback, QgsProcessingContext
import os

class SingletonMeta(type):
    _instance = None
    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance

class QgisHelper():
    __metaclass__ = SingletonMeta
    qgis = None

    def __init__(self, qgisBin=None):
        if qgisBin is None:
            qgisBin = os.getenv('OSGEO', "C:\\Program Files\\QGIS 3.14\\bin\\qgis-bin.exe")
        QgsApplication.setPrefixPath(qgisBin, True)
        qgis = QgsApplication([], False)
        qgis.initQgis()
        QgisHelper.qgis = qgis

    @staticmethod
    def getQgis():
        return QgisHelper.qgis

    @staticmethod
    def add_shapefile_layer(file_path, layer_name):
        # Create a vector layer from the shapefile
        layer = QgsVectorLayer(file_path, layer_name, "ogr")

        # Check if the layer was loaded successfully
        if not layer.isValid():
            print(f"Failed to load layer: {file_path}")
            return None

        # Add the layer to the current project
        QgsProject.instance().addMapLayer(layer)
        print(f"Layer '{layer_name}' added successfully.")
        return layer

    @staticmethod
    def initQgisRelatedVariables():
        qgs = QgisHelper.getQgis()
        feedback = overwriteProcessingFeedback(QgsProcessingFeedback())
        context = QgsProcessingContext()
        return (qgs, feedback, context)
