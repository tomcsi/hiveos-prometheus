#!/usr/bin/python3
#pip3 install -r requirements.txt

import json
from datetime import datetime, timedelta
from time import sleep
import os
from prometheus_client import Gauge,Info, start_http_server, push_to_gateway, CollectorRegistry

print("Get Stats")


def time_string():
    current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    return current_time


def hashrate(rates,total):
    #print(str(len(rates)) + " CARDS")
    for x in range(len(rates)):
        g['hash'].labels(rig=rig,card = x).set(rates[x]*1000)
        g['hash'].labels(rig=rig,card = "total").set(total)


def timetowait():
    delta = timedelta(minutes=1)
    now = datetime.now()
    next_minute = (now + delta).replace(microsecond=0,second=30)
    wait_seconds = (next_minute - now)
    wait_seconds = int((wait_seconds).total_seconds())
    print("    " + time_string() + "   " + str(wait_seconds)+"s until next")
    return(wait_seconds)

def cardstats(ctemps,mtemps,power,fan):
    for x in range(len(ctemps)):
        
        g['coretemp'].labels(rig=rig,card = x).set(ctemps[x])
        g['memtemp'].labels(rig=rig,card = x).set(mtemps[x])
        g['power'].labels(rig=rig,card = x).set(power[x])
        g['fan'].labels(rig=rig,card = x).set(fan[x])

def main_server():
    print("Main")
    start_http_server(7890)
    while(True):
        with open("/run/hive/last_stat.json") as json_data_file:
            stats = json.load(json_data_file)
            hash = (stats["params"]["miner_stats"]["hs"])
            
            ctemps = (stats["params"]["temp"])
            try:
                mtemps = (stats["params"]["mtemp"])
            except:
                mtemps = [0] * (len(ctemps)+1)
            power = (stats["params"]["power"])
            fan = (stats["params"]["fan"])
            totalhash = (int((stats["params"]["total_khs"]))*1000)
            miner = (stats["params"]["miner"])
            miner_ver = (stats["params"]["miner_stats"]["ver"])
            ars = (stats["params"]["miner_stats"]["ar"])
            
        i.info({'MinerVersion': miner_ver , 'MinerType': miner})
           
        g['ratio'].labels(rig=rig,type = "accepted").set(ars[0])
        g['ratio'].labels(rig=rig,type = "rejected").set(ars[1])
        hashrate(hash,totalhash)
        cardstats(ctemps,mtemps,power,fan)
        sleep(timetowait())

def main_push():
    print("Main")
    while(True):
        with open("./last_stat.json") as json_data_file:
            stats = json.load(json_data_file)
            hash = (stats["params"]["miner_stats"]["hs"])
            
            ctemps = (stats["params"]["temp"])
            try:
                mtemps = (stats["params"]["mtemp"])
            except:
                mtemps = [0] * (len(ctemps)+1)
            power = (stats["params"]["power"])
            fan = (stats["params"]["fan"])
            totalhash = (int((stats["params"]["total_khs"]))*1000)
            miner = (stats["params"]["miner"])
            miner_ver = (stats["params"]["miner_stats"]["ver"])
            ars = (stats["params"]["miner_stats"]["ar"])
            
        i.info({'MinerVersion': miner_ver , 'MinerType': miner})
           
        g['ratio'].labels(rig=rig,type = "accepted").set(ars[0])
        g['ratio'].labels(rig=rig,type = "rejected").set(ars[1])
        hashrate(hash,totalhash)
        cardstats(ctemps,mtemps,power,fan)
        sleep(timetowait())
        push_to_gateway(pushserver, job=rig, registry=registry)

rig = os.environ['RIG_NAME']
mode = os.environ['MODE']

print(rig)

registry = CollectorRegistry()
g = {}
g['hash'] = Gauge('hive_hashrate','Hashrate',['rig','card'], registry=registry)
g['coretemp'] = Gauge('hive_coretemp','GPU Core Temp',['rig','card'], registry=registry)
g['memtemp'] = Gauge('hive_memtemp','GPU Memory Temperature',['rig','card'], registry=registry)
g['power'] = Gauge('hive_power','GPU Power Consumption',['rig','card'], registry=registry)
g['fan'] = Gauge('hive_fan','GPU Fan Speed',['rig','card'], registry=registry)
g['ratio'] = Gauge('hive_ratio','Acceptance ratio',['rig','type'], registry=registry)

i = {}
i = Info('minername', 'Current Miner')

if mode == "push":
    pushserver = os.environ['PUSHSERVER']
    main_push()
else:
    main_server()
