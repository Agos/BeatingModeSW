#!/usr/bin/python
# -*- coding: utf-8 -*-

from numpy import *
import pylab
import matplotlib
from matplotlib.colors import LinearSegmentedColormap
from beatingmode import BeatingImageRow, BeatingImage

my_color_map = LinearSegmentedColormap("stdGreen",
                {
                'red': [(0.0, 0.0, 0.0),
                       (1.0, 0.0, 0.0)],
               'green': [(0.0, 0.0, 0.0),
                         (1.0, 1.0, 1.0)],
               'blue': [(0.0, 0.0, 0.0),
                        (1.0, 0.0, 0.0)],
                })

ratio_color_map = matplotlib.cm.jet
ratio_color_map.set_bad('k',1.)

beatingimage = BeatingImage(path="dati/generated.dat")
# beatingimage = BeatingImage(path="dati/samp6.dat")

print("Immagine ricostruita: {0}".format(beatingimage.reconstructed_on.shape))

savetxt("out/reconstructed_on.dat", beatingimage.reconstructed_on, fmt="%3.4f0")
savetxt("out/reconstructed_off.dat", beatingimage.reconstructed_off, fmt="%3.4f0")
savetxt("out/enhancement_ratios.dat", beatingimage.ratios, fmt="%3.4f0")

pylab.subplot(2,2,1)
reconstructed_on_image = pylab.imshow(beatingimage.reconstructed_on, cmap=my_color_map)
reconstructed_on_image.set_interpolation('nearest')

pylab.subplot(2,2,2)
reconstructed_off_image = pylab.imshow(beatingimage.reconstructed_off, cmap=my_color_map)
reconstructed_off_image.set_interpolation('nearest')

pylab.subplot(2,2,3)
enhancement_ratios_image = pylab.imshow(beatingimage.ratios, cmap=ratio_color_map)
pylab.colorbar()
enhancement_ratios_image.set_interpolation('nearest')

pylab.show()
