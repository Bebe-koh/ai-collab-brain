# IMAGING SCRIPT
# Run this script after a full-polarization calibration
# This script has been generated automatically from: 
#
#    scriptForCalibrationAPP_C4.py
###########################################################




for field in ['Sagittarius_A_star','J1924-2914','Ganymede','QSO B1921-293','J1312-0424','J1744-3116','QSO B1730-130','J1650-2943']:
  for spi in range(4):
    os.system('rm -rf %s.APP.spw%i.*'%(field,spi))
    clean(vis= ['uid___A002_Xbec3cb_X3d77.polcalibrated.APP.ms','uid___A002_Xbec3cb_X3fe6.polcalibrated.APP.ms','uid___A002_Xbec3cb_X4227.polcalibrated.APP.ms','uid___A002_Xbec3cb_X448f.polcalibrated.APP.ms','uid___A002_Xbec3cb_X468b.polcalibrated.APP.ms','uid___A002_Xbec3cb_X4947.polcalibrated.APP.ms','uid___A002_Xbec3cb_X4bca.polcalibrated.APP.ms','uid___A002_Xbec3cb_X4de4.polcalibrated.APP.ms'],
        spw=str(spi),
        imagename = '%s.APP.spw%i'%(field,spi),
        field=field,
        mode='mfs',
        cell='0.2arcsec',
        imsize=256,
        outframe='BARY',
        stokes = 'IQUV',
        niter=100,
        mask='',
        interactive=F,
        pbcor=False,
        weighting='briggs',
        robust=0.5,
        phasecenter='')






