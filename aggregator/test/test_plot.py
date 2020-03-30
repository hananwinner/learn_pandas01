import pandas as pd
import matplotlib.pyplot as plt

if __name__ == '__main__':
    df = pd.read_csv('variable_user-20_titles_results.csv')
    df = df.groupby(by='total_users').mean()
    df = df.reset_index()
    df['user_percent'] = df['result_total_users'] / df['total_users'] * 100
    df['unique_user_percent'] = df['result_unique_users'] / df['total_users'] * 100
    ax = plt.gca()
    df.plot(kind='bar', x='total_users', y='user_percent', ax=ax)
    df.plot(kind='bar', color="yellow", x='total_users', y='unique_user_percent', ax=ax)

    # df.plot(kind='bar', x='total_users', y='user_percent')

    plt.savefig('graphs/user_percent4.png')
    plt.show()
