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
    vals = conf['values']
    bp = ax.boxplot(vals, labels=labels, widths=barwidth)
    if conf.get('grid', 0):
        ax.grid(True, linestyle='dotted')

    # add meidan labels
    for l in bp['medians']:
        xs, ys = l.get_data()
        x = xs[1] * 1.05
        y = ys.mean() # mean of begining and end of median line y value
        p = ax.transData.transform((x,y))
        p = ax.transAxes.inverted().transform(p)
        # print(p)
        plt.text(p[0], p[1], f'{y:.0f}', color='black')

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
plt.savefig(output_file, dpi=300)
plt.show()
