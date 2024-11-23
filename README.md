ZappiToInflux
===========

https://github.com/GavinLucas/ZappiToInflux
-----------------------------------------

Script to take data from a MyEnergi Zappi and post it to InfluxDB in order to view the data in Grafana.

To run the script:
- copy settings.json.example to settings.json
  - Change the permissions of the file, e.g. `chmod 600 settings.json`, so that it's not readable 
  by other users
  - Fill in the values for your Zappi and InfluxDB
  - Set the 'interval' to the number of seconds between each data collection
- Install the requirements with `pip install -r requirements.txt`
- Leave the script running in a screen session and sit back and watch the data roll in.

There are a couple of options that can be passed to the script to help you understand your data:

- To dump all the data from the Zappi in order to see the names, etc., run `zappioinflux.py --dump` 
and it will output all the data returned as json.
- To print the data rather than send it to InfluxDB, run `zappitoinflux.py --print` and it will output the
parsed data structure as json.
