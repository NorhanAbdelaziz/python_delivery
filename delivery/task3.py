import os
import fnmatch
import json
import pandas as pd 
from pandas.io.json import json_normalize 
from subprocess import PIPE, Popen
from os import listdir
from os.path import isfile, join
import argparse

#command line automation process
#pass directory as an argument
parser = argparse.ArgumentParser()
parser.add_argument("directory",help="Enter the directory where your files locate")
parser.add_argument("-u", "--unix", action="store_true", dest="unix", default=False, help="maintain the UNIX format of timpe stamp ")
args = parser.parse_args()

#save arg in variable dir
dir = args.directory

#check for identicale files
files = [item for item in listdir(dir) if isfile(join(dir, item))]
checksums = {}
duplicates = []
for filename in files:
    
    with Popen(["md5sum", filename], stdout=PIPE) as proc:
        checksum = proc.stdout.read().split()[0]
        if checksum in checksums:
            print(filename)
            os.remove(filename)
            #remove one of identical files
            duplicates.append(filename)
        checksums[checksum] = filename

#list all files inside directory
items = os.listdir(dir)
count = 0
for item in items:
	#specify only json files
    if fnmatch.fnmatch(item, '*.json'):
        count +=1
        fullpath = dir+'/'+item
        data = [json.loads(line) for line in open(fullpath)]
        #load json file as dataframe
        df = json_normalize(data)
        #the columns we will use
        df = df[['a','r','u','ll','t','hc','tz','cy']]
        #get rid of NaNs value
        df = df.dropna()
        #some cleansing work
        df['web_browser']=df.a.str.split(expand=True)[0]
        df['operating_sys']= df.a.str.split('(',expand=True)[1].str.split(';',expand=True)[0]
        df['from_url'] = df.r.str.replace('//','/').str.split('/',expand=True)[1]
        df.from_url.fillna(df.r, inplace=True)
        df['to_url'] = df.u.str.replace('//','/').str.split('/',expand=True)[1]
        df.from_url.fillna(df.u, inplace=True)
        df[['longitude','latitude']]= pd.DataFrame(df.ll.tolist(), index= df.index)
        df.rename(columns = {'cy' : 'city', 'tz' : 'time_zone', 't' : 'time_in_unix', 'hc' : 'time_out_unix'}, inplace = True)
        # If the count arg is evaluated to true (default is False)

        if args.unix:
        	# You will add unix timestamp
        	df_new = df[['web_browser', 'operating_sys',
        	'from_url','to_url','city','longitude','latitude','time_zone','time_in_unix','time_out_unix']].copy()
        #else will add datetime
        else:
        	df_new = df[['web_browser', 'operating_sys',
        	'from_url','to_url','city','longitude','latitude','time_zone']].copy()
        	df_new['time_in'] = pd.to_datetime(df['time_in_unix'],unit='s')
        	df_new['time_out'] = pd.to_datetime(df['time_out_unix'],unit='s')
        
        #messages to user
        output_path = dir+'/target/output_file'+str(count)+'.csv'
        print('number of lines in this file = '+str(len(df.index)+1))
        print('Wrote in '+output_path)

        #write dataframes to csv files   
        df_new.to_csv(output_path)



