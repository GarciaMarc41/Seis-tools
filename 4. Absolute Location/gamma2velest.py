# Author: Marc Garcia
# Convert GaMMA Association to Velest format CNV
# Import Libriares
from obspy.core.event import Catalog, Event, Origin, Magnitude, Pick, WaveformStreamID
from obspy.core import UTCDateTime
from obspy.core.event import ResourceIdentifier
import pandas as pd

# Read the CSV files
picks = pd.read_csv('/Users/marcgarcia/Research/Association/RAPID/m2/working/picks_gmma.csv', sep="\t")
events = pd.read_csv('/Users/marcgarcia/Research/Association/RAPID/m2/working/catalog_gamma.csv', sep="\t")

# %%
events["match_id"] = events["event_index"].astype(str)
picks["match_id"] = picks["event_index"].astype(str)
# Filter out events with 0 depth
events = events[events['depth(m)'] > 5000]

# Initialize an empty catalog
catalog = Catalog()

# Loop through the events dataframe to create Event objects
for index, row in events.iterrows():
    # Create an Origin object for the event
    origin = Origin()
    origin.time = UTCDateTime(row['time'])
    origin.latitude = row['latitude']
    origin.longitude = row['longitude']
    origin.depth = row['depth(m)']   # Assuming depth is in meters
    origin.resource_id = ResourceIdentifier(id=str(row['event_index']))

    # Create a Magnitude object for the event
    magnitude = Magnitude()
    magnitude.mag = row['magnitude']
    magnitude.resource_id = ResourceIdentifier(id=str(row['event_index']))

    # Create an Event object and associate the Origin and Magnitude
    event = Event()
    event.origins = [origin]
    event.magnitudes = [magnitude]
    event.resource_id = origin.resource_id

    # Loop through the picks dataframe to create Pick objects for this event
    event_picks = picks[picks['match_id'] == str(row['event_index'])]
    for _, pick_row in event_picks.iterrows():
        network, station, location, _ = pick_row['station_id'].split('.')

        # Determine the phase type and set the component accordingly
        phase_type = pick_row['phase_type']
        components = []
        if phase_type == 'P':
            components.append('HHZ')  # For 'P' picks, use HHZ component
        elif phase_type == 'S':
            components.extend(['HHE', 'HHN'])  # For 'S' picks, duplicate for HHE and HHN components

        for component in components:
            waveform_id = WaveformStreamID(network_code=network, station_code=station, location_code=location, channel_code=component)
            
            pick = Pick()
            pick.time = UTCDateTime(pick_row['phase_time'])
            pick.phase_hint = phase_type
            pick.waveform_id = waveform_id
            pick_id = f"{row['event_index']}-{pick_row['phase_time']}-{component}"
            pick.resource_id = ResourceIdentifier(id=pick_id)

            # Here we simulate incorporating the phase_score into the pick's time_errors.uncertainty
            phase_score = pick_row['phase_score']
            pick.time_errors = {'uncertainty': phase_score}  # Storing the original phase_score as uncertainty

            # Append the Pick to the event
            event.picks.append(pick)

    # Add the event to the catalog
    catalog.events.append(event)

# Define phase mapping if the default is not suitable
phase_mapping = {
    'p': 'P', 'P': 'P', 'Pg': 'P', 'Pn': 'P', 'Pm': 'P',
    's': 'S', 'S': 'S', 'Sg': 'S', 'Sn': 'S', 'Sm': 'S'
}

# Define weight mapping based on your pick uncertainties
weight_mapping = [0.25, 0.50, 0.75]

# List of events to fix the y-coordinate in the hypocenter (optional)
ifx_list = [ResourceIdentifier(id="..."), ...]  # Replace with actual event IDs if needed

# Default weight for picks without timing uncertainty
default_weight = 1

# Now call the write method with the CNV format and additional parameters
catalog.write('/Users/marcgarcia/Research/Relocation/velest/velest/mex_rapid/input_catalog.cnv', format='CNV',
              phase_mapping=phase_mapping,
              weight_mapping=weight_mapping,
              ifx_list=ifx_list,
              default_weight=default_weight)

print(f"Catalog contains {len(catalog)} events.")
