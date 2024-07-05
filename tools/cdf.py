import os
import sys
import yaml
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import common_matplot_config


def plot_a_line(ax, line):
    """
    @ax:
    @line: config for a line
    """
    tmp = line.copy()
    del tmp['data']

    data = list(line['data'])
    if 'scale' in line:
        del tmp['scale']
        s = line['scale']
        for i in range(len(y)):
            data[i] *= s
    line = ax.ecdf(data, **tmp)


file_path = sys.argv[1]
with open(file_path, 'r') as f:
    config = yaml.safe_load(f)

fig = plt.figure(figsize=config['figsize'])
cols = len(config['subplots'])
for i in range (cols):
    subconf = config['subplots'][i]
    ax = fig.add_subplot(1,cols,i+1)
    for line in subconf['lines']:
        plot_a_line(ax, line)

    if 'ylabel' in subconf and subconf['ylabel']:
        ax.set_ylabel(subconf['ylabel'])
    if 'xlabel' in subconf and subconf['xlabel']:
        ax.set_xlabel(subconf['xlabel'])
    if 'ylim' in subconf and subconf['ylim']:
        ax.set_ylim(subconf['ylim'])
    if 'xlim' in subconf and subconf['xlim']:
        ax.set_xlim(subconf['xlim'])
    if 'xticks' in subconf and subconf['xticks']:
        ax.xaxis.set_ticks(subconf['xticks'])
    if 'xtick_labels' in subconf and subconf['xtick_labels']:
        ax.xaxis.set_ticklabels(subconf['xtick_labels'])
    if 'yticks' in subconf and subconf['yticks']:
        ax.yaxis.set_ticks(subconf['yticks'])
    if 'ytick_labels' in subconf and subconf['ytick_labels']:
        ax.yaxis.set_ticklabels(subconf['ytick_labels'])

    if ('xlabel_rotation_deg' in subconf and
            subconf['xlabel_rotation_deg']):
        ax.tick_params(axis="x",
                rotation=subconf['xlabel_rotation_deg'])

    if 'xlogscale' in subconf:
        ax.set_xscale('log', base=subconf['xlogscale'])

    if 'legend' in subconf and subconf['legend']:
        if isinstance(subconf['legend'], dict):
            if subconf['legend'].get('outside', False):
                subconf['legend'].pop('outside')
                fig.legend(**subconf['legend'])
            else:
                ax.legend(**subconf['legend'])
        else:
            ax.legend()

    ax.set_axisbelow(True)
    ax.grid()
    # ax.legend()
    if 'title' in subconf and subconf['title']:
        ax.set_title(subconf['title'])

if 'suptitle' in config and config['suptitle']:
    plt.suptitle(config['suptitle'])
if 'rc' in config:
    for param in config['rc']:
        tmp = param.copy()
        del tmp['name']
        plt.rc(param['name'], **tmp)

# draw annotations
for a in config.get('annotate', []):
    plt.annotate(**a)
for a in config.get('arrow', []):
    plt.arrow(**a)

# padding=config.get('tight_layout', {})
# plt.tight_layout(**padding)
plt.tight_layout()

outdir = './out'
if not os.path.isdir(outdir):
    os.mkdir(outdir)
output_file = os.path.join(outdir, config['output'])
plt.savefig(output_file, dpi=300, bbox_inches='tight',pad_inches = 0)
plt.show()
