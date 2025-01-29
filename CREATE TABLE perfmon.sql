CREATE TABLE perfmon (
    id SERIAL PRIMARY KEY,
    host VARCHAR(25) NOT NULL,
    time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cpu_inst_util FLOAT4,
    cpu_avg_util FLOAT4,
    cpu_max_util FLOAT4,
    cpu_inst_temp VARCHAR(8),
    cpu_avg_temp VARCHAR(8),
    cpu_max_temp VARCHAR(8),
    disk_usage VARCHAR(5),
    ram_usage VARCHAR(5),
    tx_bytes INT,
    rx_bytes INT,
    cpu_meas_per_min INT
);

insert into perfmon(host, time_stamp, cpu_inst_util, cpu_avg_util, cpu_max_util, cpu_inst_temp, cpu_avg_temp, cpu_max_temp, disk_usage, ram_usage, tx_bytes, rx_bytes, cpu_meas_per_min)
values('proxmox2', '2025-01-29 11:31:02', 1.24, 1.61, 8.31, '39.0°C', '39.77°C', '42.0°C', '65%', '74%', 10555, 27819, 54);