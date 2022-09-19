# just for testing I swear
import os

import manage_db

test = os.get_terminal_size()
print(test.columns)

print("".join([manage_db.add_minus() for i in range(189)]))
