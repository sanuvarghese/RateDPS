# RateDPS
scripts used to produce the plots in the HLT rates DPS note

# Setup

First you need to install OMS api in a separate folder according to instructions in https://github.com/silviodonato/OMSRatesNtuple/tree/main/OMS_ntuplizer

then git clone

```
 git clone https://github.com/sanuvarghese/RateDPS.git
```

Once its installed, go the ```OMS_query``` directory and run the get_stream_info.py script  with the desired fill number

```
get_stream_info.py --fill 10116 --output fill_10116.json
```

this will produce a json file with all the needed info.

# Plotting

Now go the ```Plotter``` directory and download/copy the  the json file

eg: 

```
wget https://savarghe.web.cern.ch/RateFilljsons/fill_10116.json
```

and then go through the notebooks.
