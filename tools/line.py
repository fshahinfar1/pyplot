import os
import sys
import yaml
import math
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import common_matplot_config

ARTIST_MAP = {}


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

    label = tmp.get('label')
    line = ax.plot(x, y, **tmp)
    ARTIST_MAP[label] = line[0]
    line = line[0]

    if has_err_bar:
        ax.errorbar(x, y, yerr=yerr, fmt='none', color='k')

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
            'zoom_box_width', 'zoom_box_height', 'grid', 'annotate',
              'xticks', 'xtick_labels']:
        if x in tmp:
            del tmp[x]
    axins = ax.inset_axes(bounds, xlim=(x1, x2), ylim=(y1, y2), **tmp)
    if zoom_conf.get('grid', False):
        axins.grid()
    # Plot zoomed region inside the zoom_box
    for line in lines:
        plot_a_line(axins, line)
    # Annotate
    if 'annotate' in zoom_conf:
        for a in zoom_conf['annotate']:
            axins.annotate(**a)

    if 'xticks' in zoom_conf and zoom_conf['xticks']:
        axins.xaxis.set_ticks(zoom_conf['xticks'])
    if 'xtick_labels' in zoom_conf and zoom_conf['xtick_labels']:
        axins.xaxis.set_ticklabels(zoom_conf['xtick_labels'])

    ax.indicate_inset_zoom(axins, edgecolor="black")


def do_annotate_line(ax, line_conf):
    ax.axline(**line_conf)

def do_report_delta(ax, conf):
    # Report changes between liens
    delta_conf = conf['report_delta']
    dx = delta_conf.get('dx', 0)
    dy = delta_conf.get('dy', 0)

    sel_map = delta_conf.get('selection_map')
    fontsize = delta_conf.get('fontsize')
    ndigits = delta_conf.get('round')
    sel_delta = delta_conf.get('selection_delta')

    lines = conf['lines']
    base = [line for line in lines if line.get('label') == delta_conf['base_label']][0]
    target = [line for line in lines if line.get('label') == delta_conf['target_label']][0]

    def get_y(line):
        y = line['y']
        if 'scale' in line:
            s = line['scale']
            for i in range(len(y)):
                y[i] *= s
        return y

    A = get_y(base)
    B = get_y(target)

    X = base['x']
    if 'xscale' in base:
        s = line['xscale']
        for i in range(len(X)):
            X[i] *= s

    lbls = []
    for a,b in zip(A,B):
        p=(b-a)/a*100
        if ndigits == 0:
            r = int(p)
        else:
            r = round(p, ndigits=ndigits)
        lbls.append(f'{r}%')

    print(sel_map)
    for i in range(len(X)):
        if sel_map is not None and (i >= len(sel_map) or not sel_map[i]):
            continue
        x = X[i] + dx
        y = B[i] + dy
        if sel_delta and (i < len(sel_delta)):
            x += sel_delta[i][0]
            y += sel_delta[i][1]
        lbl = lbls[i]
        xy = [x, y]
        ax.annotate(xy=xy, text=lbl, fontsize=fontsize)


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

    if 'annotate_line' in subconf:
        for item in subconf['annotate_line']:
            do_annotate_line(ax, item)

    if 'report_delta' in subconf:
        do_report_delta(ax, subconf)

    # draw annotations
    for a in subconf.get('annotate', []):
        plt.annotate(**a)
    for a in subconf.get('arrow', []):
        plt.arrow(**a)

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
    grid_cfg = subconf.get('grid', True)
    if grid_cfg:
        if isinstance(grid_cfg, bool):
            ax.grid()
        else:
            ax.grid(**grid_cfg)
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

if 'legend' in config and config['legend']:
    val = config['legend']
    if isinstance(val, dict):
        if '_artist_from_label' in val:
            tmp = val.pop('_artist_from_label')
            handles = [ARTIST_MAP[x] for x in tmp]
            fig.legend(**val, handles=handles)
        else:
            fig.legend(**val)
    else:
        fig.legend()

padding=config.get('tight_layout', {})
plt.tight_layout(**padding)
# plt.tight_layout()

outdir = './out'
if not os.path.isdir(outdir):
    os.mkdir(outdir)
output_file = os.path.join(outdir, config['output'])
plt.savefig(output_file, dpi=300, bbox_inches='tight',pad_inches = 0)
plt.show()
