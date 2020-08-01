from Palette import palettedImage
import numpy as np
from model import Prediction
pim = palettedImage("hall.jpg")
pim.palettize()
pim.save_paletted()
data = pim.get_params()
print(type(data))
print(Prediction(prediction = data, filename = "1", contenttype = "123").prediction)