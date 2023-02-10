import requests
import time
import threading
import datetime
import plyer
import logging
from playsound import playsound

logging.basicConfig(
    level=logging.DEBUG, format='%(threadName)s: %(message)s')

notify_list = { "Prapor":False, "Therapist":False, "Fence":False, "Skier":False, "Peacekeeper":True, "Mechanic":True, "Ragman":False, "Jaeger":False, "Lightkeeper":False}

def run_query(query):
    headers = {"Content-Type": "application/json"}
    response = requests.post('https://api.tarkov.dev/graphql', headers=headers, json={'query': query})
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(response.status_code, query))

def get_resetTime():
    new_query = """
    {
    traders(lang: ja) {
        name
        resetTime
        }
    }
    """
    return run_query(new_query)

def notify(name):
    print(name + "will restock in 3 minutes!")
    playsound("sounds/" + name + ".wav")
    playsound("sounds/" + "restock.wav")
    plyer.notification.notify(title="Restock Notification",
        message=name + " will restock in 3 minutes!",
        timeout=10
    )
    reset = threading.Timer(300,startTimer,args=(name,))
    reset.start()

def startTimer(name):
    logging.debug('start')
    traders = get_resetTime()
    for tr in traders['data']['traders']:
        if tr['name'] == name:
            resetTime = tr['resetTime']
    currentTime = time.time()
    resetTime = datetime.datetime.strptime(resetTime,'%Y-%m-%dT%H:%M:%S.000Z').timestamp() + 32400


    remainTime = resetTime - currentTime
    print(remainTime)
    print(name)
    if remainTime < 180:
        if remainTime < 0:
            createTimer(300,name)
        else:
            print(name + " will restock in " + str(remainTime) + "seconds!")
            createTimer(300,name)
    else:
        reset = threading.Timer(remainTime - 180,notify,args=(name,))
        reset.start()

    logging.debug('end')
    
def createTimer(remainTime,name):
    t = threading.Timer(remainTime,startTimer,args=(name,))
    t.start()
    

def main():
    traders = get_resetTime()
    print("API data recieved:" + str(traders))
    traderNames = []

    for t in traders['data']['traders']:
        traderNames.append(t['name'])
    
    for t in traderNames:
        if notify_list[t]:
            print(t + ": timer started")
            startTimer(t)

    


if __name__ == "__main__": 
    main()









