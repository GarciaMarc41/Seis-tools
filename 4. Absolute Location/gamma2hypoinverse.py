# Import Libriares
from datetime import datetime

import numpy as np
import pandas as pd
from tqdm import tqdm

# Read the CSV files
picks = pd.read_csv('/Users/marcgarcia/Research/Association/RAPID/m1/working/picks_gmma.csv', sep="\t")
events = pd.read_csv('/Users/marcgarcia/Research/Association/RAPID/m1/working/catalog_gamma.csv', sep="\t")


# %%
events["match_id"] = events["event_index"].astype(str)
picks["match_id"] = picks["event_index"].astype(str)

# %%
out_file = open("/Users/marcgarcia/Research/Relocation/hyp1.40/RAPID/RAPID/m1/hypoInput.arc", "w")

picks_by_event = picks.groupby("match_id").groups

for i in tqdm(range(len(events))):

    event = events.iloc[i]
    event_time = datetime.strptime(event["time"], "%Y-%m-%dT%H:%M:%S.%f").strftime("%Y%m%d%H%M%S%f")[:-4]
    lat_degree = int(event["latitude"])
    lat_minute = (event["latitude"] - lat_degree) * 60 * 100
    south = "S" if lat_degree <= 0 else " "
    lng_degree = int(event["longitude"])
    lng_minute = (event["longitude"] - lng_degree) * 60 * 100
    east = "E" if lng_degree >= 0 else " "
    depth = event["depth(m)"] / 1e3 * 100
    magnitude = event['magnitude']
    magnitude_str = f"{magnitude:4.1f}"
    event_line = f"{event_time}{abs(lat_degree):2d}{south}{abs(lat_minute):4.0f}{abs(lng_degree):3d}{east}{abs(lng_minute):4.0f}{depth:5.0f} {magnitude:3.1f}"
    out_file.write(event_line + "\n")

    picks_idx = picks_by_event[event["match_id"]]
    for j in picks_idx:
        pick = picks.iloc[j]
        network_code, station_code, comp_code, channel_code = pick['station_id'].split('.')
        phase_type = pick['phase_type']
        phase_weight = min(max(int((1 - pick['phase_score']) / (1 - 0.3) * 4) - 1, 0), 3)
        phase_amp = int(pick['phase_amp'] * 1e9 * 10)  # Convert to 0.1 nm
        phase_amp_str = f"{phase_amp:6d}" if phase_amp < 999999 else "999999"  # Limit to 6 characters
        pick_time = datetime.strptime(pick["phase_time"], "%Y-%m-%dT%H:%M:%S.%f")
        phase_time_minute = pick_time.strftime("%Y%m%d%H%M")
        phase_time_second = pick_time.strftime("%S%f")[:-4]
        tmp_line = f"{station_code:<5}{network_code:<2} {comp_code:<1}{channel_code:<3}"
        
        if phase_type.upper() == 'P':
            pick_line = f"{tmp_line:<13} P {phase_weight:<1d}{phase_time_minute} {phase_time_second}   {phase_amp_str}"
        elif phase_type.upper() == 'S':
            pick_line = f"{tmp_line:<13}   4{phase_time_minute} {'':<12}{phase_time_second} S {phase_weight:<1d} {phase_amp_str}"
        else:
            raise (f"Phase type error {phase_type}")
        out_file.write(pick_line + "\n")

    out_file.write("\n")
    if i > 1e5:
        break

out_file.close()
