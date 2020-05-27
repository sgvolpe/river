import io, matplotlib
import matplotlib.pyplot as pp
import numpy as np
import pandas as pd
import pymc as pm
import folium

# Statistics
def column_value_perc(df, col):
    return df[col].value_counts(normalize=True)

def sample_dist(brown=.51, n=1000):
    return pd.DataFrame({'vote': np.where(np.random.rand(n) < brown, 'Brown', 'Green')})


def sampling_dist(brown=.51, n=1000):
    dist = pd.DataFrame([sample_dist(brown, n).vote.value_counts(normalize=True) for i in range(1000)])
    dist.Brown.hist(histtype='step', bins=20)
    return dist


def quantiles(brown=.51, n=1000):
    dist = sample_dist(brown, n)
    return dist.Brown.quantile(0.025), dist.Brown.quantile(0.975)


def bootstrap(pop):
    boot_df = pd.DataFrame({'mean': pop.sample(100, replace=True).grade().mean() for i in range(1000)})
    return boot_df


def london_chart():

    img = matplotlib.image.imread('london.png')
    pp.figure(figsize=(10, 10))
    pp.imshow(img, extent=[-0.38, 0.38, -0.38, 0.38])
    pp.scatter(pumps.x, pumps.y, color='b')
    pp.scatter(cholera,x, cloera.y, color='r', s=3)


def get_map():
    m = folium.Map(location=[x,y],zoom_start=15)

def timer_loop(a):
    pass
    #%timeit -n $ntimes polyn(1000)