import os
import obspy
from obspy import read
import seisbench.models as sbm

def process_file(filename, source_directory, target_directory, model):
    try:
        print("Starting Process")
        file_path = os.path.join(source_directory, filename)
        stream = read(file_path)
        denoised = model.annotate(stream)

        for trace in denoised:
            if 'DeepDenoiser_' in trace.stats.channel:
                trace.stats.channel = trace.stats.channel.replace('DeepDenoiser_', '')

        target_file_path = os.path.join(target_directory, filename)
        denoised_stream = obspy.Stream(traces=denoised)
        denoised_stream.write(target_file_path, format='MSEED')
        print(f'Processed and saved {filename}')
    except Exception as e:
        print(f'Error processing {filename}: {e}')

