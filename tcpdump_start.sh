#!/bin/bash
filename='view_history.pcap'
touch $filename
#没有后面的tdid则无法退出tcpdump进程
tcpdump -i s1-eth4 -s 0 -w $filename & tdid='pgrep tcpdump'

sleep 10s
file_size=`du view_history.pcap|awk '{print $1}'`
tshark -r view_history.pcap -T fields -e frame.number -e frame.time_epoch -e frame.protocols -e ip.src -e ip.dst -e tcp.port -e udp.port -E separator=, > attack.csv
echo 'file_size'$file_size
