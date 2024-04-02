import os
from obspy import read
import seisbench.models as sbm
import torch
import time

# Load the model
model = sbm.DeepDenoiser.from_pretrained("original")
device = torch.device("cuda")
model.to(device)

# Define the source and target directories
source_directory = 'C:/Users/Shadow/Downloads/mseed_volumes/mseed_volumes'
target_directory = 'C:/Users/Shadow/Downloads/mseed_volumes/denoised-volumes'

# Ensure the target directory exists
os.makedirs(target_directory, exist_ok=True)

# Get all miniseed files
mseed_files = [f for f in os.listdir(source_directory) if f.endswith('.mseed')]

# Sort files by their names
mseed_files.sort()

n_threads = os.cpu_count()
print("{} CPU Cores".format(n_threads))

torch.set_num_threads(n_threads-1)

t0 = time.time()
# Loop through each sorted file
for filename in mseed_files[0:1]:
    file_path = os.path.join(source_directory, filename)
    
    # Read the stream
    stream = read(file_path)
    print("Read File: {}".format(filename))

    # Apply the model to denoise
    denoised = model.annotate(stream, batch_size=256)

    # Edit Traces
    for trace in denoised:
        if 'DeepDenoiser_' in trace.stats.channel:
            trace.stats.channel = trace.stats.channel.replace('DeepDenoiser_', '')
    
    target_file_path = os.path.join(target_directory, filename)
    
    # Write denoised signals to the target directory
    denoised.write(target_file_path, format='MSEED')

    print(f'Processed and saved {filename}')

t1 = time.time()
print("total time: {}".format(t1-t0))
