import argparse
import json
from datetime import datetime
from tools import getOMSAPI, getAppSecret, getOMSdata

# Set up argument parser
parser = argparse.ArgumentParser(description='Script to fetch and save detailed lumisection and stream data')
parser.add_argument('--run', type=int, help='Run number')
parser.add_argument('--fill', type=int, help='Fill number')
parser.add_argument('--lsMin', type=int, default=1, help='Minimum lumisection')
parser.add_argument('--lsMax', type=int, default=9999, help='Maximum lumisection')
parser.add_argument('--output', type=str, default='detailed_stream_data.json', help='Output JSON file')
args = parser.parse_args()

if not args.run and not args.fill:
    parser.error('Either --run or --fill must be provided.')
elif args.run and args.fill:
    parser.error('Please provide only one of --run or --fill, not both.')

omsapi = getOMSAPI(getAppSecret())
PAGE_LIMIT = 10000
LS_LENGTH = 2**18 / 11245.5  # 23.31 s

# Function to get all runs in a fill
def getFillRuns(omsapi, fillNumber):
    q = omsapi.query("lumisections")
    q.filter("fill_number", fillNumber)
    q.custom("fields", "physics_flag,beam1_stable,beam2_stable,run_number")
    q.per_page = PAGE_LIMIT
    data = q.data().json()['data']
    return list({item['attributes']['run_number'] for item in data if item['attributes']['physics_flag'] and item['attributes']['beam1_stable'] and item['attributes']['beam2_stable']})

# Function to get min/max lumisections for a run
def getMinMaxLS(omsapi, run):
    q = omsapi.query("lumisections")
    q.filter("run_number", run)
    q.custom("fields", "lumisection_number")
    q.per_page = PAGE_LIMIT
    data = q.data().json()['data']
    
    minLS = min(item['attributes']['lumisection_number'] for item in data)
    maxLS = max(item['attributes']['lumisection_number'] for item in data)
    return minLS, maxLS

def getDeadtime(omsapi, run, minLS, maxLS):
    data = getOMSdata(omsapi, "lumisections", 
        attributes=['delivered_lumi_per_lumisection', 'recorded_lumi_per_lumisection', 'lumisection_number'],
        filters={"run_number": [run], "lumisection_number": [minLS, maxLS]},
        verbose=False
    )

    deadtime_data = {}
    for row in data:
        if 'attributes' not in row:
            print(f"Warning: Missing 'attributes' key in lumisection response: {row}")
            continue

        attr = row['attributes']
        ls_number = attr.get('lumisection_number')
        delivered_lumi = attr.get('delivered_lumi_per_lumisection', 0)
        recorded_lumi = attr.get('recorded_lumi_per_lumisection', 0)

        if ls_number is None:
            print(f"Warning: Missing 'lumisection_number' in lumi data: {attr}")
            continue

        if delivered_lumi > 0:
            deadtime = 1 - (recorded_lumi / delivered_lumi)
        else:
            deadtime = 0.0  # If delivered lumi is 0, deadtime is undefined; assume 0

        deadtime_data[ls_number] = deadtime

    return deadtime_data

# Function to get HLT rate for `Status_OnGPU`
def getHLTRate(omsapi, run, minLS, maxLS):
    data = getOMSdata(omsapi, "hltpathrates",
        attributes=["counter", "last_lumisection_number"],
        filters={"run_number": [run], "first_lumisection_number": [minLS, None], "last_lumisection_number": [None, maxLS], "path_name": ["Status_OnGPU"]},
        max_pages=PAGE_LIMIT
    )
    return {row['attributes']['last_lumisection_number']: row['attributes']['counter'] / LS_LENGTH for row in data}

# Function to get detailed lumisection data
def getLumisectionDetails(omsapi, run, minLS, maxLS):
    data = getOMSdata(omsapi, "lumisections",
                      attributes=['delivered_lumi_per_lumisection', 'run_number', 'lumisection_number', 'start_time', 'pileup'],
                      filters={"run_number": [run], "lumisection_number": [minLS, maxLS]},
                      max_pages=5000)
    
    lumisection_details = {}
    for row in data:
        ls_number = row['attributes']['lumisection_number']
        lumisection_details[ls_number] = row['attributes']

        # Convert start time to Unix timestamp
        dtime = row['attributes']['start_time']
        date, time = dtime.split('T')
        yy, mm, dd = map(int, date.split('-'))
        HH, MM, SS = map(int, time[:-1].split(':'))
        lumisection_details[ls_number]['time'] = int(datetime(yy, mm, dd, HH, MM, SS).timestamp())

    return lumisection_details

# Function to get stream data
def getStreamData(omsapi, run, lumisection_details, minLS, maxLS):
    StreamData = {}
    
    for LS in range(minLS, maxLS + 1):
        q = omsapi.query("streams")
        q.per_page = 100
        q.filter("run_number", run)
        q.filter("last_lumisection_number", LS)
        q.custom("fields", "last_lumisection_number,rate,file_size,bandwidth,stream_name")
        response = q.data().json()['data']
        
        if not response:
            continue

        for item in response:
            stream_name = item['attributes']['stream_name']
            ls_number = item['attributes']['last_lumisection_number']

            if stream_name not in StreamData:
                StreamData[stream_name] = []

            stream_entry = {
                'LS': ls_number,
                'rate': item['attributes']['rate'],
                'size': item['attributes']['file_size'] * 1e9,  # Convert GB to bytes
                'bandwidth': item['attributes']['bandwidth'] * 1e6,  # Convert MB/s to bits/s
            }

            # Add lumisection details
            stream_entry.update(lumisection_details.get(ls_number, {}))

            # Add deadtime and HLT rate of Status_OnGPU
            stream_entry['deadtime'] = deadtime_data.get(ls_number, 0.0)
            stream_entry['hlt_rate_Status_OnGPU'] = hlt_rate_data.get(ls_number, 0.0)

            StreamData[stream_name].append(stream_entry)

    return StreamData

# Main logic
if args.fill:
    runs = getFillRuns(omsapi, args.fill)
else:
    runs = [args.run]

all_stream_data = {}

for run in runs:
    print(f"Processing run: {run}")

    # Get lumisection range
    minLS, maxLS = getMinMaxLS(omsapi, run)

    # Fetch lumisection details
    lumisection_details = getLumisectionDetails(omsapi, run, minLS, maxLS)

    # Fetch deadtime data
    deadtime_data = getDeadtime(omsapi, run, minLS, maxLS)

    # Fetch HLT rate data for Status_OnGPU
    hlt_rate_data = getHLTRate(omsapi, run, minLS, maxLS)

    # Fetch stream data
    stream_data = getStreamData(omsapi, run, lumisection_details, minLS, maxLS)

    # Store results
    all_stream_data[run] = stream_data

# Save to JSON file
with open(args.output, 'w') as json_file:
    json.dump(all_stream_data, json_file, indent=4)

print(f"Detailed stream data saved to {args.output}")
