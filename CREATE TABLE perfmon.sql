CREATE TABLE perfmon (
	id serial4 NOT NULL,
	host varchar(25) NOT NULL,
	"time_stamp" timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	cpu_inst_util float4 NULL,
	cpu_avg_util float4 NULL,
	cpu_max_util float4 NULL,
	cpu_inst_temp varchar(15) NULL,
	cpu_avg_temp varchar(15) NULL,
	cpu_max_temp varchar(15) NULL,
	disk_usage varchar(10) NULL,
	ram_usage varchar(10) NULL,
	tx_bytes int4 NULL,
	rx_bytes int4 NULL,
	cpu_meas_per_min int4 NULL,
	CONSTRAINT perfmon_pkey PRIMARY KEY (id)
);

CREATE INDEX idx_time_stamp ON perfmon (time_stamp);
CREATE INDEX idx_host ON perfmon (host);
