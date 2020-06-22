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
import astropy.units as u
import numpy as np

def tofits(path=None):
    f = open(path, 'r')
    lines = f.readlines()[0:3]
    f.close()


    cols = lines[1].replace("VARIABLES=","").replace("\"","").replace(" ","").replace('\n','').split(',')
    data_file = np.loadtxt(path, skiprows=3)
    freqs_str = cols[4:]
    freqs = []
    print ("Conversion starting....")
    for freq in freqs_str:
        try:
            freq = freq.replace('f=','')
            quantity = float(freq.split('_')[0])
            unit = u.Unit(freq.split('_')[1])
            freqs.append(quantity * unit)
        except Exception as e:
            print ("Error reading data... (freq %s)" % freq)
            freqs.append(0 * u.Unit('GHz'))

    for idf, freq in enumerate(freqs):
        print ("\rProcessing %s freq...     " % freq, end='')
        hdu = fits.PrimaryHDU()
        hdu.header['SIMPLE'] = True
        hdu.header['BITPIX'] = -32
        hdu.header['NAXIS'] = 2
        fields = lines[2].split(',')
        hdu.header['NAXIS1'] = int(fields[1].replace('I=',''))
        hdu.header['NAXIS2'] = int(fields[2].replace('J=',''))
        hdu.header['EXTEND'] = True
        hdu.header['CRVAL1'] = np.min(data_file[:,2])
        hdu.header['CRVAL2'] = np.min(data_file[:,3])
        hdu.header['CDELT1'] = np.abs(data_file[0,2] - data_file[1,2])
        hdu.header['CDELT2'] = np.abs(data_file[0,3] - data_file[1,3])
        hdu.header['CRPIX1'] = 0.
        hdu.header['CRPIX2'] = 0.
        hdu.header['CTYPE1'] = 'GLON-CAR'
        hdu.header['CTYPE2'] = 'GLAT-CAR'
        hdu.header['RADESYS'] = 'ICRS'
        hdu.header['BUNIT'] = 'K'
        hdu.header['AUTHOR'] ='Conversor from tecplot2fits by d.diaz@irya.unam.mx'
        hdu.header['COMMENTS'] = 'F=%s' % freq

        data = np.zeros((hdu.header['NAXIS2'], hdu.header['NAXIS1']), np.float32)
        for x in range(hdu.header['NAXIS1']):
            for y in range(hdu.header['NAXIS2']):
                row =  data_file[np.where((data_file[:,0] == x+1) & (data_file[:,1] == y+1))]
                value = row[0][idf+4]
                data[y,x] = value


        hdu.data = data
        filepath = path.replace('.dat', '_%s.fits' % (str(freq).replace('.','_'))).replace(' ','')
        hdu.writeto(filepath, overwrite=True)

    print ("\nConversion finished")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert .dat tecplot files to standar .fits files")
    parser.add_argument('path', nargs='+')
    args = parser.parse_args()
    for path in args.path:
        tofits(path)
