

# get a consensus on the arrivals of known datasets, start by getting the aq2009 or the iquiaue dataset


import sys

import seisbench
import seisbench.data as sbd
import seisbench.models as sbm
import seisbench.generate as sbg

import matplotlib.pyplot as plt
plt.rcParams['font.family']='helvetica'


from obspy import Stream, Trace
from obspy.core import UTCDateTime as UT


start_index = int(sys.argv[1])

# The Iquique model is problematic because the traces are 
data = sbd.CEED()
data.metadata['split']='train'

train, dev, test = data.train_dev_test()
print(train,dev,test)
print(len(data.metadata))
print(data.metadata)

print(data.metadata.iloc[0])

train_generator = sbg.GenericGenerator(train)
dev_generator = sbg.GenericGenerator(dev)


pn_model = sbm.PhaseNet.from_pretrained("original")
eq_model = sbm.EQTransformer.from_pretrained("original")

def to_stream(x,metadata,data):
	#print(x,metadata,data)

	st = Stream()
	for i,comp in enumerate(data.component_order):
		tr      = Trace()
		tr.data = x[i,:]
		tr.stats.network   = metadata.station_network_code
		tr.stats.station   = metadata.station_code
		tr.stats.starttime = metadata.trace_start_time
		tr.stats.channel   = metadata.station_instrument+comp
		tr.stats.sampling_rate = metadata.trace_sampling_rate_hz
		st += tr
	return st


# create plots for suspicious examples
def plot_(st,metadata,pn_picks,eq_picks,all_arrivals,all_phases):
	fig=plt.figure(figsize=(10,3))
	#for i,tr in enumerate(st):
	#	plt.plot(tr.normalize().data-i,linewidth=0.5,c='k')
	try:
		for k,phase in enumerate(all_phases):
			if phase=='P':
				plt.axvline(all_arrivals[k],c='r',label='P label',linewidth=3,alpha=0.5)
			if phase=='S':
				plt.axvline(all_arrivals[k],c='b',label='S label',linewidth=3,alpha=0.5)
		#plt.axvline(metadata.trace_P_arrival_sample,c='r',label='P label',linewidth=3)
		#plt.axvline(metadata.trace_S_arrival_sample,c='b',label='S label',linewidth=3)
	except Exception as e:
		print(e)
	
	for i,tr in enumerate(st):
		plt.plot(tr.normalize().data-i,linewidth=0.5,c='k')

	for position in pn_picks:
		plt.axvline(position,c='green',linestyle='--')
	for position in eq_picks:
		plt.axvline(position,c='orange',linestyle=':')
	plt.xlim(0,len(st[0].data))


	plt.title('CEED: '+st[0].id+' '+str(st[0].stats.starttime))
	plt.legend(loc='upper right')
	plt.yticks([])

	return fig


chunk_size=50000


for j in range(start_index*chunk_size,(start_index*chunk_size) + chunk_size):
	print(j)
	try:
		sample = train_generator[j]
		#print(sample['X'].shape)
		st    = to_stream(sample['X'],data.metadata.iloc[j],data)
		#sts.append(tst)

		#for j,st in enumerate(sts):
		print(st)
		# annotate and classify, compare to labels
		pn_picks = pn_model.classify(st,P_threshold=0.1,S_threshold=0.1)
		eq_picks = eq_model.classify(st,P_threshold=0.1,S_threshold=0.1)
		print(pn_picks.picks)

		# get the positions of the picks relateive to the trace tocompare to the metadata
		reftime=st[0].stats.starttime
		p_pos = [(pick.__dict__['peak_time'] - reftime)*st[0].stats.sampling_rate for pick in pn_picks.picks]
		s_pos = [(pick.__dict__['peak_time'] - reftime)*st[0].stats.sampling_rate for pick in eq_picks.picks]

		#print(pn_picks,eq_picks)
		#print(data.metadata.iloc[j])
		print(p_pos,s_pos)
		#print(data.metadata.iloc[j].trace_P_arrival_sample, data.metadata.iloc[j].trace_S_arrival_sample)


		# adpat to recover and plot all the available arrivals
		all_arrivals = data.metadata.iloc[j].trace_phase_time_list[1:-1].replace("'","").split()
		print(all_arrivals)
		all_arrivals = [UT(time) for time in all_arrivals]
		print(all_arrivals)
		all_arrivals = [(time - reftime)*data.metadata.iloc[j].trace_sampling_rate_hz  for time in all_arrivals]
		print(all_arrivals)
		all_phases   = data.metadata.iloc[j].trace_phase_type_list[1:-1].replace("'","").split() 

		print(all_phases,all_arrivals)

		# get some failure conditions to trigger plotting
		if len(p_pos)==0 and len(s_pos)==0:
			print('no arrivals')


			fig = plot_(st,data.metadata.iloc[j],p_pos,s_pos,all_arrivals,all_phases)
			
			outname = 'ceed_fp/ceed_'+str(j).rjust(7,'0')+'.pdf'
			plt.savefig(outname)
			plt.close()

	except Exception as e:
		print(e)

# read in some of the data


