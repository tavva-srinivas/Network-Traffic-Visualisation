# capture_packets.py
import pyshark
import pandas as pd
import time
import os
from datetime import datetime

def create_csv_file():
    if not os.path.isfile('packets.csv'):
        with open('packets.csv', 'w') as f:
            f.write("src_ip,dst_ip,timestamp,packet_type,packet_count\n")  # Header

def capture_packets(interface='Wi-Fi', packet_count=100):
    print(f"Capturing {packet_count} packets on interface: {interface}...")
    create_csv_file()
    capture = pyshark.LiveCapture(interface=interface)

    packet_dict = {}  # To store aggregated packet information

    try:
        while True:  # Run indefinitely
            capture.sniff(packet_count=packet_count)

            for packet in capture:
                if 'IP' in packet:
                    src_ip = packet.ip.src
                    dst_ip = packet.ip.dst
                    timestamp = str(packet.sniff_time)
                    packet_type = packet.transport_layer if hasattr(packet, 'transport_layer') else 'Unknown'

                    # Round the timestamp to the nearest second for aggregation
                    timestamp_key = timestamp.split('.')[0]  # Take only the date and time up to seconds

                    # Create a unique key for the packet entry
                    key = (src_ip, dst_ip, packet_type, timestamp_key)

                    if key in packet_dict:
                        packet_dict[key] += 1  # Increment the count
                    else:
                        packet_dict[key] = 1  # Initialize the count

            # Write the aggregated packets to CSV every second
            with open('packets.csv', 'a') as f:
                for (src, dst, p_type, ts), count in packet_dict.items():
                    f.write(f"{src},{dst},{ts},{p_type},{count}\n")

            # Clear the dictionary for the next second
            packet_dict.clear()
            time.sleep(1)  # Adjust sleep time as needed

    except Exception as e:
        print(f"Error capturing packets: {e}")

if __name__ == "__main__":
    interface = input("Enter network interface (e.g., Wi-Fi): ")
    packet_count = int(input("Enter number of packets to capture: "))
    capture_packets(interface, packet_count)
