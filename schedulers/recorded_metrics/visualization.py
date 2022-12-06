import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

cores=["2_cores","4_cores","8_cores"]
specs=["cfs_spec1","cfs_spec2","cfs_spec3"]

spec_map={
    "cfs_spec1": "High Def",
    "cfs_spec2": "Mod Def",
    "cfs_spec3": "Low Def"
}



def getRequestMetric(core,spec):
    path=f"./request_timeline/{spec}/{core}/metrics.info"
    x=pd.read_csv(path,header=None,names=["time","file_size","latency"])
    x=x[x.time!="total_count"]
    x.time=pd.to_datetime(x.time, unit='s', origin='unix')
    x.latency = x.latency.astype(np.float64)
    x.time=pd.to_timedelta(x.time-x.time.min())
    # x.time=str(pd.to_timedelta([x.time]).astype(np.int64)[0])
    return x

def getPreemptionMetric(core,spec):
    path=f"./preemption_timeline/{spec}/{core}/metrics.info"
    x=pd.read_csv(path,header=None,names=["pid","time"],dtype={"pid":int,"time":np.float64})
    # x.time=x.time.astype(np.datetime64_ns)
    # x.time=x.time/10**9
    x.time=pd.to_datetime(x.time, unit='ns', origin='unix')
    x=x.set_index("time")
    x['Refusals']=1
    x=x.drop(columns=['pid'])
    x = x.groupby(pd.Grouper(freq='s')).sum()
    x=x.reset_index()
    min=x.time.min()
    x=x.set_index("time")
    return x,min


fig=plt.figure(figsize=(12,12))
fig_i=1
fig.suptitle("API Response latencies", fontsize=15)
for core in cores:
    for spec in specs:
        ax_plt = fig.add_subplot(3, 3, fig_i)
        request_core=getRequestMetric(core, spec)

        sns.lineplot(data=request_core,x="time",y="latency",hue="file_size").set_title(f"{spec_map[spec]} {core}")
        print(f"Min Latency {spec} {core}", request_core.latency.min())
        print(f"Max Latency {spec} {core}", request_core.latency.max())
        print(f"Average Latency {spec} {core}", request_core.latency.mean())
        fig_i+=1
plt.tight_layout()
# plt.show()
plt.savefig("API_Response_Latencies.png")

fig_i = 0
fig_j = 0

fig, axes = plt.subplots(nrows=3, ncols=3)
fig.suptitle("Preemption  refusal timeline", fontsize=15)

for core in cores:
    for spec in specs:
        preemption_core,min_time=getPreemptionMetric(core, spec)
        def fix_xticks_preempt(label):
            if (label - min_time).seconds%5!=0:
                return ""
            return (label - min_time).seconds
        ax=preemption_core.plot(kind='bar', width=1, rot=0,ax=axes[fig_i,fig_j],title=f"{spec_map[spec]} {core}")
        # plt.bar(preemption_core.index,preemption_core.Refusals,width=1)
        ax.set_xticklabels(map(fix_xticks_preempt, preemption_core.index))
        fig_j+=1
        if fig_j==3:
            fig_i+=1
            fig_j=0

plt.tight_layout()
# plt.show()
plt.savefig("Refusal_timeline.png")


fig=plt.figure(figsize=(12,12))
fig_i=1
fig.suptitle("API Response latencies(CFS)", fontsize=15)
for core in cores:
    ax_plt = fig.add_subplot(3, 1, fig_i)
    request_core=getRequestMetric(core,"cfs")
    sns.lineplot(data=request_core,x="time",y="latency",hue="file_size").set_title(f"CFS {core}")
    print(f"Min Latency CFS {core}",request_core.latency.min())
    print(f"Max Latency CFS {core}",request_core.latency.max())
    print(f"Average Latency CFS {core}",request_core.latency.mean())

    fig_i+=1
plt.tight_layout()
# plt.show()
plt.savefig("CFS_Latencies.png")


data_8_cfs=getRequestMetric("8_cores","cfs")
data_8_cfs_spec1=getRequestMetric("8_cores","cfs_spec1")


mapping={
    "1k":1,
    "2k":2,
    "4k":3,
    "10k":4,
    "50k":5,
    "100k":6,
    "500k":7,
    "1m":8,
    "2m":9
}

fig, axes = plt.subplots(nrows=2, ncols=1)
data_8_cfs=data_8_cfs.groupby(by=["file_size"]).max().reset_index()
key = data_8_cfs['file_size'].map(mapping)
data_8_cfs=data_8_cfs.iloc[key.argsort()]
data_8_cfs = data_8_cfs.drop(columns=['time'])
data_8_cfs.plot(kind="bar",x="file_size",ax=axes[0], title="Average Latency by file size (CFS) 8-core")



data_8_cfs_spec1=data_8_cfs_spec1.groupby(by=["file_size"]).max().reset_index()
key = data_8_cfs_spec1['file_size'].map(mapping)
data_8_cfs_spec1=data_8_cfs_spec1.iloc[key.argsort()]
data_8_cfs_spec1 = data_8_cfs_spec1.drop(columns=['time'])

data_8_cfs_spec1.plot(kind="bar",x="file_size",ax=axes[1],title="Average Latency by file size (High Defiance) 8-core")

plt.tight_layout()
# plt.show()
plt.savefig("Latency_by_file_size.png")
