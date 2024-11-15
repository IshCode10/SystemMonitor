import tkinter as tk
from tkinter import ttk
import psutil
import os
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Thresholds for alerts (can be modified as needed)
CPU_THRESHOLD = 85
MEMORY_THRESHOLD = 80
DISK_THRESHOLD = 90

# Initialize SQLite Database
conn = sqlite3.connect("system_health.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS health_data (
    timestamp TEXT,
    cpu_usage REAL,
    memory_usage REAL,
    disk_usage REAL,
    network_status TEXT
)
""")
conn.commit()

# Function to save data to the database
def save_to_db(cpu, memory, disk, network_status):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO health_data VALUES (?, ?, ?, ?, ?)",
                   (timestamp, cpu, memory, disk, "Online" if network_status else "Offline"))
    conn.commit()

# Function to check system metrics
def check_cpu_usage():
    return psutil.cpu_percent(interval=1)

def check_memory_usage():
    return psutil.virtual_memory().percent

def check_disk_usage():
    return psutil.disk_usage('/').percent

def check_network():
    return os.system("ping -c 1 8.8.8.8") == 0

# Tkinter GUI setup
root = tk.Tk()
root.title("System Health Monitor")

# Labels to display real-time metrics
cpu_label = ttk.Label(root, text="CPU Usage: Calculating...", font=("Arial", 14))
cpu_label.pack(pady=5)
memory_label = ttk.Label(root, text="Memory Usage: Calculating...", font=("Arial", 14))
memory_label.pack(pady=5)
disk_label = ttk.Label(root, text="Disk Usage: Calculating...", font=("Arial", 14))
disk_label.pack(pady=5)
network_label = ttk.Label(root, text="Network Status: Checking...", font=("Arial", 14))
network_label.pack(pady=5)

# Function to update metrics and display them in the GUI
def update_metrics():
    cpu = check_cpu_usage()
    memory = check_memory_usage()
    disk = check_disk_usage()
    network = check_network()
    
    cpu_label['text'] = f"CPU Usage: {cpu}%"
    memory_label['text'] = f"Memory Usage: {memory}%"
    disk_label['text'] = f"Disk Usage: {disk}%"
    network_label['text'] = "Network Status: Online" if network else "Network Status: Offline"
    
    # Save metrics to the database
    save_to_db(cpu, memory, disk, network)

    # Schedule next update
    root.after(5000, update_metrics)  # Update every 5 seconds

# Run the update_metrics function for the first time
update_metrics()

# Data for graphing trends
time_stamps = []
cpu_data = []
memory_data = []

# Function to update the graph with new data from the database
def update_graph(frame):
    cursor.execute("SELECT timestamp, cpu_usage, memory_usage FROM health_data ORDER BY timestamp DESC LIMIT 20")
    data = cursor.fetchall()[::-1]  # Reverse to show oldest data first
    
    # Extract data for plotting
    time_stamps.clear()
    cpu_data.clear()
    memory_data.clear()
    for row in data:
        time_stamps.append(row[0])
        cpu_data.append(row[1])
        memory_data.append(row[2])

    # Clear previous plots and re-plot with updated data
    ax1.clear()
    ax2.clear()
    ax1.plot(time_stamps, cpu_data, label="CPU Usage (%)")
    ax2.plot(time_stamps, memory_data, label="Memory Usage (%)")
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper left")
    ax1.set_ylabel("CPU Usage (%)")
    ax2.set_ylabel("Memory Usage (%)")
    ax2.set_xlabel("Time")
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

# Initialize Matplotlib figure and subplots
fig, (ax1, ax2) = plt.subplots(2, 1)
fig.suptitle("System Health Metrics Over Time")

# Run the animation for live updating of the graph
ani = FuncAnimation(fig, update_graph, interval=5000)  # Update every 5 seconds

# Button to open the graph window
def open_graph():
    plt.show()

graph_button = ttk.Button(root, text="Show Trend Graph", command=open_graph)
graph_button.pack(pady=20)

# Run the Tkinter main loop
root.mainloop()
