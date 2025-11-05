

# get a consensus on the arrivals of known datasets, start by getting the aq2009 or the iquiaue dataset

# go over the noise samples, in case there are any picked arrivals flag it

import seisbench
import seisbench.data as sbd
import seisbench.models as sbm
import seisbench.generate as sbg

import matplotlib.pyplot as plt
plt.rcParams['font.family']='helvetica'


from obspy import Stream, Trace


# The Iquique model is problematic because the traces are 
data = sbd.STEAD()
data.metadata['type']=data.metadata['trace_name_original'].str[-2:]
print(data.metadata['type'])

md = data.metadata.copy()
print(md[md['type']=='NO'])
#print(len(data.metadata))

#overwrite the splits
data.metadata['split']='train'


train, dev, test = data.train_dev_test()

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
		tr.stats.channel   = metadata.trace_channel[:2]+comp
		tr.stats.sampling_rate = metadata.trace_sampling_rate_hz
		st += tr
	return st


# create plots for suspicious examples
def plot_(st,metadata,pn_picks,eq_picks):
	fig=plt.figure(figsize=(10,3))
	for i,tr in enumerate(st):
		plt.plot(tr.normalize().data-i,linewidth=0.5,c='k')
	try:
		plt.axvline(metadata.trace_p_arrival_sample,c='r',label='P label',linewidth=3)
		plt.axvline(metadata.trace_s_arrival_sample,c='b',label='S label',linewidth=3)
	except Exception as e:
		print(e)
	for position in eq_picks:
		plt.axvline(position,c='orange',linestyle='--')
	for position in pn_picks:
		plt.axvline(position,c='green',linestyle=':')
	plt.xlim(0,len(st[0].data))

	plt.title('STEAD noise: '+st[0].id+' '+str(st[0].stats.starttime))
	plt.legend(loc='upper right')
	plt.yticks([])

	return fig

sts = []






for j in range(1601000):
	try:
		sample = train_generator[j]
		#print(sample['X'].shape)
		st    = to_stream(sample['X'],data.metadata.iloc[j],data)
		#sts.append(tst)

		#for j,st in enumerate(sts):
		print(st)
		# annotate and classify, compare to labels
		pn_picks = pn_model.classify(st,P_threshold=0.4,S_threshold=0.4)
		eq_picks = eq_model.classify(st,P_threshold=0.4,S_threshold=0.4)
		print(pn_picks.picks)

		# get the positions of the picks relateive to the trace tocompare to the metadata
		reftime=st[0].stats.starttime
		p_pos = [(pick.__dict__['peak_time'] - reftime)*st[0].stats.sampling_rate for pick in pn_picks.picks]
		s_pos = [(pick.__dict__['peak_time'] - reftime)*st[0].stats.sampling_rate for pick in eq_picks.picks]

		#print(pn_picks,eq_picks)
		#print(data.metadata.iloc[j])
		print(p_pos,s_pos)
		print(data.metadata.iloc[j].trace_p_arrival_sample, data.metadata.iloc[j].trace_s_arrival_sample)

		# get some failure conditions to trigger plotting
		event_type = data.metadata.iloc[j]['trace_name_original'][-2:]
		print(j,event_type)

		# PhaseNet is producing too many false positives, 
		if event_type=='NO' and len(p_pos)>0 and len(s_pos)>0: #or (event_type=='NO' and len(p_pos)>=2):
			print(' arrivals in noise sample')


			fig = plot_(st,data.metadata.iloc[j],p_pos,s_pos)
			
			outname = 'stead_noise/stead_'+str(j).rjust(7,'0')+'.pdf'
			plt.savefig(outname)
			plt.close()
	except Exception as e:
		print(e)

# read in some of the data


