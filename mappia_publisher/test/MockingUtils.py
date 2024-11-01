from contextlib import contextmanager
from functools import wraps
import types
import os
import inspect
from typing import Dict, Any, List
from mappia_publisher.UTILS import UTILS

from qgis.core import QgsProcessingContext, QgsPointXY, QgsCoordinateReferenceSystem, QgsMapLayer, QgsVectorLayer, QgsRasterLayer

class MockParameters:
    # Define `parameters` as a static class attribute
    parameters: Dict[str, Any] = {}

    @staticmethod
    def parameterAsPoint(self, name: str, context: 'QgsProcessingContext',
                         crs: 'QgsCoordinateReferenceSystem' = None) -> 'QgsPointXY':
        return QgsPointXY(MockParameters.parameters.get(name, None))

    @staticmethod
    def parameterAsString(self, name: str, context: 'QgsProcessingContext') -> str:
        return str(MockParameters.parameters.get(name, ""))

    @staticmethod
    def parameterAsInt(self, name: str, context: 'QgsProcessingContext') -> int:
        return int(MockParameters.parameters.get(name, 0))

    @staticmethod
    def parameterAsFloat(self, name: str, context: 'QgsProcessingContext') -> float:
        return float(MockParameters.parameters.get(name, 0.0))

    @staticmethod
    def parameterAsBool(self, name: str, context: 'QgsProcessingContext') -> bool:
        return bool(MockParameters.parameters.get(name, False))

    @staticmethod
    def parameterAsList(self, name: str, context: 'QgsProcessingContext') -> List[Any]:
        return list(MockParameters.parameters.get(name, []))

    @staticmethod
    def parameterAsDict(self, name: str, context: 'QgsProcessingContext') -> Dict[str, Any]:
        return dict(MockParameters.parameters.get(name, {}))

    @staticmethod
    def parameterAsCoordinateSystem(self, name: str, context: 'QgsProcessingContext') -> 'QgsCoordinateReferenceSystem':
        return MockParameters.parameters.get(name, QgsCoordinateReferenceSystem())

    @staticmethod
    def parameterAsLayerList(self, name: str, context: 'QgsProcessingContext') -> 'QgsMapLayer':
        return [TypeUtils.getShapeFrom(filePath) if filePath.endswith('.shp') else TypeUtils.getRasperFrom(filePath) for filePath in MockParameters.parameters.get(name, '') if os.path.isfile(filePath)]

def setMockingParameters(target, parameters, overwriteParameters={}):
    parameters.update(overwriteParameters)
    MockParameters.parameters = parameters
    # Iterate over each function in the source class
    for name in [attr for attr in dir(MockParameters) if attr.startswith('parameter') and type(getattr(MockParameters, attr)) in [types.MethodType, types.FunctionType]]:
        setattr(target, name, getattr(MockParameters, name))
    return target, parameters


class MockingUtils:
    @staticmethod
    def createMockingFunction(obj, func_name, default_return_value):
        original_func = getattr(obj, func_name)
        @wraps(original_func)
        def new_func(*args, **kwargs):
            return default_return_value
        return new_func

    #Usually need a first parameter to be a placeholder for the instance 'self' parameter.
    @staticmethod
    @contextmanager
    def replaceFunction(obj, function_name, new_func=None):
        # Save the original function to restore it later
        original_func = getattr(obj, function_name)
        # Replace the function with the new one
        setattr(obj, function_name, new_func)
        try:
            yield
        finally:
            # Restore the original function
            setattr(obj, function_name, original_func)

    @staticmethod
    @contextmanager
    def mockFunctionWithReturn(obj, func_name, default_return_value):
        # Get the original function to restore it later
        original_func = getattr(obj, func_name)

        # Define a new function with the same signature but a fixed return value
        @wraps(original_func)
        def new_func(*args, **kwargs):
            return default_return_value

        # Ensure the new function has the same parameter signature
        signature = inspect.signature(original_func)
        new_func.__signature__ = signature

        # Replace the function with the new one
        setattr(obj, func_name, new_func)
        try:
            yield
        finally:
            # Restore the original function
            setattr(obj, func_name, original_func)



class TypeUtils:
    @staticmethod
    def getShapeFrom(filePath):
        return QgsVectorLayer(filePath, UTILS.getBasename(filePath))

    @staticmethod
    def getRasperFrom(filePath):
        return QgsRasterLayer(filePath, UTILS.getBasename(filePath))



class MockingQgsProcessingFeedback:
    @staticmethod
    def pushConsoleInfo(message):
        print('pushConsoleInfo: ' + message)

def overwriteProcessingFeedback(target):
    cReference = MockingQgsProcessingFeedback
    # Iterate over each function in the source class
    for name in [attr for attr in dir(cReference) if type(getattr(cReference, attr)) in [types.MethodType, types.FunctionType]]:
        #setattr(target, name, func.__get__(target, target.__class__))
        setattr(target, name, getattr(cReference, name))
        #target[name]=source[name]
    return target



class MockParameters:
    # Define `parameters` as a static class attribute
    parameters: Dict[str, Any] = {}

    @staticmethod
    def parameterAsPoint(self, name: str, context: 'QgsProcessingContext',
                         crs: 'QgsCoordinateReferenceSystem' = None) -> 'QgsPointXY':
        return QgsPointXY(MockParameters.parameters.get(name, None))

    @staticmethod
    def parameterAsString(self, name: str, context: 'QgsProcessingContext') -> str:
        return str(MockParameters.parameters.get(name, ""))

    @staticmethod
    def parameterAsInt(self, name: str, context: 'QgsProcessingContext') -> int:
        return int(MockParameters.parameters.get(name, 0))

    @staticmethod
    def parameterAsFloat(self, name: str, context: 'QgsProcessingContext') -> float:
        return float(MockParameters.parameters.get(name, 0.0))

    @staticmethod
    def parameterAsBool(self, name: str, context: 'QgsProcessingContext') -> bool:
        return bool(MockParameters.parameters.get(name, False))

    @staticmethod
    def parameterAsList(self, name: str, context: 'QgsProcessingContext') -> List[Any]:
        return list(MockParameters.parameters.get(name, []))

    @staticmethod
    def parameterAsDict(self, name: str, context: 'QgsProcessingContext') -> Dict[str, Any]:
        return dict(MockParameters.parameters.get(name, {}))

    @staticmethod
    def parameterAsCoordinateSystem(self, name: str, context: 'QgsProcessingContext') -> 'QgsCoordinateReferenceSystem':
        return MockParameters.parameters.get(name, QgsCoordinateReferenceSystem())

    @staticmethod
    def parameterAsLayerList(self, name: str, context: 'QgsProcessingContext') -> 'QgsMapLayer':
        return [TypeUtils.getShapeFrom(filePath) if filePath.endswith('.shp') else TypeUtils.getRasperFrom(filePath) for filePath in MockParameters.parameters.get(name, '') if os.path.isfile(filePath)]

def setMockingParameters(target, parameters, overwriteParameters={}):
    parameters.update(overwriteParameters)
    MockParameters.parameters = parameters
    # Iterate over each function in the source class
    for name in [attr for attr in dir(MockParameters) if attr.startswith('parameter') and type(getattr(MockParameters, attr)) in [types.MethodType, types.FunctionType]]:
        setattr(target, name, getattr(MockParameters, name))
    return target, parameters
