import rebound
import numpy as np
from scipy.optimize import fsolve
#import cPickle as pickle
import pickle
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import LogNorm
import sys


#conversion constants
yr = (2.0*np.pi)
mj = 0.00095458 #m_J in m_Sun
dtr = np.pi/180.0


#read in parameters as command line arguments
#amin,amax,na, imin,imax,ni, Om, ecc, outfile (with angles in degrees)
r_in = float(sys.argv[1]) 
r_out = float(sys.argv[2]) 
N_a = int(sys.argv[3]) 
da = (r_out-r_in)/N_a

i_min = float(sys.argv[4]) *dtr 
i_max = float(sys.argv[5]) *dtr 
N_inc = int(sys.argv[6])
dinc = (i_max-i_min)/N_inc

Om_fixed = float(sys.argv[7]) *dtr 
ecc_fixed = float(sys.argv[8])

Ntp=N_a*N_inc
Ntp_init=Ntp

outfile=sys.argv[9]


print(Ntp)

outplot=outfile+'.pdf'
outfile=outfile+'.pickle'


#how to distribute inclinations?
UNIFORM_IN_MUTUAL = False 

#eqn that mutual inclination phi satisfies
def mutual_inc(i2,*params):
    #input angles in radians
    i1,Om1,Om2,phi = params
    
    #np.arccos( np.cos(i1)*np.cos(i2) + np.sin(i1)*np.sin(i2)*np.cos(Om2-Om1) )
    return np.cos(i1)*np.cos(i2) + np.sin(i1)*np.sin(i2)*np.cos(Om2-Om1) - np.cos(phi) #E-e*math.sin(E)-M

#distance in pc
#par = 0.023
#dist = 44.9

#initialise sim & set integrator options
sim  = rebound.Simulation()
sim.integrator = "whfast"
sim.t = 2017.874 * yr

#integrate until tmax
tmax = 1e6 * yr #250

#interval between data points
interval = 1e2 * yr #0.8606*yr/50. #1e3 * yr

#times to get data at
times_output = np.arange(0, tmax+interval, interval)
numtimes=len(times_output)


#add the various components of the planetary system
#BaBb

sim.add(m=0.58) 
sim.add(m=0.7,e=0.785,inc=66.8*dtr,
        omega=109.6*dtr,Omega=(90+337.6)*dtr,
        P=0.8606*yr,
#        a=0.023*44.9,
        T=2002.563*yr)
sim.move_to_com()

#initial test particle distribution
initial_a=[]
initial_i=[]
initial_phi=[]

#to keep track of changing particle indices
initial_a_of_remaining=[] 
initial_i_of_remaining=[]
initial_phi_of_remaining=[]

#ejection times
t_eject=np.zeros(Ntp)+tmax/yr
orig_indices=list(range(Ntp))

for index_a in range(N_a):
    for index_inc in range(N_inc):
        i=index_a*N_inc+index_inc
        
        if UNIFORM_IN_MUTUAL == False:
            a0=r_in+da/2.+index_a*da 
            inc0=i_min+dinc/2.+index_inc*dinc
            Omega0=Om_fixed
            e0=ecc_fixed 
            
            initial_a.append(a0)
            initial_a_of_remaining.append(a0)
            initial_i.append(inc0)
            initial_i_of_remaining.append(inc0)
            
            i1=sim.particles[1].inc
            i2=inc0
            Om1=sim.particles[1].Omega
            Om2=Omega0
            
            #print(np.arccos( np.cos(i1)*np.cos(i2) + np.sin(i1)*np.sin(i2)*np.cos(Om2-Om1) ))
            
            initial_phi.append( np.arccos( np.cos(i1)*np.cos(i2) + np.sin(i1)*np.sin(i2)*np.cos(Om2-Om1) ) )
            initial_phi_of_remaining.append( np.arccos( np.cos(i1)*np.cos(i2) + np.sin(i1)*np.sin(i2)*np.cos(Om2-Om1) ) )
            
        else:
            a0=r_in+da/2.+index_a*da 
            phi=i_min+dinc/2.+index_inc*dinc 
            Omega0=Om_fixed 
            e0=ecc_fixed
            
            i1=sim.particles[1].inc
            Om1=sim.particles[1].Omega
            Om2=Omega0
            
            params=(i1,Om1,Om2,phi)
            i2=fsolve(mutual_inc,1.0,params)
            inc0=i2
            
            
            initial_a.append(a0)
            initial_a_of_remaining.append(a0)
            initial_i.append(inc0)
            initial_i_of_remaining.append(inc0)
            
            initial_phi.append(phi)
            initial_phi_of_remaining.append(phi)
            
            
        sim.add(a=a0, e=e0, inc=inc0, 
                Omega=np.pi/2+Omega0, omega=np.random.uniform(0,2.0*np.pi),
                M=np.random.uniform(0,2.0*np.pi))


sim.move_to_com()

#Aab
sim.add(m=1.3,e=0.52,inc=88.58*dtr,
        omega=(180+63.16)*dtr,Omega=(90+4.71)*dtr,
#        P=246.32*yr,
        a=1.22*44.9,
        T=2022.71*yr)


#fig = rebound.OrbitPlot(sim, slices=True, lim=25, limz=25*2/3.)
#fig.savefig('ini.png')
#plt.show()


# previously Aab elements were (from MSC):
#sim.add(m=1.3,e=0.4,inc=88.1*dtr,omega=249.1*dtr,Omega=184.2*dtr,P=214.*yr,T=2023.1*yr)

sim.move_to_com()


sim.dt=0.8606*yr/20.0 #suitably small timestep


#number of bodies in the system
Nbodies = len(sim.particles)
print(Nbodies)
#initial total energy
E0 = sim.calculate_energy()

#perform the integration

x1=[]
y1=[]
z1=[]
x2=[]
y2=[]
z2=[]
x3=[]
y3=[]
z3=[]
inner_ecc=[]

numpart=[]

for i, time in enumerate(times_output):
    numpart.append(Ntp)
    sim.integrate(time, exact_finish_time=0)
#    print("Time (years): " + str(sim.t/yr))

    
#    print(Ntp)
    remove=[]
    
    for p in range (Ntp):
        #print(sim.particles[p+2].e)
        
        d_abs=np.sqrt((sim.particles[p+2].x)**2+(sim.particles[p+2].y)**2+(sim.particles[p+2].z)**2)
        ejected = d_abs>2000. 
        
        if ejected == True: #sim.particles[p+2].e>1:
            remove.append(p+2)
            Ntp-=1
            
    #index offset to keep track of shifting indices after ejection
    offset=0      
    for ind in remove:
        #print(np.sqrt((sim.particles[ind-offset].x)**2+(sim.particles[ind-offset].y)**2+(sim.particles[ind-offset].z)**2))
        sim.remove(index=ind-offset)
        t_eject[orig_indices[ind-2-offset]]=time/yr
        del initial_a_of_remaining[ind-2-offset]
        del initial_i_of_remaining[ind-2-offset]
        del initial_phi_of_remaining[ind-2-offset]
        del orig_indices[ind-2-offset]
        offset+=1
          
    '''
    x1.append(sim.particles[0].x)
    y1.append(sim.particles[0].y)
    z1.append(sim.particles[0].z)
    x2.append(sim.particles[1].x)
    y2.append(sim.particles[1].y)
    z2.append(sim.particles[1].z)
    x3.append(sim.particles[-1].x)
    y3.append(sim.particles[-1].y)
    z3.append(sim.particles[-1].z)
    '''
    
pxs=[]
pys=[]
pzs=[]

remaining_a=[]
remaining_i=[]
remaining_phi=[]

for i in range(Ntp):
    p = sim.particles[i+2]
    d = np.sqrt((p.x-sim.particles[0].x)**2+(p.y-sim.particles[0].y)**2+(p.z-sim.particles[0].z)**2)
    
    pxs.append(p.x)
    pys.append(p.y)
    pzs.append(p.z)
    remaining_a.append(initial_a_of_remaining[i])
    remaining_i.append(initial_i_of_remaining[i])
    remaining_phi.append(initial_phi_of_remaining[i])
        

#make array of ejection times
imgdata=np.zeros((N_inc,N_a))
for i in range(N_a):
        for j in range(N_inc):
            imgdata[N_inc-1-j][i]=t_eject[i*N_inc+j]/1e6


#save output: grid parameters (input), image array, and which inclination the particles are uniform in
output_dict = {'a_min':r_in, 'a_max':r_out,'N_a':N_a,'i_min':i_min/dtr,'i_max':i_max/dtr,'N_i':N_inc,'Om':Om_fixed/dtr,'ecc':ecc_fixed,'imgdata':imgdata,'UNIFORM_IN_MUTUAL':UNIFORM_IN_MUTUAL}

with open(outfile,'wb') as handle:
    pickle.dump(output_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

fig=plt.figure()
ax=plt.gca()
plt.imshow(imgdata,cmap='binary', aspect='auto',interpolation='none',extent=[r_in,r_out,i_min/dtr,i_max/dtr],vmin=0,vmax=1)
plt.xlabel('a / au')

if UNIFORM_IN_MUTUAL==True:
    plt.ylabel('Mutual inclination / deg')
else:
    plt.ylabel('Inclination / deg')

ax.annotate(r'$\mathregular{e=%.3f}$'%ecc_fixed, xy=(0.95, 0.95), xycoords='axes fraction',horizontalalignment='right', verticalalignment='top',fontsize=14)

#ax.annotate(r'$\mathregular{\Omega=%.2f^{o}}$'%Om, xy=(0.95, 0.95), xycoords='axes fraction',horizontalalignment='right', verticalalignment='top',fontsize=14)

cb=plt.colorbar()
cb.set_label('Lifetime / Myr')



#print fractional energy change
fract_dE = (sim.calculate_energy()-E0)/E0
print("Simulation complete; dE/E = " + str(fract_dE))   

fig.savefig(outplot)
plt.show()
