from lightkurve import search_targetpixelfile
from lightkurve import TessTargetPixelFile
import matplotlib.pyplot as plt
import numpy as np
import lightkurve as lk

# Get the pixel data over time for a given target and plotting it
pixelDataOverTime = search_targetpixelfile('KIC 6922244', author='Kepler', cadence='long', quarter=4).download()
ax = pixelDataOverTime.plot(frame=42)
ax.figure.savefig('./media/lightplot.png')

# Getting the aperture of the star right using a mask
axMasked = pixelDataOverTime.plot(frame=42, aperture_mask=pixelDataOverTime.pipeline_mask)
axMasked.figure.savefig('./media/lightplotMasked.png')

# Masking all the frames and creating a light curve
lc = pixelDataOverTime.to_lightcurve(aperture_mask=pixelDataOverTime.pipeline_mask)
lc.plot()
plt.savefig('./media/lightcurve.png')

# There might be other general luminosity trends in the star which we should flatten
flat_lc = lc.flatten()
flat_lc.plot()
plt.savefig('./media/flatlightcurve.png')

# Using a periodogram, we can find any periodicity in the star's luminosity
pg = flat_lc.to_periodogram(method="bls")
prominent_peak = pg.period_at_max_power
transit_time = pg.transit_time_at_max_power
transit_duration = pg.duration_at_max_power
pg.plot()
plt.savefig('./media/periodogram.png')

# We can use the most prominent period to fold the light curve
folded_lc = flat_lc.fold(period=prominent_peak)
folded_lc.plot()
plt.savefig('./media/foldedlightcurve.png')

# Folding the light curve with the transit time
transit_folded_lc = flat_lc.fold(period=prominent_peak, epoch_time=transit_time).scatter()
transit_folded_lc.set_xlim(-2, 2)
transit_folded_lc.plot()
plt.savefig('./media/transitfoldedlightcurve.png')