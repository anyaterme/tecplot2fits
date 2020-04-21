#!/usr/bin/env python
#=========================================================
# Author: Daniel Jacobo Diaz Gonzalez
# Creation Date: 2020 Apr 18
# Last Update: 2020 Apr 18
# Description: tool to covert from tectplot .dat files to
# standar .fits files
# ========================================================
import argparse
import astropy.io.fits as fits
import numpy as np

def tofits(path=None):
    f = open(path, 'r')
    lines = f.readlines()[0:3]
    f.close()


    cols = lines[1].replace("VARIABLES=","").replace("\"","").replace(" ","").replace('\n','').split(',')
    data_file = np.loadtxt(path, skiprows=3)


    hdu = fits.PrimaryHDU()
    hdu.header['SIMPLE'] = True
    hdu.header['BITPIX'] = -32
    hdu.header['NAXIS'] = 3
    fields = lines[2].split(',')
    hdu.header['NAXIS1'] = int(fields[1].replace('I=',''))
    hdu.header['NAXIS2'] = int(fields[2].replace('J=',''))
    hdu.header['NAXIS3'] = len(cols)-4
    hdu.header['EXTEND'] = True
    hdu.header['CRVAL1'] = np.min(data_file[:,3])
    hdu.header['CRVAL2'] = np.min(data_file[:,4])
    hdu.header['CDELT1'] = np.abs(data_file[0,3] - data_file[1,3])
    hdu.header['CDELT2'] = np.abs(data_file[0,4] - data_file[1,4])
    hdu.header['CRPIX1'] = 0
    hdu.header['CRPIX2'] = 0
    hdu.header['CTYPE1'] = 'GLON-CAR'
    hdu.header['CTYPE2'] = 'GLAT-CAR'
    hdu.header['RADESYS'] = 'ICRS'
    hdu.header['BUNIT'] = 'K'
    hdu.header['AUTHOR'] ='Conversor from tecplot2fits by d.diaz@irya.unam.mx'
    hdu.header['COMMENTS'] = ','.join(cols[4:])

    data = np.zeros((hdu.header['NAXIS3'], hdu.header['NAXIS2'], hdu.header['NAXIS1']), np.float32)
    for j in range(hdu.header['NAXIS2']):
        row =  data_file[np.where((data_file[:,0] == j+1))]
        values = row[:,- hdu.header['NAXIS3']:]
        for freq in range(hdu.header['NAXIS3']):
            data[freq, j] = values[:,freq]


    hdu.data = data
    hdu.writeto(path.replace('.dat', '.fits'), overwrite=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert .dat tecplot files to standar .fits files")
    parser.add_argument('path', nargs='+')
    args = parser.parse_args()
    for path in args.path:
        tofits(path)
