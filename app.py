import socket
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import os
import requests

# Calculate the private IP at the start
private_ip = socket.gethostbyname(socket.gethostname())
print(private_ip)

# Global variable to keep track of the last row index
last_row_index = 0

# Function to create the CSV file if it doesn't exist
def create_csv_file():
    if not os.path.isfile('packets.csv'):
        with open('packets.csv', 'w') as f:
            f.write("src_ip,dst_ip,timestamp,packet_type,packet_count\n")  # Header

# Load only new entries and limit the number of packets
def load_new_packets(limit=50):
    global last_row_index
    create_csv_file()  # Ensure the file exists
    packets = pd.read_csv('packets.csv', names=['src_ip', 'dst_ip', 'timestamp', 'packet_type', 'packet_count'], header=0)
    new_packets = packets.iloc[last_row_index:]  # Get new entries
    last_row_index = len(packets)  # Update the last row index

    return new_packets.tail(limit)  # Return only the last 'limit' rows

# Define a mapping from packet types to colors
packet_type_colors = {
    'TCP': 'blue',
    'UDP': 'orange',
    'ICMP': 'green',
    'Unknown': 'gray',
}

# Function to get coordinates from IP address
def get_ip_location(ip):
    # Check if the IP is the private IP and replace it with the specified coordinates
    if ip == private_ip:
        return 25.43, 81.77  # Replace private IP coordinates

    url = f'http://ip-api.com/json/{ip}'
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200 and data['status'] == 'success':
        return data['lat'], data['lon']
    else:
        print(f"Location data not found for IP: {ip}")
        return None, None

# Streamlit app
st.title("Network Traffic Visualization")

# Input parameters for packet capture
interface = st.selectbox("Select Network Interface", ["Wi-Fi", "Ethernet"])  # Add other interfaces as needed
packet_count = st.number_input("Number of packets to capture", min_value=1, max_value=1000, value=100)

# Create a placeholder for the map
map_placeholder = st.empty()

# Start packet capture button
if st.button("Start Packet Capture"):
    st.warning("Packet capture is now running in a separate process. Use the terminal to stop it.")
    # Instructions to run the capture script

# Load packets button
if st.button("Load New Packets"):
    new_packets = load_new_packets(limit=packet_count)  # Load packets based on user input
    if not new_packets.empty:
        st.success(f"Loaded {len(new_packets)} new packets.")

        # Display packet data
        st.write(new_packets)

        # Create a table to show packet type to color mapping
        packet_type_df = pd.DataFrame({
            'Packet Type': ['TCP', 'UDP', 'ICMP', 'Unknown'],
            'Color': ['Blue', 'Orange', 'Green', 'Gray']
        })
        st.table(packet_type_df)  # Display the table

        # Initialize the map at the start
        traffic_map = folium.Map(location=[0, 0], zoom_start=2)  # Center the map at [0, 0]

        # Add lines for each packet dynamically
        for _, row in new_packets.iterrows():
            # Get coordinates from IP addresses
            src_coordinates = get_ip_location(row['src_ip'])
            dst_coordinates = get_ip_location(row['dst_ip'])

            if src_coordinates != (None, None) and dst_coordinates != (None, None):
                # Determine line color based on packet type
                line_color = packet_type_colors.get(row['packet_type'], 'gray')

                # Draw a line from source to destination
                folium.PolyLine(
                    locations=[src_coordinates, dst_coordinates],
                    color=line_color,
                    weight=2 + int(row['packet_count']) / 10,  # Line thickness based on packet count
                    opacity=0.7,
                ).add_to(traffic_map)

                # Add markers for source and destination
                folium.Marker(
                    location=src_coordinates,
                    popup=f"Source: {row['src_ip']}, Time: {row['timestamp']}, Type: {row['packet_type']}, Count: {row['packet_count']}",
                    icon=folium.Icon(color="blue"),
                ).add_to(traffic_map)

                folium.Marker(
                    location=dst_coordinates,
                    popup=f"Destination: {row['dst_ip']}, Time: {row['timestamp']}, Type: {row['packet_type']}, Count: {row['packet_count']}",
                    icon=folium.Icon(color="red"),
                ).add_to(traffic_map)

                # Update the map in the placeholder
                map_placeholder.empty()  # Clear previous map
                with map_placeholder:
                    folium_static(traffic_map)

            else:
                print(f"Skipping packet with invalid location: {row['src_ip']} -> {row['dst_ip']}")

    else:
        st.warning("No new packets captured.")
