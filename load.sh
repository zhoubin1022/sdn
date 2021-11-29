#!/bin/bash
tshark -r view_history.pcap -T fields -e frame.number -e frame.time_epoch -e frame.protocols -e ip.src -e ip.dst -e tcp.port -e udp.port -E separator=, > attack.csv
