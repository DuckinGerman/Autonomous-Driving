import numpy as np


class Calibration:

    def __init__(self, translation, rotation, intrinsic=None):
        self.translation = np.array(translation)
        self.rotation = np.array(rotation)

        if intrinsic is None:
            self.intrinsic = None
        else:
            self.intrinsic = np.array(intrinsic)

    def __str__(self):

        return (
            f"Translation:\n{self.translation}\n\n"
            f"Rotation:\n{self.rotation}\n\n"
            f"Intrinsic:\n{self.intrinsic}"
        )