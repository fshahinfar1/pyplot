import os
import sys
import yaml
import math
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import common_matplot_config


def plot_a_line(ax, line):
    """
    @ax:
    @line: config for a line
    """
    tmp = line.copy()
    del tmp['x']
    del tmp['y']
    has_err_bar = False
    yerr = None
    if 'yerr' in tmp:
        has_err_bar = True
        yerr = tmp['yerr']
        del tmp['yerr']

    y = list(line['y'])
    if 'scale' in line:
        del tmp['scale']
        s = line['scale']
        for i in range(len(y)):
            y[i] *= s

        if has_err_bar:
            assert len(yerr) == len(y)
            for i in range(len(yerr)):
                yerr[i] *= s

    x = list(line['x'])
    if 'xscale' in line:
        del tmp['xscale']
        s = line['xscale']
        for i in range(len(x)):
            x[i] *= s

    if 'logscale' in line:
        base = line['logscale']
        for i in range(len(y)):
            y[i] = math.log(y[i], base)
        del tmp['logscale']


    draw_marker_line = False
    if 'marker_dist' in line:
        draw_marker_line = True
        dist = line['marker_dist']
        color = line.get('color')
        marker = line.get('marker')
        markersize = line.get('markersize')

        del tmp['marker_dist']
        tmp['marker'] = None
        tmp['markersize'] = None

    line = ax.plot(x, y, **tmp)
    line = line[0]

    if has_err_bar:
        ax.errorbar(x, y, yerr=yerr)

    if draw_marker_line:
        x2 = [v for i, v in enumerate(x) if i % dist == 0]
        y2 = [v for i, v in enumerate(y) if i % dist == 0]
        ax.plot(x2, y2, marker=marker, markersize=markersize, color=color, linestyle="None")
        # line = Line2D(line)
        # line.set_marker(marker)
        # line.set_markersize(markersize)


def do_zoom(ax, zoom_conf, lines):
    tL = zoom_conf['top_left']
    bR = zoom_conf['bottom_right']
    # Where to put the zoom box
    x0, y0 = zoom_conf['zoom_box_bottom_left']
    W = zoom_conf['zoom_box_width']
    H = zoom_conf['zoom_box_height']
    bounds = [x0, y0, W, H]
    # Sub-region of original axis
    x1, x2, y1, y2 = tL[0], bR[0], bR[1], tL[1]
    #
    tmp = zoom_conf.copy()
    for x in ['top_left', 'bottom_right', 'zoom_box_bottom_left',
            'zoom_box_width', 'zoom_box_height', 'grid']:
        del tmp[x]
    axins = ax.inset_axes(bounds, xlim=(x1, x2), ylim=(y1, y2), **tmp)
    if zoom_conf['grid']:
        axins.grid()
    # Plot zoomed region inside the zoom_box
    for line in lines:
        plot_a_line(axins, line)
    ax.indicate_inset_zoom(axins, edgecolor="black")
    pass


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

    if 'zoom' in subconf:
        for z in subconf['zoom']:
            do_zoom(ax, z, subconf['lines'])

    if 'xlogscale' in subconf:
        ax.set_xscale('log', base=subconf['xlogscale'])
    if 'ylogscale' in subconf:
        ax.set_yscale('log', base=subconf['ylogscale'])

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
    if subconf.get('grid', True):
        ax.grid()
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
