# generate some clean images

selfcal_dir = '/Volumes/hdd/grant/astro/rawdata/alma/hd98800/self-cal/'
selfcal_dir = '/Users/grant/tmp/hd98800/self-cal/'

split_dir = '/Volumes/hdd/grant/astro/rawdata/alma/hd98800/splits/'
clean_dir = '/Volumes/hdd/grant/astro/rawdata/alma/hd98800/clean/'
fits_dir = '/Volumes/hdd/grant/astro/rawdata/alma/hd98800/fits/'


# look at each observation separately
fn = 'X7bf8'
fn = 'X311b'
clean(vis=split_dir+fn+'.hd98800.pcal1.cont.ms',
      imagename=clean_dir+fn+'hd98800.pcal1.cont.uniform',
      imsize=[500,500],cell='0.005arcsec',
      weighting='uniform',interactive=True)

# some continuum images
clean(vis=split_dir+'hd98800.pcal1.cont.ms',
      imagename=clean_dir+'hd98800.pcal1.cont.natural',
      imsize=[1024,1024],cell='0.005arcsec',
      weighting='natural',interactive=True)

exportfits(imagename=clean_dir+'hd98800.pcal1.cont.natural.image',
           fitsimage=fits_dir+'hd98800.pcal1.cont.natural.fits')
exportfits(imagename=clean_dir+'hd98800.pcal1.cont.natural.residual',
           fitsimage=fits_dir+'hd98800.pcal1.cont.natural.residual.fits')

clean(vis=split_dir+'hd98800.pcal1.cont.ms',
      imagename=clean_dir+'hd98800.pcal1.cont.briggs',
      imsize=[500,500],cell='0.005arcsec',
      weighting='briggs',robust=0.5,interactive=True)

exportfits(imagename=clean_dir+'hd98800.pcal1.cont.briggs.image',
           fitsimage=fits_dir+'hd98800.pcal1.cont.briggs.fits')

clean(vis=split_dir+'hd98800.pcal1.cont.ms',
      imagename=clean_dir+'hd98800.pcal1.cont.uniform',
      imsize=[1024,1024],cell='0.005arcsec',
      weighting='uniform',interactive=True)

exportfits(imagename=clean_dir+'hd98800.pcal1.cont.uniform.image',
           fitsimage=fits_dir+'hd98800.pcal1.cont.uniform.fits')

clean(vis=split_dir+'hd98800.pcal1.cont.ms',
      imagename=clean_dir+'hd98800.pcal1.cont.superuniform',
      imsize=[500,500],cell='0.005arcsec',
      weighting='superuniform',npixels=4,interactive=True)

clean(vis=split_dir+'hd98800.pcal1.cont.spw04.ms',
      imagename=clean_dir+'hd98800.pcal1.cont.spw04.natural',
      imsize=[1024,1024],cell='0.005arcsec',
      weighting='natural',interactive=True)

exportfits(imagename=clean_dir+'hd98800.pcal1.cont.spw04.natural.image',
           fitsimage=fits_dir+'hd98800.pcal1.cont.spw04.natural.fits')


# dirty cube for modelling, not quite centered but close
# perhaps because the phase shift required is rather large
os.system('rm -r '+clean_dir+'hd98800.pcal1.CO.approx_center.natural*')
tclean(vis=split_dir+'hd98800.pcal1.CO.ms',
       imagename=clean_dir+'hd98800.pcal1.CO.approx_center.natural', specmode='cube',
       restfreq='230538.0MHz',outframe='BARY',
       phasecenter='J2000 170d31m17.6155s -24d46m39.5043s',
       restoringbeam='common',
       weighting='natural',start=1,nchan=40,niter=0,
       interactive=False, imsize=[100,100], cell='0.005arcsec')

exportfits(imagename=clean_dir+'hd98800.pcal1.CO.approx_center.natural.image',
           fitsimage=fits_dir+'hd98800.pcal1.CO.approx_center.natural.fits',
           velocity=True)

# cube for images, still off center
os.system('rm -r '+clean_dir+'hd98800.pcal1.CO.natural*')
tclean(vis=split_dir+'hd98800.pcal1.CO.ms',
       imagename=clean_dir+'hd98800.pcal1.CO.natural', specmode='cube',
       restfreq='230538.0MHz',outframe='BARY',
       restoringbeam='common',
       weighting='natural',start=1,nchan=40,niter=1000,
       interactive=True, imsize=[1024,1024], cell='0.005arcsec')

os.system('rm -r '+clean_dir+'hd98800.pcal1.CO.natural.fits')
exportfits(imagename=clean_dir+'hd98800.pcal1.CO.natural.image',
           fitsimage=fits_dir+'hd98800.pcal1.CO.natural.fits',
           velocity=True)

immoments(imagename=fits_dir+'hd98800.pcal1.CO.natural.fits',
          moments=0,#includepix=[0.003,100],
          outfile=clean_dir+'hd98800.pcal1.CO.natural.mom0',stretch=False)

exportfits(imagename=clean_dir+'hd98800.pcal1.CO.natural.mom0',
           fitsimage=fits_dir+'hd98800.pcal1.CO.natural.mom0.fits')

immoments(imagename=fits_dir+'hd98800.pcal1.CO.natural.fits',
          moments=[1],axis='spectral',region='',box='',
          stokes='',mask='',includepix=[0.0025, 100],excludepix=-1,
          outfile=clean_dir+'hd98800.pcal1.CO.natural.mom1.0025',stretch=False)

exportfits(imagename=clean_dir+'hd98800.pcal1.CO.natural.mom1.0025',
           fitsimage=fits_dir+'hd98800.pcal1.CO.natural.mom1.0025.fits')
