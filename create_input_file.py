import uuid
import numpy as np
import datetime


NUM_CAMP = 5
camp_ids = list()
for _ in range(NUM_CAMP):
    camp_ids.append(str(uuid.uuid4())[:7])

base_dt = datetime.datetime.strptime('2019/09/08 09:00', "%Y/%m/%d %H:%M")


def create_cost_entry(i=None):
    timestamp = base_dt + \
                datetime.timedelta(
                    hours=i % 24 if i is not None else np.random.randint(0,23)
                )
    camp_id = i % NUM_CAMP if i is not None else np.random.randint(0,NUM_CAMP)
    camp_id = camp_ids[camp_id]
    clicks = np.random.randint(0,100)
    cost = float(np.random.randint(0, 999)) + np.random.ranf()
    csv_entry = "%s,%s,%d,%.3f"%(datetime.datetime.strftime(timestamp, "%Y/%m/%d %H:%M"),
                                 camp_id, clicks, cost)
    return csv_entry

def create_rev_entry(i=None):
    timestamp = base_dt + \
                datetime.timedelta(
                    hours=i % 24 if i is not None else np.random.randint(0, 23)
                )
    camp_id = i % NUM_CAMP if i is not None else np.random.randint(0, NUM_CAMP)
    camp_id = camp_ids[camp_id]
    rev = float(np.random.randint(0, 999)) + np.random.ranf()
    csv_entry = "%s,%s,%.3f" % \
                (datetime.datetime.strftime(timestamp, "%Y/%m/%d %H:%M"),
                 camp_id, rev)
    return csv_entry


if __name__ == "__main__":
    n = 100
    cost_rows = []
    rev_rows = []
    for i in range(n):
        cost_row = create_cost_entry(i)
        cost_rows.append(cost_row + '\n')
        rev_row = create_rev_entry(i)
        rev_rows.append(rev_row + '\n')
    with open("cost.csv", "w") as fdw:
        fdw.write('date,camp_id,clicks,cost\n')
        fdw.writelines(cost_rows)
    with open("rev.csv", "w") as fdw:
        fdw.write('date,camp_id,rev\n')
        fdw.writelines(rev_rows)

