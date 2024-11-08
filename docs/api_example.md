---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.14.5
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

# Storing data in database

First generate a fresh database built using latest source code:

```python
import logging
import sys
logging.basicConfig(format='%(asctime)s | %(levelname)s : %(message)s',
                    level=logging.INFO, stream=sys.stdout)
```

```python
# Check your environment
print(sys.path)
```

Create a database with:

```python
from solvency2_data.eiopa_data import get_workspace
from solvency2_data.sqlite_handler import EiopaDB
database = get_workspace()['database']
db = EiopaDB(database)
```

Reset the database with:

```python
# Hard reset of DB - deletes the file and all stored data and rebuilds empty DB
db.reset()
```

Now populate it for every month:

```python
import solvency2_data
solvency2_data.refresh()
```

Now this can be indirectly queried using the API

```python
import solvency2_data
from datetime import date
ref_date = date(2020, 12, 31)
rfr = solvency2_data.get(ref_date)
meta = solvency2_data.get(ref_date, 'meta')
spr = solvency2_data.get(ref_date, 'spreads')
gov = solvency2_data.get(ref_date, 'govies')
sym_adj =  solvency2_data.get(ref_date, 'sym_adj')
rfr.head()
```

Or directly queried via a SQL expression:

```python
import pandas as pd
sql = "SELECT * FROM rfr"
df = pd.read_sql(sql, con=db.conn)
df = df.loc[df.scenario=='base',['currency_code','ref_date', 'duration', 'spot']]
df.head()
```

```python
month_list = df.ref_date.drop_duplicates().to_list()
month_list[:5]
```

```python
df['ref_date'] = df.ref_date.apply(lambda x: month_list.index(x))
df.head()
```

```python
eurs = df.loc[df.currency_code=='EUR', ['ref_date', 'duration', 'spot']].set_index('ref_date')
gbps = df.loc[df.currency_code=='GBP', ['ref_date', 'duration', 'spot']].set_index('ref_date')
chfs = df.loc[df.currency_code=='CHF', ['ref_date', 'duration', 'spot']].set_index('ref_date')
usds = df.loc[df.currency_code=='USD', ['ref_date', 'duration', 'spot']].set_index('ref_date')
eurs.head()
```

```python
list(eurs.loc[66, 'spot'].values)[:5]
```

## Now have some fun :p

```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from IPython.display import HTML

# plt.style.use('ggplot')
plt.xkcd()

fig, ax = plt.subplots(figsize=(7, 4))
ax.set(xlim=(0, 100), ylim=(-0.01, 0.04))

date_text = ax.text(0.02, 0.9, '', transform=ax.transAxes)
#plt.tight_layout()
plt.gcf().subplots_adjust(bottom=0.15, left=0.15)
plt.title('EIOPA Spots')

x = list(range(1,151))
#plt.xticks(ticks = x)
plt.xlabel('duration (years)')
plt.locator_params(axis='x', nbins=10)

percentage = np.array(list(map("{:.1%}".format, 0.005 * np.arange(-2, 10))))
plt.yticks(ticks=0.005 * np.arange(-2, 10), labels=percentage)
plt.ylabel('risk free spots')

date_text.set_text(month_list[0])

eur_start = ax.plot(x, eurs.loc[0,'spot'].values, color='b', ls='dashed', lw=2)[0]
eur_line = ax.plot(x, eurs.loc[0,'spot'].values, color='b', lw=2)[0]

gbp_start = ax.plot(x, gbps.loc[0, 'spot'].values, color='y', ls='dashed', lw=2)[0]
gbp_line = ax.plot(x, gbps.loc[0, 'spot'].values, color='y', lw=2)[0]

chf_start = ax.plot(x, chfs.loc[0, 'spot'].values, color='m', ls='dashed', lw=2)[0]
chf_line = ax.plot(x, chfs.loc[0, 'spot'].values, color='m', lw=2)[0]

ax.legend((eur_line, chf_line, gbp_line), ('eur', 'chf', 'gbp'), loc='lower right')
def animate(i):
    key = min(i, 66)
    date_text.set_text(month_list[key])
    eur_line.set_ydata(list(eurs.loc[key, 'spot'].values))
    gbp_line.set_ydata(list(gbps.loc[key, 'spot'].values))
    chf_line.set_ydata(list(chfs.loc[key, 'spot'].values))

anim = FuncAnimation(
    fig, animate, interval=100, frames=67 + 15)

plt.draw()
#plt.show()
HTML(anim.to_html5_video())
```

```python

```
