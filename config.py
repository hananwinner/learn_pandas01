import collections


class Config(collections.abc.Mapping):
    def __init__(self, _dict):
        self._dict = _dict
        total_titles = self._dict['total_titles']
        total_users = self._dict['total_users']
        self._user_interest_rows = \
            round(total_titles * self._dict['user_interset_multiplier']
                  * total_users)
        self._user_timeslot_rows = \
            round(total_users * self._dict['user_timeslot_multiplier_per_day']
                  * self._dict['time_period_days'])

    def __getitem__(self, k):
        if k in self._dict:
            return self._dict[k]
        elif k == 'user_interest_rows':
            return self._user_interest_rows
        elif k == 'user_timeslot_rows':
            return self._user_timeslot_rows
        raise KeyError()

    def __len__(self):
        raise NotImplementedError()

    def __iter__(self):
        raise NotImplementedError()
