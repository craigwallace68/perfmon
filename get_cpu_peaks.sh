#!/bin/bash

# Set file path and variables
max_cpu_util=-1.0
max_cpu_temp=-1.0
measure_cycles=0
cpu_aggregate_util=0
cpu_aggregate_temp=0
cpu_avg_util=0
cpu_avg_temp=0
cpu_peaks_file="/tmp/cpu_peaks.txt"

# Function to get cpu peak utilization
# (requires sysstat package, set /etc/default/sysstat ENABLED="true")
get_cpu_util() {
  output=$(sar -u ALL 1 1)
  last_line=$(echo "$output" | tail -n 1)
  idle_value=$(echo "$last_line" | awk '{print $NF}')
  declare -g cpu_util=$(bc <<< "100 - $idle_value")
}

# Function to get cpu temperature (requires lm-sensors package)
get_cpu_temp() {
  temp=$(sensors | grep "Core" | head -1 | cut -d "+" -f2-)
  cpu_temporary="${temp:0:7}"
  declare -g cpu_temp=$(echo "$cpu_temporary" | sed 's/°C//; s/ $//')
}

trap 'exit' INT

# Run while not top of minute, write peaks, pause for cron job to pick up values
while true; do

# Update max values with the latest value if it's greater than the current
  get_cpu_util  # grab cpu util instance
  if (( $(printf "%s\n" "$cpu_util" | awk '{print $0 * 1000}') > $(printf "%s\n" "$max_cpu_util" | awk '{print $0 * 1000}') )); then
      max_cpu_util="$cpu_util"
  fi

  get_cpu_temp  # grab cpu temp instance
  if (( $(printf "%s\n" "$cpu_temp" | awk '{print $0 * 1000}') > $(printf "%s\n" "$max_cpu_temp" | awk '{print $0 * 1000}') )); then
      max_cpu_temp="$cpu_temp"
  fi

# Aggregate total measurements and calculate average
measure_cycles=$((measure_cycles+1))
cpu_aggregate_util=$(echo "scale=0; ${cpu_aggregate_util} + ($cpu_util)" | bc)
cpu_aggregate_temp=$(echo "scale=0; ${cpu_aggregate_temp} + ($cpu_temp)" | bc)

# Check if near top of minute to set max values for perfmon script to pickup
  if (( $(printf "%s\n" "$(date +%S)" | awk '{print $0 * 1000}') > $(printf "%s\n" "58" | awk '{print $0 * 1000}') )); then
      cpu_avg_util=$(bc -l <<< "scale=2; $cpu_aggregate_util / $measure_cycles")
      cpu_avg_temp=$(bc -l <<< "scale=2; $cpu_aggregate_temp / $measure_cycles")
      echo "${max_cpu_util}" "${max_cpu_temp}" "${cpu_avg_util}" "${cpu_avg_temp}" "${measure_cycles}" > "$cpu_peaks_file"
      max_cpu_util=-1.0
      max_cpu_temp=-1.0
      measure_cycles=0
      cpu_aggregate_util=0
      cpu_aggregate_temp=0
      sleep 5
  fi

done
