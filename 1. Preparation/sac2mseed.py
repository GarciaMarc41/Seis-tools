# Marc Garcia
# import libraries 
# 3 days 7.5 mins/ 6 months 7.5 hours 
import glob
import numpy as np 
from obspy import read, UTCDateTime
import time


# where data is stored
data_dir = '/nfs/data/isml/Projects/Mexico_Data/Raw_Data'

# output data
out_dir = '/nfs/data/isml/Marc/PhaseNet/working_dataset/data'

# stations to be formated
sta_list_perm = ['CCIG','CMIG','HLIG','HUIG','OXIG','PCIG','PEIG','PNIG','TGIG','THIG','TLIG','TOIG','TUIG','TXIG','YOIG']
sta_list_temp = ['A01','A03','A04','B01','B02','B03','B04','B05','B06','B07','B08','B09','B10']

# channels to use
chan_str = 'HH?'

# start and end time of the data.
data_start_time = UTCDateTime('2017-10-15T00:00:00')
data_end_time = UTCDateTime('2017-10-18T00:00:00')

# length of a file
file_length = 3600

# begin iteration
file_start_time = data_start_time
file_end_time = file_start_time + file_length
st = False


while file_end_time <= data_end_time:
    # search for permanet stations
    for a_sta in sta_list_perm:
        search_perm = '{0}/{1}/*{3}*'.format(data_dir, a_sta, file_start_time.strftime('%Y%m%d'), chan_str)
        file_list = glob.glob(search_perm)

        if len(file_list) > 0:
            st_perm1 = read(search_perm, starttime=file_start_time, endtime=file_end_time)
            st_perm = st_perm1.merge(fill_value=0)
            st_perm.filter('highpass', freq=5.0, zerophase=False)
           
            if st:
                st1 = st + st_perm
            else:
                st1 = st_perm  
            st = st1

    # search for temporary stations        
    for a_sta in sta_list_temp:
        search_temp = '{0}/{1}/{1}*{3}*{2}'.format(data_dir, a_sta, file_start_time.strftime('%Y.%j'), chan_str)
        file_list2 = glob.glob(search_temp)

        if len(file_list2) > 0:
            st_temp1 = read(search_temp, starttime=file_start_time, endtime=file_end_time)
            st_temp = st_temp1.merge(fill_value=0)
            st_temp.filter('highpass', freq=5.0, zerophase=False)
           
            if st:
                st2 = st + st_temp
            else:
                st2 = st_temp   
            st = st2
               

    # write files
    if st:
        st.write('{0}/{1}.mseed'.format(out_dir, file_start_time.strftime('%Y-%m-%dT%H-%M-%S')), format='MSEED')

    # restart interation
    file_start_time = file_end_time
    file_end_time = file_start_time + file_length
    st = False


