import os


def log_test_result(
                     start_time, end_time, total_duration,
                     gen_input_duration, read_duration, process_duration,
                     config,
                     result_num_group, result_total_users, result_total_money,
                     result_unique_users,
                     out_file):
    test_columns = ['test_name', 'start_time', 'end_time', 'total_duration',
                    'gen_input_duration', 'read_input_duration',
                    'process_duration',
                    'total_users', 'user_interest_rows',
                    'total_titles', 'user_timeslot_rows',
                    'min_bid', 'max_bid', 'max_num_ticket',
                    'min_group_bid',
                    'result_num_group', 'result_total_users',
                    'result_total_money', 'result_unique_users'
                    ]
    test_result_filename = out_file
    if not os.path.exists(test_result_filename):
        with open(test_result_filename, 'w') as fdnew:
            fdnew.write(','.join(test_columns) + '\n')
    result_string = ','.join([
        str(config['test_name']),
        str(int(start_time)), str(int(end_time)), str(int(total_duration)),
        str(gen_input_duration), str(read_duration), str(process_duration),
        str(config['total_users']),
        str(config['user_interest_rows']),
        str(config['total_titles']),
        str(config['user_timeslot_rows']),
        str(config['min_bid'] if 'min_bid' in config else config['fixed_bid']),
        str(config['max_bid'] if 'max_bid' in config else config['fixed_bid']),
        str(config['max_num_ticket'] if 'max_num_ticket' in config else 1),
        str(config['min_group_bid']),
        str(result_num_group), str(result_total_users), str(result_total_money),
        str(result_unique_users)
    ])
    with open(test_result_filename, 'a') as fda:
        fda.write(result_string)
        fda.write('\n')
