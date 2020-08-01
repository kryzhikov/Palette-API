from Palette import palettedImage
import numpy as np
from model import Prediction
pim = palettedImage("90.jpg")
pim.palettize()
pim.save_paletted()
data = pim.get_params()
pim.draw_points()
print(Prediction(prediction = data, filename = "1", contenttype = "123").prediction)