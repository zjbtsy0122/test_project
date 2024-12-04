SELECT
            CONCAT("'", clientcomm_common_time) AS '时间|clientcomm_common_time',
            total_dequeue_speed AS '持续吞吐率|total_dequeue_speed',
            max_deal_speed AS '峰值吞吐率|max_deal_speed',
            avg_deal_time AS '平均时延ms|avg_deal_time',
            total_enqueue AS '总请求|total_enqueue',
            failed_cnt AS '失败数|failed_cnt'
        FROM
            loganalyze.test_client
        WHERE
            ip = '192.168.8.20'
            AND clientcomm_common_time BETWEEN %s AND %s
        ORDER BY
            clientcomm_common_time;