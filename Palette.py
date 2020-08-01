import cv2
import numpy as np
from sklearn.cluster import KMeans
from  PIL import Image
import os
import json
from scipy.cluster.vq import kmeans,vq
from matplotlib import pyplot as plt
def image_resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]
    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))
    resized = cv2.resize(image, dim, interpolation=inter)
    return resized
class palettedImage(object):
    def __init__(self, imgSource, imgPath = 'test.jpg', clusters = 5, colorOffset = 5, regime = 0):
        self.imgSource = imgSource
        if isinstance(imgSource, str):
            self.imgPath = imgSource
            if not os.path.exists(self.imgSource):
                print("No Image found")
                return None
        self.clusters = clusters
        self.barPil = None
        self.barImage = None
        self.barredImage = None
        self.regime = regime
        self.colorOffset = colorOffset
        self.bar = None
        self.outBarPath = imgPath.replace(imgPath.split("/")[-1], "BAR_"+imgPath.split("/")[-1])
        self.outImgPath = imgPath.replace(imgPath.split("/")[-1], "paletted_"+imgPath.split("/")[-1])
    @staticmethod
    def plot_colors_rel(hist, centroids, offset):
        # initialize the bar chart representing the relative frequency
        # of each of the colors
        bar = np.zeros((50, 300, 3), dtype="uint8")
        startX = 0
        prs = list(zip(hist, centroids))
        prs = sorted(prs, key=lambda x: x[0])
        #centroids = sorted(centroids, key=lambda x: sum(x))
        # loop over the percentage of each cluster and the color of
        # each cluster
        for (percent, color) in prs:
            # plot the relative percentage of each cluster
            endX = startX + (percent * 300)
            cv2.rectangle(bar, (int(startX), 0), (int(endX), 50),
                          color.astype("uint8").tolist(), -1)
            startX = endX

        # return the bar chart
        return bar

    @staticmethod
    def plot_colors_abs(hist, centroids, offset, clusters, margin):
        # initialize the bar chart representing the relative frequency
        # of each of the colors
        bar = np.zeros((50, 300, 3), dtype="uint8")
        startX = 0

        # Sort the centroids to form a gradient color look
        # centroids = sorted(centroids, key=lambda x: sum(x))
        prs = list(zip(hist, centroids))
        prs = sorted(prs, key=lambda x: x[0])
        rez = []
        rez.extend(prs[:(len(centroids)-offset)//2])
        rez.extend(prs[(len(centroids) - offset)// 2:])
        # loop over the percentage of each cluster and the color of
        # each cluster
        for (percent, color) in rez:
            # plot the relative percentage of each cluster
            # endX = startX + (percent * 300)
            # Instead of plotting the relative percentage,
            # we will make a n=clusters number of color rectangles
            # we will also seperate them by a margin
            new_length = 300 - margin * (clusters - 1)
            endX = startX + new_length / clusters
            cv2.rectangle(bar, (int(startX), 0), (int(endX), 50),
                          color.astype("uint8").tolist(), -1)
            cv2.rectangle(bar, (int(endX), 0), (int(endX + margin), 50),
                          (255, 255, 255), -1)
            startX = endX + margin

        # return the bar chart
        return bar

    @staticmethod
    def centroid_histogram(clt):
        # grab the number of different clusters and create a histogram
        # based on the number of pixels assigned to each cluster
        numLabels = np.arange(0, len(np.unique(clt.labels_)) + 1)
        (hist, _) = np.histogram(clt.labels_, bins=numLabels)
        # normalize the histogram, such that it sums to one
        hist = hist.astype("float")
        hist /= hist.sum()
        # return the histogram
        return hist


    def palettize(self):
        regime = self.regime
        if isinstance(self.imgSource, str):
            image = cv2.imread(self.imgPath)
            image= cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image = np.array(self.imgSource)
            image = image.copy()
        image_copy = image_resize(image, width=400)
        self.image = image_copy
        pixelImage = image_copy.reshape(
            (image_copy.shape[0] * image_copy.shape[1], 3))
        self.pixelImage = pixelImage
        clt = KMeans(n_clusters=self.clusters + (self.colorOffset if regime == 1 else 0 ))
        clt.fit(pixelImage)
        hist = self.centroid_histogram(clt)
        self.centroids = clt.cluster_centers_
        self.hist = hist
        self.outData = sorted(list(zip(self.centroids, self.hist)), key = lambda x: x[1])
        if regime == 0:
            print("Using relative palette colors scaling")
            self.bar = self.plot_colors_rel(hist, clt.cluster_centers_, self.colorOffset)
        elif regime == 1:
            print("Using absolute palette colors scaling")
            self.bar = self.plot_colors_abs(hist, clt.cluster_centers_, self.colorOffset, self.clusters, 5)
        else:
            raise ValueError("No such regime")
        self.barImage = image_resize(
            self.bar,
            width=int(image.shape[1]))
        self.barPil = Image.fromarray(self.barImage)
        newImg = np.concatenate([image, self.barImage], axis=0)
        self.barredImage = Image.fromarray(newImg)
    def show_paletted(self):
        if self.barredImage is not None:
            self.barredImage.show()


    def show_bar(self):
        if self.barPil is not None:
            self.barPil.show()

    def save_bar(self):
        if self.barPil is not None:
            self.barPil.save(self.outBarPath)
            return self.outBarPath

    def save_paletted(self):
        if self.barredImage is not None:
            self.barredImage.save(self.outImgPath)
            return self.outImgPath
    @staticmethod
    def create_data_dict(data):
        d = [(i[0][0], i[0][1], i[0][2]) for i in data]
        return d
    def get_params(self):
        return self.create_data_dict(self.outData)



