#!/bin/bash

# Add a crontab setting to run this file every minute (*/1 * * * * /usr/local/bin/perfmon.sh)
# Suggest placing in /usr/local/bin path

# Set the remote hostnames of your syslog servers (comma separated)
syslog_servers='172.20.68.83'

# Set main or primary Ethernet interface
eth_interface="enp1s0"

# Set files location, but recommend /tmp folder as it is open to write and not persistent
get_cpu_peaks="/usr/local/bin/get_cpu_peaks.sh"
net_data_file="/tmp/net_metrics.txt"
cpu_peaks_file="/tmp/cpu_peaks.txt"

# Determine if first run, or if first run after reboot (needs procps and/or ethtool)
# If true, set intitial rx and tx values to calculate a delta value
if [ ! -f "$net_data_file" ]; then
  echo "tx_value: $(awk '{print $1}' /sys/class/net/$eth_interface/statistics/tx_bytes)
  rx_value: $(awk '{print $1}' /sys/class/net/$eth_interface/statistics/rx_bytes)" > "$net_data_file"
fi

# Check if 'get_cpu_peaks.sh' script is running, if not, start it
PID=$(pgrep -f get_cpu_peaks.sh | head -n 1)
if [ -z "$PID" ]; then
  # Main script not running, start it
  eval "${get_cpu_peaks}" &
fi

# get the hostname of this machine
get_hostname() {
  declare -g current_hostname="${HOSTNAME}"
}

# Function to get cpu utilization (requires sysstat package, set /etc/default/sysstat ENABLED="true")
get_cpu_utilization() {
  output=$(sar -u ALL 1 1)
  last_line=$(echo "$output" | tail -n 1)
  idle_value=$(echo "$last_line" | awk '{print $NF}')
  declare -g cpu_utilization=$(bc <<< "100 - $idle_value")
}

# Function to get cpu temperature (requires lm-sensors package)
get_cpu_temperature() {
  temp=$(sensors | grep "Core" | head -1 | cut -d "+" -f2-)
  cpu_temporary="${temp:0:7}"
  declare -g cpu_temperature=$(echo "$cpu_temporary" | tr -d '[:space:]' | sed 's/°C$//')
}

# Function to get hard disk space used and available (requires df package)
get_disk_usage() {
  declare -g disk_used=$(df -h | awk '/\/dev\/mapper\/pve-root/ {print $5 }')
}

# Function to get RAM memory usage (requires free package)
get_ram_usage() {
   ram_used=$(free -m | grep Mem: | awk '{print $3}')
   ram_total=$(free -m | grep Mem: | awk '{print $2}')
   declare -g percent_ram_used=$(( (ram_used * 100) / ram_total ))
}

# Function to get tx network stats
get_network_tx() {
  prev_tx_bytes=$(awk '{if (NR==1) {print $2; exit}}' "$net_data_file")
  new_tx_bytes=$(cat /sys/class/net/$eth_interface/statistics/tx_bytes | awk '{print $1}')
  tx_delta=$((new_tx_bytes - prev_tx_bytes))
  declare -g tx_bytes=$tx_delta
}

# Function to get rx network stats
get_network_rx() {
  prev_rx_bytes=$(awk '{if (NR==2) {print $2; exit}}' "$net_data_file")
  new_rx_bytes=$(cat /sys/class/net/$eth_interface/statistics/rx_bytes | awk '{print $1}')
  rx_delta=$((new_rx_bytes - prev_rx_bytes))
  declare -g rx_bytes=$rx_delta
}

get_cpu_peaks() {
# Check if the file exists
  if [ -f "$cpu_peaks_file" ]; then
    # Use awk to extract first and second columns into variables max util and max temp respectively
   cmu=$(awk '{print $1}' "$cpu_peaks_file")
   cmt=$(awk '{print $2}' "$cpu_peaks_file")
   declare -g cpu_max_util=$cmu cpu_max_temp=$cmt
 fi
}

get_cpu_avg() {
# Check if the file exists
  if [ -f "$cpu_peaks_file" ]; then
    # Use awk to extract third and fourth columns into variables avg util and avg temp respectively
    cau=$(awk '{print $3}' "$cpu_peaks_file")
     cat=$(awk '{print $4}' "$cpu_peaks_file")
   declare -g cpu_avg_util=$cau cpu_avg_temp=$cat
 fi
}

get_cpu_measures_min() {
  if [ -f "$cpu_peaks_file" ]; then
    # Use awk to extract fith column into variables for measures per minute
    cmp=$(awk '{print $5}' "$cpu_peaks_file")
    declare -g cpu_meas_min=$cmp
 fi
}

# Set stored byte values to current values for next delta calculation
reset_network_bytes() {
  echo "tx_value: $(awk '{print $1}' /sys/class/net/$eth_interface/statistics/tx_bytes)
  rx_value: $(awk '{print $1}' /sys/class/net/$eth_interface/statistics/rx_bytes)" > "$net_data_file"
}

# Get metrics and reset byte values
get_hostname
get_cpu_utilization
get_cpu_temperature
get_disk_usage
get_ram_usage
get_network_tx
get_network_rx
get_cpu_peaks
get_cpu_avg
get_cpu_measures_min
reset_network_bytes

# Get current time
time_stamp=$(date +"%Y-%m-%d %H:%M:%S")

# Construct log message
log_message="host=${current_hostname},timestamp=${time_stamp},cpu_inst_util=${cpu_utilization},cpu_avg_util=${cpu_avg_util},cpu_max_util=${cpu_max_util},cpu_inst_temp=${cpu_temperature}C,cpu_avg_temp=${cpu_avg_temp}C,cpu_max_temp=${cpu_max_temp}C,disk_usage=${disk_used},ram_usage=${percent_ram_used}%,tx_bytes=${tx_bytes},rx_bytes=${rx_bytes},cpu_meas_per_min=${cpu_meas_min}"

# Send logs to syslog servers
for server in $syslog_servers; do
  logger -s -n $server "$log_message"
done
