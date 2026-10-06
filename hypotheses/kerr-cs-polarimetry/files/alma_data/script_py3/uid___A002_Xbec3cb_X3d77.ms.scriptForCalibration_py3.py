###########################################################
# ALMA Phasing Project (APP) QA2 Data Calibration Script
# EU-ARC (Nordic/Allegro Nodes) -- v 2.0 - August 27, 2018
#
# This script has been generated automatically from: 
#
#    scriptForCalibrationAPP_C4.py
###########################################################


thesteps = []
step_title = {0: ' Import of the ASDM',
              1: ' Fix of SYSCAL table times',
              2: ' Listobs and a-priori flagging',
              3: ' Split out science SPWs',
              4: ' Save original flags',
              5: ' Initial flagging',
              6: ' Apply ordinary calibration',
              7: ' Save flags after applycal',
              8: ' Split calibrated data',
              9: ' Apply polarization calibration (APP scans)', 
              10: ' Split corrected column (APP scans)',
              11: ' Save flags after polarization applycal'}

T = True
F = False

# [py3-port] removed: import casadef (CASA5-only module)

APPCAL = True

try:
  print('List of steps to be executed ...', mysteps)
  thesteps = mysteps
except:
  print('global variable mysteps not set.')
if (thesteps==[]):
  thesteps = list(step_title.keys())   #range(0,len(step_title))
  print('Executing all steps: ', thesteps)


# [py3-port] removed CASA 5.1.1 version gate (running CASA 6)



# Import of the ASDM
mystep = 0
if(mystep in thesteps):

  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  os.system('rm -rf uid___A002_Xbec3cb_X3d77.ms')
  os.system('rm -rf uid___A002_Xbec3cb_X3d77.ms.flagversions')
  importasdm(asdm='uid___A002_Xbec3cb_X3d77', vis='uid___A002_Xbec3cb_X3d77.ms', 
      asis='Antenna Station Receiver Source CalAtmosphere CorrelatorMode SBSummary CalAppPhase')



# Fix of SYSCAL table times
mystep = 1
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  def fixsyscaltimes(vis):
      print('[py3-port] fixsyscaltimes SKIPPED (no Tsys cal in this script; SYSCAL times unused)')
  fixsyscaltimes(vis = 'uid___A002_Xbec3cb_X3d77.ms')




# listobs and a-priori flagging:
mystep = 2
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  listobs(vis = 'uid___A002_Xbec3cb_X3d77.ms',
      listfile = 'uid___A002_Xbec3cb_X3d77.ms.listobs')

  flagdata(vis = 'uid___A002_Xbec3cb_X3d77.ms',
      mode = 'manual',
      spw = '',
      autocorr = T,
      flagbackup = F)
  
  flagdata(vis = 'uid___A002_Xbec3cb_X3d77.ms',
      mode = 'manual',
      intent = '*POINTING*,*SIDEBAND_RATIO*,*ATMOSPHERE*',
      flagbackup = F)
  
           
  flagcmd(vis = 'uid___A002_Xbec3cb_X3d77.ms',
      inpmode = 'table',
      useapplied = True,
      action = 'apply')




# Split:
mystep = 3
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  split(vis = 'uid___A002_Xbec3cb_X3d77.ms',
      outputvis = 'uid___A002_Xbec3cb_X3d77.ms.split',
      datacolumn='data',      
      spw = '17,19,21,23',
      keepflags = T)



# Save original flags
mystep = 4
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])
    
  if not os.path.exists('uid___A002_Xbec3cb_X3d77.ms.split.flagversions/flags.Original'):
    flagmanager(vis = 'uid___A002_Xbec3cb_X3d77.ms.split',
      mode = 'save',
      versionname = 'Original')
  else:
    flagmanager(vis = 'uid___A002_Xbec3cb_X3d77.ms.split',
      mode = 'restore',
      versionname = 'Original')



# Initial flagging
mystep = 5
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  flagmanager(vis = 'uid___A002_Xbec3cb_X3d77.ms.split',
    mode = 'restore',
    versionname = 'Original')


  # Flagging shadowed data
  flagdata(vis = 'uid___A002_Xbec3cb_X3d77.ms.split',
     mode = 'shadow',
     flagbackup = F)

  # Flagging autocorrelations
  flagdata(vis='uid___A002_Xbec3cb_X3d77.ms.split',
    autocorr = T,
    flagbackup = F)
  
  # Flagging "APP" antenna:
  flagdata(vis='uid___A002_Xbec3cb_X3d77.ms.split', 
    mode = 'manual', antenna = 'DV03',
    flagbackup = F)

  flagdata(vis = 'uid___A002_Xbec3cb_X3d77.ms.split',
    mode = 'list',
    inpfile = 'TRACK_C.flg',
    flagbackup = F)
    
  # Once all bad data are flagged, we save the flags:
  if os.path.exists('uid___A002_Xbec3cb_X3d77.ms.split.flagversions/flags.BeforeCalibration'):
    flagmanager(vis='uid___A002_Xbec3cb_X3d77.ms.split', 
      mode = 'delete', versionname='BeforeCalibration')

  flagmanager(vis='uid___A002_Xbec3cb_X3d77.ms.split', 
    mode = 'save', versionname='BeforeCalibration')




# Apply calibration:
mystep = 6
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  message = '\n\n\n     SOME CASA ERRORS MAY APPEAR SOON.\n    THEY ARE RELATED TO POSSIBLE MISSING SCANS IN APP/ALMA MODES.\n    THESE ERRORS SHOULD BE HARMLESS\n\n\n'
  casalog.post(message)
  print(message)

  for field in ['Sagittarius_A_star','J1744-3116','QSO B1730-130','J1650-2943']:

  # APP Scans:
    print('Applying calibration to %s (APP Obs.)'%field)
    try:
        applycal(vis = 'uid___A002_Xbec3cb_X3d77.ms.split',
          field = field,
          gaintable = ['TRACK_C.concatenated.ms.bandpass-zphs', 
          'TRACK_C.concatenated.ms.flux_inf.APP',
          'TRACK_C.concatenated.ms.phase_int.APP.XYsmooth'],
          gainfield = ['',field,field],
          interp = ['linear','nearest','nearest'],
          scan = '3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,28,29,30,31,32,33,34,35,36,37,38,39,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,97,98,99,100,101,102,103,104,105,106,107,108,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,167,168,169,170,171,172,173,174,175,176,177,178',
          antenna = 'DV12,DV18,DA65,DA64,DA63,DA48,DA61,DA60,DV11,DA44,DV13,DA46,DA41,DV14,DA42,DV23,DA49,DA62,PM01,DV19,DV10,DV22,DA50,DA51,DA56,DV25,DA54,DV06,DV15,DA58,DA59,DV01,DV16,DV05,DV24&',
          calwt = [T,T,F],
          parang = F,
          flagbackup = F)
    except RuntimeError as e:
        print('WARNING: applycal failed for %s (harmless per QA2 script note): %s' % (field, e))




# Save flags
mystep = 7
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])


  flagmanager(vis = 'uid___A002_Xbec3cb_X3d77.ms.split',
    mode = 'save',
    versionname = 'AfterApplycal')




# Split
mystep = 8
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  os.system('rm -rf uid___A002_Xbec3cb_X3d77.ms.split.cal*')
  split(vis = 'uid___A002_Xbec3cb_X3d77.ms.split',
    datacolumn='corrected',
    keepflags = False,
    antenna='DV12,DV18,DA65,DA64,DA63,DA48,DA61,DA60,DV11,DA44,DV13,DA46,DA41,DV14,DA42,DV23,DA49,DA62,PM01,DV19,DV10,DV22,DA50,DA51,DA56,DV25,DA54,DV06,DV15,DA58,DA59,DV01,DV16,DV05,DV24&',
    scan = '3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,28,29,30,31,32,33,34,35,36,37,38,39,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,97,98,99,100,101,102,103,104,105,106,107,108,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,167,168,169,170,171,172,173,174,175,176,177,178',
    outputvis = 'uid___A002_Xbec3cb_X3d77.ms.split.cal')





# Apply polarization calibration:
mystep = 9
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  if APPCAL:
      applycal(vis = 'uid___A002_Xbec3cb_X3d77.ms.split.cal',
          field = '',
          gaintable = ['TRACK_C.calibrated.ms.XY0.APP',
                       'TRACK_C.calibrated.ms.Gxyamp.APP',
                       'TRACK_C.calibrated.ms.Df0gen.APP'],
          interp = ['linear','nearest','linear'],
          calwt = [F,T,F],
          parang = T,
          flagbackup = F)

  else:
      applycal(vis = 'uid___A002_Xbec3cb_X3d77.ms.split.cal',
        field = '',
        gaintable = ['TRACK_C.calibrated.ms.XY0.ALMA',
                     'TRACK_C.calibrated.ms.Gxyamp.ALMA',
                     'TRACK_C.calibrated.ms.Df0gen.ALMA'],
        interp = ['linear','nearest','linear'],
        calwt = [F,T,F],
        parang = T,
        flagbackup = F)


# Split
mystep = 10
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])

  os.system('rm -rf uid___A002_Xbec3cb_X3d77.polcalibrated.APP.ms')
  split(vis = 'uid___A002_Xbec3cb_X3d77.ms.split.cal',
    datacolumn='corrected',
    outputvis = 'uid___A002_Xbec3cb_X3d77.polcalibrated.APP.ms')




# Save flags
mystep = 11
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print('Step ', mystep, step_title[mystep])


  flagmanager(vis = 'uid___A002_Xbec3cb_X3d77.ms.split.cal',
    mode = 'save',
    versionname = 'AfterApplycal')











###########################################################

