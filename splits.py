import uvplot

# split ms files and uv tables for continuum imaging and modelling

# assume self-cal files have been moved here
selfcal_dir = '/Volumes/hdd/grant/astro/rawdata/alma/hd98800/self-cal/'
selfcal_dir = '/Users/grant/tmp/hd98800/self-cal/'

split_dir = '/Volumes/hdd/grant/astro/rawdata/alma/hd98800/splits/'

fn = 'X7bf8'
fn = 'X311b'

# continuum files for imaging
split(vis=selfcal_dir+'hd98800.pcal1.ms',
      timebin='20s', keepflags=False,
      width=[32,32,32,480,32,32,32,480],
      outputvis=split_dir+'hd98800.pcal1.cont.ms',
      datacolumn='CORRECTED')

split(vis=selfcal_dir+fn+'.hd98800.pcal1.ms',
      timebin='20s', keepflags=False,
      width=[32,32,32,480],
      outputvis=split_dir+fn+'.hd98800.pcal1.cont.ms',
      datacolumn='DATA')

# continuum files for modelling

# first spw from each observation
# drgmk version of uvplot.io to export multiple channels
uvplot.io.export_uvtable(split_dir+'uv-w32-t20-'+fn+'-spw0.txt', tb,
                         vis=selfcal_dir+fn+'.hd98800.pcal1.ms',
                         split=split, keep_tmp_ms=True, datacolumn='DATA',
                         channel='all',
                         split_args={'vis':selfcal_dir+fn+'.hd98800.pcal1.ms',
                                     'timebin':'20s', 'keepflags':False,
                                     'width':32, 'spw':'0',
                                     'outputvis':split_dir+fn+'.hd98800.pcal1.cont.spw0.ms',
                                     'datacolumn':'DATA'
                                    }
                        )

# and split of first spws from concatenated ms file
uvplot.io.export_uvtable(split_dir+'uv-w32-t20-spw04.txt', tb, vis=split_dir+'hd98800.pcal1.cont.ms',
                         split=split, keep_tmp_ms=True, datacolumn='DATA',
                         channel='all',
                         split_args={'vis':split_dir+'hd98800.pcal1.cont.ms',
                                     'keepflags':False, 'spw':'0,4',
                                     'outputvis':split_dir+'hd98800.pcal1.cont.spw04.ms',
                                     'datacolumn':'DATA'
                                    }
                        )



# cube creation, spw=3, +/-20 -> 914-977
# systemic velocity of BaBb from Torres+95 is 5.73km/s, orbit
# has probably moved a bit since then.

# cut down to near CO line
os.system('rm -r '+split_dir+'hd98800.pcal1.CO.tmp.ms')
split(vis=selfcal_dir+'hd98800.pcal1.ms',
      outputvis=split_dir+'hd98800.pcal1.CO.tmp.ms',
      spw='3:900~1000,7:900~1000',datacolumn='corrected')

# combine spws from two obs in rough region near CO line
# shift frequencies to barycentric frame so that 230538 is 0km/s
# after this the first channel is at 230508.957MHz, and the 
# width is 0.488246MHz.
os.system('rm -r '+split_dir+'hd98800.pcal1.CO.tmp.bary.ms')
mstransform(vis=split_dir+'hd98800.pcal1.CO.tmp.ms',
            outputvis=split_dir+'hd98800.pcal1.CO.tmp.bary.ms',
            douvcontsub=True,fitorder=1,
            combinespws=True,
            regridms=True,outframe='BARY',
            datacolumn='DATA')

# cut out final CO. Want -7.3<v<17.4km/s, which is
# -28 to +12 channels from zero velocity. First channel
# is at 230508.957MHz, so zero velocity is at the 59th channel.
# Therefore want channels 31 to 71. 
os.system('rm -r '+split_dir+'hd98800.pcal1.CO.ms')
split(vis=split_dir+'hd98800.pcal1.CO.tmp.bary.ms',
      outputvis=split_dir+'hd98800.pcal1.CO.ms',
      timebin='20s', keepflags=False,
      spw='0:31~71',datacolumn='DATA')

# export this to a series of uv tables
os.system('rm -r '+split_dir+'uv-cube/*')
for i in np.arange(0,41):
    uvplot.io.export_uvtable(split_dir+'uv-cube/uv-CO-ch{:02}.txt'.format(i), tb,
                             vis=split_dir+'hd98800.pcal1.CO.ms',split=split,
                             split_args={'spw': '0:{}'.format(i),
                                         'vis':split_dir+'hd98800.pcal1.CO.ms',
                                         'datacolumn': 'data', 'keepflags': False},
                             datacolumn='DATA')
