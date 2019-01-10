# steps to process hd98800 data to something that might be better
# than the observatory products

# using CASA 5.1.2-4

# do all the processing on the SSD, shift elsewhere after

# the data output by running the alma script
cal_dir = ('/Volumes/hdd/grant/astro/rawdata/alma/hd98800/2017.1.00350.S/'
           'sg_ouss_id/group_ouss_id/member_ouss_id/calibrated/')

# working dir
selfcal_dir = '/Users/grant/tmp/hd98800/self-cal/'

# file names
fn1 = 'uid___A002_Xc6d2f9_X7bf8'
f1str = 'X7bf8'

fn2 = 'uid___A002_Xc6ff69_X311b'
f2str = 'X311b'

# first split to get just target data, put these in self-cal directory
split(vis=cal_dir+fn1+'.ms',outputvis=selfcal_dir+fn1+'.hd98800.ms',spw='19,21,23,25',
      keepflags=False,intent='OBSERVE_TARGET#ON_SOURCE',field='HD_98800')

split(vis=cal_dir+fn2+'.ms',outputvis=selfcal_dir+fn2+'.hd98800.ms',spw='19,21,23,25',
      keepflags=False,intent='OBSERVE_TARGET#ON_SOURCE',field='HD_98800')

# ---- self-cal ----

# set fn and do interactively, run in selfcal_dir
fn = fn1
fstr = f1str
wt = 'briggs'
robust = 0.5

# duplicate or split to working file
# we end up combining spws to get s/n, so averaging them here for speed is OK
os.system('rm -r '+selfcal_dir+fn+'.hd98800.cont.tmp.*')
#os.system('cp -r '+selfcal_dir+fn+'.hd98800.ms '+selfcal_dir+fn+'.hd98800.cont.tmp.ms')
split(vis=selfcal_dir+fn+'.hd98800.ms',
      width=[32,32,32,480],
      outputvis=selfcal_dir+fn+'.hd98800.cont.tmp.ms',
      datacolumn='data')

plotms(vis=selfcal_dir+fn+'.hd98800.cont.tmp.ms',
       spw='',xaxis='uvdist',yaxis='amp',
       coloraxis='spw',plotfile='cont_uvplot.png',showgui=True)

# continuum for self-cal, use clean rather than tclean
os.system('rm -r '+selfcal_dir+fstr+'.cont.tmp.p0.*')
clean(vis=selfcal_dir+fn+'.hd98800.cont.tmp.ms',
       imagename=selfcal_dir+fstr+'.cont.tmp.p0',
       imsize=[500,500], cell='0.005arcsec',
       weighting=wt, robust=robust,
       npercycle=400, interactive=True)

# X311b
# 100 iter
# rms in original image is 0.048mJy/beam
# peak flux (on N side of disk) is 4.5mJy/beam
# beam area is 95
# -> s/n = 94
# 400 iter
# rms in original image is 0.032mJy/beam
# peak flux (on N side of disk) is 4.2mJy/beam
# beam area is 95
# -> s/n = 132
# more iterations is similar

# X7bf8
# 400 iter rms=0.027mJy/beam, peak=3.9mJy/beam, s/n=144, beam=84

os.system('rm -r '+selfcal_dir+fstr+'.pcal1')
gaincal(vis=selfcal_dir+fn+'.hd98800.cont.tmp.ms',
        caltable=selfcal_dir+fstr+'.pcal1',
        gaintype='T', refant='DA52',
        calmode='p', solint='40min', combine='spw,scan', minsnr=2,
        minblperant=6)

plotcal(caltable=selfcal_dir+fstr+'.pcal1',
        xaxis='time',yaxis='phase',timerange='',
        iteration='antenna',subplot=771,plotrange=[0,0,-90,90],
        figfile=selfcal_dir+fstr+'.selfcal.p0.png',fontsize=6)

os.system('rm -r '+selfcal_dir+fn+'.hd98800.cont.tmp.pcal1.ms')
os.system('cp -r '+selfcal_dir+fn+'.hd98800.cont.tmp.ms ' +selfcal_dir+fn+'.hd98800.cont.tmp.pcal1.ms')
applycal(vis=selfcal_dir+fn+'.hd98800.cont.tmp.pcal1.ms',
         gaintable=[selfcal_dir+fstr+'.pcal1'],
         spwmap=[0,0,0,0],
         interp='linear')

os.system('rm -r '+selfcal_dir+fstr+'.cont.tmp.p1.*')
clean(vis=selfcal_dir+fn+'.hd98800.cont.tmp.pcal1.ms',
       imagename=selfcal_dir+fstr+'.cont.tmp.p1',
       imsize=[500,500], cell='0.005arcsec',
       mask=selfcal_dir+fstr+'.cont.tmp.p0.mask',
       weighting=wt, robust=robust, npercycle=400, interactive=True)

# rms after one round, use *
# X311b
# combine='spw', solint='inf': rms=0.018mJy/beam, peak=5.3mJy/beam, s/n=294, beam=121
# combine='spw,scan', solint='10min': rms=0.019mJy/beam, peak=4.9mJy/beam, s/n=258, beam=112
# combine='spw,scan', solint='10min', minsnr=2: rms=0.019mJy/beam, peak=4.5mJy/beam, s/n=237, beam=100
#* combine='spw,scan', solint='20min', minsnr=2: rms=0.018mJy/beam, peak=4.3mJy/beam, s/n=238, beam=95. need this to not flag anything so keep full resolution

# X7bf8
# combine='spw,scan', solint='20min', minsnr=2: rms=0.022mJy/beam, peak=4.4mJy/beam, s/n=200, beam=97., some flagging
# combine='spw,scan', solint='30min', minsnr=2: rms=0.022mJy/beam, peak=4.1mJy/beam, s/n=200, beam=91., some flagging
#* combine='spw,scan', solint='40min', minsnr=2: rms=0.02mJy/beam, peak=3.9mJy/beam, s/n=195, beam=84., no flagging


# second round
os.system('rm -r '+selfcal_dir+fstr+'.pcal2')
gaincal(vis=selfcal_dir+fn+'.hd98800.cont.tmp.pcal1.ms',
        caltable=selfcal_dir+fstr+'.pcal2',
        gaintype='T', refant='DA52',
        calmode='p', solint='40min', combine='spw,scan', minsnr=2,
        minblperant=6)

plotcal(caltable=selfcal_dir+fstr+'.pcal2',
        xaxis='time',yaxis='phase',timerange='',
        iteration='antenna',subplot=771,plotrange=[0,0,-90,90],
        figfile=selfcal_dir+fstr+'.selfcal.p1.png',fontsize=6)

os.system('rm -r '+selfcal_dir+fn+'.hd98800.cont.tmp.pcal2.ms')
os.system('cp -r '+selfcal_dir+fn+'.hd98800.cont.tmp.pcal1.ms ' +selfcal_dir+fn+'.hd98800.cont.tmp.pcal2.ms')
applycal(vis=selfcal_dir+fn+'.hd98800.cont.tmp.pcal2.ms',
         gaintable=[selfcal_dir+fstr+'.pcal2'],
         spwmap=[0,0,0,0],
         interp='linear')

os.system('rm -r '+selfcal_dir+fstr+'.cont.tmp.p2.*')
clean(vis=selfcal_dir+fn+'.hd98800.cont.tmp.pcal2.ms',
       imagename=selfcal_dir+fstr+'.cont.tmp.p2',
       imsize=[500,500], cell='0.005arcsec',
       mask=selfcal_dir+fstr+'.cont.tmp.p0.mask',
       weighting=wt, robust=robust, npercycle=400, interactive=True)

# X311b
# combine='spw,scan', solint='20min', minsnr=2: rms=0.018mJy/beam, peak=4.2mJy/beam, s/n=233, beam=95

# X7bf8
# combine='spw,scan', solint='40min', minsnr=2: rms=0.02mJy/beam, peak=3.9mJy/beam, s/n=195, beam=84

# was only able to avoid losing antennas with the same gaincal parameters
# as in the first round, and no improvement results. resolution is important
# so don't try any more rounds


# decide we're done after one round of self-cal
# and apply the calibration to the full data
fn = fn2
fstr = f2str

os.system('rm -r '+selfcal_dir+fstr+'.hd98800.pcal1.ms')
os.system('cp -r '+selfcal_dir+fn+'.hd98800.ms ' +selfcal_dir+fstr+'.hd98800.pcal1.ms')
applycal(vis=selfcal_dir+fstr+'.hd98800.pcal1.ms',spwmap=[0,0,0,0],
         gaintable=[selfcal_dir+fstr+'.pcal1'],interp='linear')

# concatenate observations, one massive file.
os.system('rm -r '+selfcal_dir+'hd98800.pcal1.ms')
os.system('cp -r '+selfcal_dir+f1str+'.hd98800.pcal1.ms '+selfcal_dir+'hd98800.pcal1.ms')
ms.open(selfcal_dir+'hd98800.pcal1.ms', nomodify=False)
ms.concatenate(selfcal_dir+f2str+'.hd98800.pcal1.ms')
ms.close()

# rms in final image (briggs) is 0.014uJy/beam, peak is 3.9mJy/beam
# rms in final image (natural) is 0.014uJy/beam, peak is 6mJy/beam

# from here separate products are split out using splits.py
