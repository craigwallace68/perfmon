# perfmon
A set of bash scripting and ETL processes to monitor linux server statistics, log them, and store them in SQL for analysis.

Steps to install:
 1.  Ensure sysstat, lm-sensors, ethtool, procps are installed on the linux server to be monitored.
 2.  Modify /etc/default/sysstat file line 'ENABLED=true'
 3.  Copy perfmon.sh & get_cpu_peaks.sh files into (recommended) /usr/local/bin/ folder, and set permissions to exec.
 4.  Set syslog server address(s), file paths in both perfmon.sh & get_cpu_peaks.sh files (recommendaton in comments, or change as needed).
 5.  Set up remote (or local) syslog receiver /etc/rsyslog.conf to allow udp/tcp port 514 (as shown in 'netservices syslog receiver' file.
 6.  Verify any firewall port 514 as needed on network, if required.
 7.  Set crontab file to execute perfmon.sh file cadence (recommended 1 min intervals).

The main perfmon routine will collect and process data, and form the syslog message and send it to the designated server(s) per the crontab schedule.

The get_cpu_peaks routine runs constantly to record transient peaks as well as averages for time inbetween the syslog messages, ensuring transients are captured and not missed (to about 1 second resolution).
