from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List
import io
import numpy as np
import sys
from model import Prediction
from Palette import palettedImage
import json
from PIL import Image

app = FastAPI()

@app.get('/')
def root_route():
  return { 'error': 'Use POST /prediction instead of the root route!' }

@app.post('/prediction/', response_model=Prediction)
async def prediction_route(file: UploadFile = File(...)):

  if file.content_type.startswith('image/') is False:
    raise HTTPException(status_code=400, detail=f'File \'{file.filename}\' is not an image.')

  try:
    contents = await file.read()
    pil_image = Image.open(io.BytesIO(contents))
    if pil_image.mode == 'RGBA':
      pil_image = pil_image.convert('RGB')
    pim = palettedImage(pil_image,file.filename)
    pim.palettize()
    #pim.save_paletted()
    data = pim.get_params()
    return {
      'filename'   : file.filename,
      'contenttype': file.content_type,
      'prediction' : data
    }
  except:
    e = sys.exc_info()[1]
    raise HTTPException(status_code=500, detail=str(e))