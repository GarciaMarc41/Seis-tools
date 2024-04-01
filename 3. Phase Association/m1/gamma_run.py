# import libriaries
import pandas as pd
from datetime import datetime, timedelta
from gamma import BayesianGaussianMixture, GaussianMixture
from gamma.utils import convert_picks_csv, association, from_seconds, estimate_station_spacing
import numpy as np
from sklearn.cluster import DBSCAN 
from datetime import datetime, timedelta
import os
import json
import pickle
from pyproj import Proj
from tqdm import tqdm
import time

if __name__ == '__main__':
    from multiprocessing import freeze_support, Manager
    freeze_support()

    # configurations
    data_dir = lambda x: os.path.join("working", x)
    station_csv = data_dir("mexico_stations.csv")
    pick_json = data_dir("picks_m1.json")
    catalog_csv = data_dir("catalog_gamma.csv")
    picks_csv = data_dir("picks_gmma.csv")
    if not os.path.exists("figures"):
        os.makedirs("figures")
    figure_dir = lambda x: os.path.join("figures", x)

    config = {'center': (-95.3516, 16.3274), 
        'xlim_degree': [-99.5665, -91.1368], 
        'ylim_degree': [13.5593, 19.0956], 
        'degree2km': 106.659, 
        'starttime': datetime(2017, 9, 1, 0, 0), 
        'endtime': datetime(2017, 10, 1, 0, 0)}

    ## read picks
    picks = pd.read_json(pick_json)
    picks["station_id"] = picks["id"]
    picks["phase_time"] = picks["timestamp"]
    picks["phase_amp"] = picks["amp"]
    picks["phase_type"] = picks["type"]
    picks["phase_score"] = picks["prob"]

    ## read stations
    stations = pd.read_csv(station_csv, delimiter="\t")
    stations = stations.rename(columns={"station":"id"})
    proj = Proj(f"+proj=sterea +lon_0={config['center'][0]} +lat_0={config['center'][1]} +units=km")
    stations[["x(km)", "y(km)"]] = stations.apply(lambda x: pd.Series(proj(x["longitude"], x["latitude"])), axis=1)
    stations["z(km)"] = stations["elevation(m)"].apply(lambda x: -x/1e3)

    ### setting GMMA configs
    config["use_dbscan"] = True
    config["use_amplitude"] = True
    config["method"] = "BGMM"  
    if config["method"] == "BGMM": ## BayesianGaussianMixture
        config["oversample_factor"] = 8
    if config["method"] == "GMM": ## GaussianMixture
        config["oversample_factor"] = 1

    # earthquake location
    #config["vel"] = {"p": 6.0, "s": 6.0 / 1.75}
    config["dims"] = ['x(km)', 'y(km)', 'z(km)']
    config["x(km)"] = (np.array(config["xlim_degree"])-np.array(config["center"][0]))*config["degree2km"]
    config["y(km)"] = (np.array(config["ylim_degree"])-np.array(config["center"][1]))*config["degree2km"]
    config["z(km)"] = (0,350)
    config["bfgs_bounds"] = (
        (config["x(km)"][0] - 2, config["x(km)"][1] + 2),  # x
        (config["y(km)"][0] - 2, config["y(km)"][1] + 2),  # y
        (0, config["z(km)"][1] + 2),  # z
        (None, None),  # t
    )   

    # DBSCAN
    config["dbscan_eps"] = 80
    config["dbscan_min_samples"] = 3

     ## Eikonal for 1D velocity model
    zz = [0.00, 1.00, 2.00, 3.00, 4.00, 5.00, 7.00, 10.0, 14.0, 18.0, 20.0, 23.0, 25.0, 28.0, 33.0, 36.0, 38.0, 50, 100, 150, 300]
    vp = [4.81, 5.00, 5.11, 5.34, 5.87, 6.15, 6.17, 6.18, 6.24, 6.45, 6.92, 6.92, 7.30, 7.41, 7.74, 7.80, 7.81, 7.99, 8.27, 8.60, 8.90]
    vp_vs_ratio = 1.73
    vs = [v / vp_vs_ratio for v in vp]
    h = 0.3
    h = 3
    vel = {"z": zz, "p": vp, "s": vs}
    config["eikonal"] = {"vel": vel, "h": h, "xlim": config["x(km)"], "ylim": config["y(km)"], "zlim": config["z(km)"]}


    # filtering
    config["min_picks_per_eq"] = 5
    config["min_p_picks_per_eq"] = 3
    config["min_s_picks_per_eq"] = 2
    config["max_sigma11"] = 2.0 # s
    config["max_sigma22"] = 1.0 # log10(m/s)
    config["max_sigma12"] = 1.0 # covariance

    ## filter picks without amplitude measurements
    if config["use_amplitude"]:
        picks = picks[picks["amp"] != -1]

    for k, v in config.items():
        print(f"{k}: {v}")

    # association with GaMMA
    start_time = time.time()
    event_idx0 = 0 ## current earthquake index
    assignments = []
    catalogs, assignments = association(picks, stations, config, event_idx0, config["method"])
    event_idx0 += len(catalogs)

    ## create catalog
    catalogs = pd.DataFrame(catalogs, columns=["time"]+config["dims"]+["magnitude", "sigma_time", "sigma_amp", "cov_time_amp",  "event_index", "gamma_score"])
    catalogs[["longitude","latitude"]] = catalogs.apply(lambda x: pd.Series(proj(longitude=x["x(km)"], latitude=x["y(km)"], inverse=True)), axis=1)
    catalogs["depth(m)"] = catalogs["z(km)"].apply(lambda x: x*1e3)
    with open(catalog_csv, 'w') as fp:
        catalogs.to_csv(fp, sep="\t", index=False, 
                        float_format="%.3f",
                        date_format='%Y-%m-%dT%H:%M:%S.%f',
                        columns=["time", "magnitude", "longitude", "latitude", "depth(m)", "sigma_time", "sigma_amp", "cov_time_amp", "event_index", "gamma_score"])
    # catalogs = catalogs[['time', 'magnitude', 'longitude', 'latitude', 'depth(m)', 'sigma_time', 'sigma_amp', 'gamma_score']]

    ## add assignment to picks
    assignments = pd.DataFrame(assignments, columns=["pick_index", "event_index", "gamma_score"])
    picks = picks.join(assignments.set_index("pick_index")).fillna(-1).astype({'event_index': int})
    with open(picks_csv, 'w') as fp:
        picks.to_csv(fp, sep="\t", index=False, 
                        date_format='%Y-%m-%dT%H:%M:%S.%f',
                        columns=["station_id", "phase_time", "phase_type", "phase_score", "phase_amp", "event_index", "gamma_score"])

    print(f"Total time: {time.time() - start_time} seconds")




