import sys
import os
import time
import requests
import json
import argparse

def __init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION] [FILE]...",
        description="<program_description>"
    )
    parser.add_argument(
        "-v", "--version", action="version",
        version = f"{parser.prog} version 0.01"
    )
    parser.add_argument('-o','--output',nargs=1,default=False,
                    help='file to store result in - defaults to none')
    parser.add_argument('-c','--cache',nargs=1,default=False,
                    help='cache directory - defaults to forced call and stores result in cwd if output provided')
    parser.add_argument('-t','--time',nargs=1,type=int,default=5,
                    help='age of cache file in mins to force call - defaults to 5 ')
    parser.add_argument('-s','--sleep',nargs=1,type=int,default=200,
                    help='time to sleep in ms for the request - default 200')
    parser.add_argument('-nc','--no-cache',default=False,action='store_true',
                    help='force a rest call')
    parser.add_argument('-r','--rest',nargs=1,default=False,
                    help='REST object - if not provided will return an error object')
    args = parser.parse_args()
    #print(args)
    if args.cache is False:
        args.cache = os.getcwd()
    return args

def __getTime(float):
    return int(str(float).split('.')[0])

def __readCache(file, path=os.getcwd(), age=5):
    if path == '':
        fileToOpen = file
    else:
        fileToOpen = path + '/' + file
    try:
        if os.path.exists(fileToOpen):
            fileAge = __getTime(time.time()) - __getTime(os.path.getmtime(fileToOpen))
            if fileAge / 60 > age:
                return False   
            with open(fileToOpen, 'r') as f:
                for line in f:
                    jsonObj = line.strip(' \t\n\r')
                    return jsonObj
        return False
    except Exception as e:
        return {
            'errorCode':'ReadFile',
            'errorDescription':str(e)
        } 

def __executeCall(restObj, sleep):
    time.sleep(sleep / 1000)
    try:
        operation = restObj.operation 
        endpoint = restObj.endpoint
        params = restObj.params
        payload = restObj.payload
        headers = restObj.headers
        if operation == 'get':
            response = requests.get(
                url=endpoint,
                params=params,
                headers=headers,
                data=payload
            )
            return response.text
    except Exception as e:
        return {
            'errorCode':'RESTCall',
            'errorDescription':str(e)
        }

def __writeCache(file, content, path=os.getcwd()):
    if path == '':
        fileToWrite = file
    else:
        fileToWrite = path + '/' + file
    os.makedirs(os.path.dirname(fileToWrite), exist_ok=True)
    try:
        with open(fileToWrite, 'w') as f:
            f.write(content)
    except Exception as e:
        return {
            'errorCode':'WriteFile',
            'errorDescription':str(e)
        }

def __validateConfig(config):
    if 'no_cache' not in config:
        config['no_cache'] = False
    if 'output' not in config:
        config['output'] = None
    if 'cache' not in config:
        config['cache'] = None
    if 'time' not in config:
        config['time'] = 5
    if 'sleep' not in config:
        config['sleep'] = 200
    if 'rest' not in config:
        return False
    return config

def execute(config):
    config = __validateConfig(config)
    if not config:
        return False
    runCall = False
    returnJSON = False
    #003 - Check Cache
    if config['output'] is not None:
        #004 - Read File
        returnJSON = __readCache(config['output'], config['cache'] or os.getcwd(), config['time'])
    #005 - Rest Call
    if returnJSON is False or config['no_cache']:
        returnJSON = __executeCall(config['rest'], config['sleep'])
        runCall = True
    #006 - Write to cache
    if returnJSON is not False and config['output'] and runCall:
        if 'errorCode' not in returnJSON:
            errorObj = __writeCache(config['output'], returnJSON, config['cache'])
    #007 - Return JSON Data
    return returnJSON

def main():
    args = __init_argparse()
    config = {
        'cache': args.cache,
        'output': args.output,
        'time': args.time,
        'sleep': args.sleep,
        'no_cache': args.no_cache,
        'rest': args.rest
    }
    returnJSON = execute(config)
    print(returnJSON)

if __name__ == "__main__":
    main()