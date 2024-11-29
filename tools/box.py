import os
import argparse
import yaml
import matplotlib.pyplot as plt
import common_matplot_config


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', type=str, help="path to the yaml file")
    args = parser.parse_args()
    return args


def read_data_from_file(path):
    data = []
    with open(path, 'r') as f:
        for a in f:
            try:
                b = float(a)
            except:
                print('Error converting a line of data to float: Line ignored!')
                continue
            data.append(b)
    return data


args = parse()
with open(args.config_file) as f:
    conf = yaml.safe_load(f)

figsize = conf['figsize']
fig = plt.figure(figsize=figsize)
rows = 1
cols = 1
# cols = conf.get('columns', 1)

for i in range(cols):
    col = i + 1
    ax = fig.add_subplot(rows,cols,col)
    barwidth = conf.get('bar_width', 0.35)
    labels = conf['labels']
    tmp_vals = conf['values']
    vals = []
    for x in tmp_vals:
        if isinstance(x, list):
            vals.append(x)
        elif isinstance(x, str):
            t = read_data_from_file(x)
            vals.append(t)
        else:
            raise Exception('Unsupported data-type for value')

    if 'scale' in conf:
        s = conf['scale']
        vals = [[s * y for y in x] for x in vals]


    mp = conf.get('medianprops', {})
    bp = ax.boxplot(vals, labels=labels, widths=barwidth,
            showfliers=conf.get('showfliers', True), medianprops=mp)
    if conf.get('grid', 0):
        ax.grid(True, linestyle='dotted')

    # add meidan labels
    x_offset = (((barwidth / 2)) / figsize[0]) * 1.5
    for l in bp['medians']:
        xs, ys = l.get_data()
        x = xs[1] + x_offset
        y = ys.mean() # mean of begining and end of median line y value
        p = ax.transData.transform((x,y))
        p = ax.transAxes.inverted().transform(p)
        # print(p)
        percision = conf.get('label_percision', 0)
        yy = round(y, ndigits=percision)
        if percision == 0:
            yy = int(yy)
        plt.text(p[0], p[1], yy, color='black')

    if 'yticks' in conf and conf['yticks']:
        ax.yaxis.set_ticks(conf['yticks'])
    # apply y axis limits
    if 'ylims' in conf and conf['ylims'] is not None:
        ax.set_ylim(conf['ylims'])
    if 'ylabel' in conf and conf['ylabel'] is not None:
        ylabel = conf['ylabel']
        ax.set_ylabel(ylabel)

plt.tight_layout()

outdir = './out'
if not os.path.isdir(outdir):
    os.mkdir(outdir)
output_file = os.path.join(outdir, conf['output'])
plt.savefig(output_file, dpi=300, bbox_inches='tight',pad_inches = 0)
plt.show()
