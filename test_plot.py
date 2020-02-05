import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

if __name__ == '__main__':
    df = pd.read_csv('variable_user-2_results.csv',
                     # index_col=['total_users'],
            dtype={
                'test_name': 'object',
                'start_time': 'float64',
                'end_time': 'float64',
                'total_duration': 'float64',
                'gen_input_duration': 'float64',
                'read_input_duration': 'float64',
                'process_duration': 'float64',
                'total_users': 'int64',
                'user_interest_rows': 'int64',
                'total_titles': 'int64',
                'user_timeslot_rows': 'int64',
                'min_bid': 'int64', 'max_bid': 'int64', 'max_num_ticket': 'int64',
                'min_group_bid': 'int64',
                'result_num_group': 'int64', 'result_total_users': 'int64',
                'result_total_money': 'int64'
            })

    # ax = plt.gca()
    df['user_percent'] = df['result_total_users'] / df['total_users'] * 100
    df.plot(kind='bar', x='total_users', y='user_percent', color='blue')
    # plt.savefig('test/graphs/user_percent2.png')
    plt.show()
