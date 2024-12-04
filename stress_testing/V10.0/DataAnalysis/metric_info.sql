SELECT
            CONCAT("'", time) AS 'Time',
            cpu AS 'CPU|cpu',
            memory AS '内存|memory',
            disks_readbytes AS '磁盘IO读取|disks_readbytes',
            disks_writebytes AS '磁盘IO写入|disks_writebytes',
            network_bytesrecv AS '网络接收字节|network_bytesrecv',
            network_bytessent AS '网络发送字节|network_bytessent'
        FROM
            loganalyze.metric_info
        WHERE
            ip = '172.190.121.106' AND time BETWEEN %s AND %s
        ORDER BY
            time;