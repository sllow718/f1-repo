import sys
import os
import glob
import time
import socket
import pickle
import json
import queue
import logging

from telemetry_f1_2021.packets import PacketHeader, Packet, HEADER_FIELD_TO_PACKET_TYPE, HEADER_FIELD_TO_PACKET_TYPE_OVERRIDE

def find_packet_by_bestfit(key,data):
    bestfit = None
    packet = None
    for ii in HEADER_FIELD_TO_PACKET_TYPE_OVERRIDE.keys():
        if key[0] == ii[0] and key[1] == ii[1] and key[2] == ii[2] and key[3] >= ii[3] and key[4] >= ii[4]:
            bestfit = ii
    if bestfit != None:
        packet = HEADER_FIELD_TO_PACKET_TYPE_OVERRIDE[bestfit].from_buffer_copy(data)
    return packet

q = queue.Queue()
socketclient = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
localudpclient = (sys.argv[1], 20777)
timestamp = None
start = None

def send(tuple):
    global start
    global timestamp
    global socketclient
    global localudpclient 
    current_timestamp = tuple[0]
    if timestamp == None:
        timestamp = current_timestamp;
    delta_timestamp = (current_timestamp - timestamp) / 1000000
    packet = tuple[1]
    current_time = time.time_ns()
    delta_time = (current_time - start) / 1000000
    if (delta_timestamp > delta_time):
        time.sleep((delta_timestamp - delta_time)/1000)
    # Send to server using created UDP socket
    packet.m_header.m_session_uid = start
    print(str(packet.m_header.m_session_uid)+":"+str(packet.m_header.m_packet_id)+":"+str(packet.m_header.m_frame_identifier))
    socketclient.sendto(packet.pack(), localudpclient)

def read_and_queue(filename):
    global q
    with open(filename, "rb") as input_file:
        data = pickle.load(input_file) 
        current_timestamp = int(filename[filename.rfind('-')+1:filename.find('.pickle')])
        if isinstance(data,Packet) == False:
            packet = PacketHeader.from_buffer_copy(data)
            bestkey = (packet.m_packet_format, packet.m_packet_version, packet.m_packet_id, packet.m_game_major_version, packet.m_game_minor_version)
            basekey = (packet.m_packet_format, packet.m_packet_version, packet.m_packet_id)
            print(bestkey)
            print(basekey)
            packet = find_packet_by_bestfit(bestkey,data)
            print(packet)
            if packet == None:
                packet = HEADER_FIELD_TO_PACKET_TYPE[basekey].from_buffer_copy(data)
                print(packet)
        else:
            packet = data
        if packet != None:
            q.put((current_timestamp,packet))

def sort_by_filename_timestamp(filename):
    # 9038508826540061828-telemetry-1655937106567290379.pickle
    return filename[filename.rfind('-')+1:filename.find('.pickle')]

def print_help():
    print("Help: (Sample)")
    print("Syntax: test/main.py hostname testdir")
    print("hostname: IP address of the UDP listener (with default port of 20777)")
    print("testdir: directory where the series of pickle files will be read from.")
    print("NB: Assume that the filename format (and origin) of pickle files are from the f1sim-consumer.")
    print("")
    print(". dev/bin/activate")
    print(". f1env.sh")
    print("python3 test/main.py localhost test/data/123")

def main():
    global start
    try:
        data_dir = sys.argv[2]
        glob_results = glob.glob(data_dir+'/*.pickle')
        glob_results = sorted(glob_results,key=sort_by_filename_timestamp)
        for g in glob_results:
            read_and_queue(g)
        start = time.time_ns()
        while q.empty() == False:
            send(q.get())
            q.task_done()
    except (Exception) as ex:
        print(ex)
        print_help()

if __name__ == '__main__':
    main()
