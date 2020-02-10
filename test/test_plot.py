import pandas as pd
import matplotlib.pyplot as plt

if __name__ == '__main__':
    df = pd.read_csv('variable_user-4_results.csv')
    df['user_percent'] = df['result_total_users'] / df['total_users'] * 100
    df.plot(kind='bar', x='total_users', y='user_percent')
    # plt.savefig('graphs/user_percent2.png')
    plt.show()
