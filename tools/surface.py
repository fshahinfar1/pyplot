import sys
import csv
import yaml

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib.ticker as mticker

sys.path.insert(0, '../')
from common import DictObject

with open(sys.argv[1]) as f:
    config = yaml.safe_load(f)
config = DictObject(config)

xs = []
ys = []
zs = []

y_index = {}
length = 0

with open('./data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        x = float(row[config.x_key])
        y = float(row[config.y_key])
        z = float(row[config.z_key])
        # z = float(row['Mpps'])
        if y not in y_index:
            y_index[y] = length
            length += 1
            xs.append([])
            ys.append([])
            zs.append([])
        cur_index = y_index[y]
        xs[cur_index].append(x)
        ys[cur_index].append(y)
        zs[cur_index].append(z)
xs = np.array(xs)
ys = np.array(ys)
zs = np.array(zs)
print(xs)
print(ys)
print(zs)

fig = plt.figure()
ax = fig.add_subplot(projection='3d')
# ax.plot_wireframe(xs, ys, zs)
surf = ax.plot_surface(xs, ys, zs, cmap=cm.coolwarm, antialiased=False)
# surf = ax.plot_surface(xs, ys, zs, cmap='jet')
fig.colorbar(surf)

ax.xaxis.set_ticks(config.x_ticks)
ax.yaxis.set_ticks(config.y_ticks)
ax.zaxis.set_ticks(config.z_ticks)
# ax.zaxis.set_ticks(np.arange(0, 15))

ax.set_xlabel(config.x_label)
ax.set_ylabel(config.y_label)
ax.set_zlabel(config.z_label)

# ax.yaxis.set_major_formatter(mticker.LogFormatter(base=2))
# ax.xaxis.set_major_formatter(mticker.LogFormatter(base=2))
# ax.yaxis.set_major_locator(mticker.LogLocator(base=2))
# ax.xaxis.set_major_locator(mticker.LogLocator(base=2))

ax.set_title(config.title)

plt.show()
