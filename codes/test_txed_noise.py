

# get a consensus on the arrivals of known datasets, start by getting the aq2009 or the iquiaue dataset


import seisbench
import seisbench.data as sbd
import seisbench.models as sbm
import seisbench.generate as sbg

import matplotlib.pyplot as plt

from obspy import Stream, Trace
from obspy.core import UTCDateTime as UT

# The Iquique model is problematic because the traces are 
data = sbd.TXED()
data.metadata['split']='train'

print(data.metadata.columns)
md = data.metadata.copy()

n_len  = md[md['trace_category']=='noise']
print(n_len)


# the dev and test splits do not exist

train, dev, test = data.train_dev_test()
print(train,dev,test)


train_generator = sbg.GenericGenerator(train)
dev_generator = sbg.GenericGenerator(dev)
test_generateor = sbg.GenericGenerator(test)

pn_model = sbm.PhaseNet.from_pretrained("original")
eq_model = sbm.EQTransformer.from_pretrained("original")

def to_stream(x,metadata,data):
	#print(x,metadata,data)

	st = Stream()
	for i,comp in enumerate(data.component_order):
		tr      = Trace()
		tr.data = x[i,:]
		tr.stats.network   = 'TX'
		tr.stats.station   = metadata.station_code
		tr.stats.starttime = metadata.source_origin_time
		
		tr.stats.channel   = 'HH'+comp
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
	for position in pn_picks:
		plt.axvline(position,c='green',linestyle='--')
	for position in eq_picks:
		plt.axvline(position,c='orange',linestyle=':')

	plt.title('TXED noise: '+st[0].id+' '+str(st[0].stats.starttime))
	plt.xlim(0,len(st[0].data))
	plt.yticks([])

	plt.legend(loc='upper right')

	return fig

sts = []




for j in range(41000,len(n_len)):
	print(j)
	#try:
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
	#print(p_pos,s_pos)
	#print(data.metadata.iloc[j].trace_P_arrival_sample, data.metadata.iloc[j].trace_S_arrival_sample)

	# get some failure conditions to trigger plotting
	if len(p_pos)>0 and len(s_pos)>0:
		print(' arrivals in noise')


		fig = plot_(st,data.metadata.iloc[j],p_pos,s_pos)
		
		outname = 'txed_noise/txed_'+str(j).rjust(6,'0')+'.pdf'
		plt.savefig(outname)
		plt.close()

	#except Exception as e:
	#	print(e)

"""
for j in range(100):
	sample = train_generator[j]
	#print(sample['X'].shape)
	tst    = to_stream(sample['X'],data.metadata.iloc[j],data)
	sts.append(tst)

for j,st in enumerate(sts):
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
	print(data.metadata.iloc[j].trace_P_arrival_sample, data.metadata.iloc[j].trace_S_arrival_sample)

	# get some failure conditions to trigger plotting
	if len(p_pos)>2 and len(s_pos)>2:
		print('extra arrivals')


		fig = plot_(st,data.metadata.iloc[j],p_pos,s_pos)
		
		outname = 'pnw_'+str(j).rjust(5,'0')+'.pdf'
		plt.savefig(outname)
		plt.close()


# read in some of the data

"""
