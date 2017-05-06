import cv2

from tests.full_cycle_vision import ICubeDetector


class CascadeCubeDetector(ICubeDetector):
    """Implementation CubeDetector from cascade classifier"""

    def __init__(self, cascade_config):
        self.cascade = cv2.CascadeClassifier()
        if self.cascade.load(cascade_config):
            raise IOError('Config file %s is not valid!', cascade_config)

    def cubes(self, image):
        cubes = self.cascade.detectMultiScale(image)
        return cubes