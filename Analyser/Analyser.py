from lightkurve import search_targetpixelfile
from lightkurve import TessTargetPixelFile
import matplotlib.pyplot as plt
import numpy as np
import lightkurve as lk
from urllib.request import urlopen
from io import BytesIO
from zipfile import ZipFile
import os
from fnmatch import fnmatch

class Analyser: 
    def __init__(self, objectID:str, dataExists:bool=False, dataPath:str=None ):
        # Creating the necessary folders
        if not os.path.exists('./media/'+self.objectID):
            os.makedirs('./media/'+self.objectID)
        if not os.path.exists('./data/'):
            os.makedirs('./data/')
        self.objectID = objectID
        self.dataExists = dataExists
        self.dataPath = self.downloadData(objectID=objectID)
        self.pixelDataOverTime = TessTargetPixelFile(self.dataPath)
        # To be created later
        self.lightCurve = None
        self.flatLightCurve = None
        self.periodogram = None
        self.periodAtMaxPower = None
        self.transitDurationAtMaxPower = None
        self.durationAtMaxPower = None

    def downloadData(self, objectID:str):
        if not self.dataExists:
            print('-->Downloading data for object ID: ' + objectID)
            url = 'https://mast.stsci.edu/api/v0.1/Download/bundle.zip?previews=false&obsid=' + objectID
            http_response = urlopen(url)
            print('-->Data downloaded. Now extracting...')
            zipfile = ZipFile(BytesIO(http_response.read()))
            zipfile.extractall(path='./data/'+objectID+'/')
        else: 
            print('-->Data already exists. Skipping download...')
        root = './data/'+objectID
        pattern = "*s_tp.fits"
        print('-->Searching for light curve file...')
        for path, subdirs, files in os.walk(root):
            for name in files:
                if fnmatch(name, pattern):
                    return os.path.join(path, name)
        raise Exception('Data downloaded but no light curve file found')

    def displayFrame(self, frame:int):
        pixelDataOverTime = TessTargetPixelFile(self.dataPath)
        pixelDataOverTime.plot(frame=frame)
        plt.savefig('./media/'+self.objectID+'/lightplot.png')

    def displayMaskedFrame(self, frame:int):
        pixelDataOverTime = TessTargetPixelFile(self.dataPath)
        pixelDataOverTime.plot(frame=frame, aperture_mask=pixelDataOverTime.pipeline_mask)
        plt.savefig('./media/'+self.objectID+'/lightplotMasked.png')

    def createLightCurve(self, useMask:bool=True, saveImage:bool=True):
        if useMask:
            lc = self.pixelDataOverTime.to_lightcurve(aperture_mask=self.pixelDataOverTime.pipeline_mask)
        else:
            lc = self.pixelDataOverTime.to_lightcurve()
        self.lightCurve = lc
        if saveImage:
            lc.plot()
            plt.savefig('./media/'+self.objectID+'/lightcurve.png')
        return self.lightCurve

    def flattenLightCurve(self, saveImage:bool=True):
        if self.lightCurve is None:
            raise Exception('Light curve not created yet')
        flat_lc = self.lightCurve.flatten()
        self.flatLightCurve = flat_lc
        if saveImage:
            flat_lc.plot()
            plt.savefig('./media/'+self.objectID+'/flatLightCurve.png')
        return flat_lc
    
    def createPeriodogram(self, saveImage:bool=True):
        if self.flatLightCurve is None:
            raise Exception('Flat light curve not created yet')
        pg = self.flatLightCurve.to_periodogram(method="bls")
        self.periodogram = pg
        self.periodAtMaxPower = pg.period_at_max_power
        self.transitDurationAtMaxPower = pg.duration_at_max_power
        self.durationAtMaxPower = pg.duration_at_max_power
        if saveImage:
            pg.plot()
            plt.savefig('./media/'+self.objectID+'/periodogram.png')
        return {
            'periodogram': pg,
            'periodAtMaxPower': pg.period_at_max_power,
            'transitDurationAtMaxPower': pg.duration_at_max_power,
            'durationAtMaxPower': pg.duration_at_max_power
        }
    
    def createFoldedLightCurve(self, saveImage:bool=True):
        if self.flatLightCurve is None:
            raise Exception('Flat light curve not created yet')
        if self.periodAtMaxPower is None:
            raise Exception('Periodogram not created yet')
        if self.durationAtMaxPower is None:
            raise Exception('Duration at max power not created yet')
        foldedLC = self.flatLightCurve.fold(period=self.periodAtMaxPower, epoch_time=self.transitDurationAtMaxPower)
        if saveImage:
            foldedLC.plot()
            plt.savefig('./media/'+self.objectID+'/foldedLightCurve.png')

    def createBasic(self):
        print('-->Creating basic analysis for object ID: ' + self.objectID)
        self.createLightCurve(useMask=True, saveImage=True)
        self.flattenLightCurve(saveImage=True)
        self.createPeriodogram(saveImage=True)
        self.createFoldedLightCurve(saveImage=True)
        print('-->Basic analysis created for object.')
