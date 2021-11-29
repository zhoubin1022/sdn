#!/bin/bash
filename='view_history.pcap'
touch $filename
tcpdump -i $1 -s 0 -w $filename & tdid='pgrep tcpdump'
