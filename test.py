from Palette import palettedImage
import numpy as np
from model import Prediction
import time
start  = time.time()
pim = palettedImage("90.jpg", clusters=6, colorOffset=3)
pim.palettize()
pim.save_paletted()
data = pim.get_params()
print(time.time() - start)
pim.draw_points()
pim.save_quantized()
