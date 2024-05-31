import os
import sys
import yaml
import matplotlib.pyplot as plt
import common_matplot_config


def pad_list_with_none(lst, count):
    if lst is None:
        return [None] * count
    elif len(lst) < count:
        new_lst = lst[:]
        new_lst.extend([None] * (count - len(lst)))
        return new_lst
    return lst


def plot_stacked(ax, x, y_values, config, barw=0.5):
    count_bars = len(x)
    count_layers = len(y_values[0])
    bottom_vals = [0] * count_bars
    labels  = pad_list_with_none(config.get('label'), count_layers)
    hatches = pad_list_with_none(config.get('hatch'), count_layers)
    colors  = pad_list_with_none(config.get('color'), count_layers)

    for i in range(count_layers):
        lyr_target_y_vals = [v[i] for v in y_values]
        lyr_height = [max(v - b, 0) for v, b in zip(lyr_target_y_vals, bottom_vals)]
        ax.bar(x, lyr_height, width=barw, alpha=0.99, bottom=bottom_vals,
                label=labels[i], hatch=hatches[i], color=colors[i])
        bottom_vals = lyr_target_y_vals



def multi_experiment(config, ax):
    vspace_between_exp = 0.5
    barw = config.get('bar_width', 0.3)
    x = config['x']
    count_bars = len(x)
    count_subbar = len(config['experiments'])
    pos = [i * (count_subbar * barw + vspace_between_exp)  for i in range(count_bars)]
    for i in range(count_subbar):
        subbar_x = [j + i * barw  for j in pos]
        subbar = config['experiments'][i]
        y_values = subbar['y']
        is_stacked = isinstance(y_values[0], list)
        if not is_stacked:
            ax.bar(subbar_x, y_values, label=subbar.get('label'), width=barw,
                    alpha=0.99, hatch=subbar.get('hatch'), color=subbar.get('color'))
        else:
            plot_stacked(ax, subbar_x, y_values, subbar, barw=barw)

    tick_pos = [j + (count_subbar/2.0 - 0.5)*barw for j in pos]
    ax.set_xticks(tick_pos)
    ax.set_xticklabels(x)


def do_plot(config, ax):
    if 'y' not in config or config['y'] is None:
        multi_experiment(config, ax)
    else:
        barw = config.get('bar_width', 0.3)
        y_values = config['y']
        is_stacked = isinstance(y_values[0], list)
        if not is_stacked:
            ax.bar(config['x'], y_values, width=barw, hatch=config.get('hatch'), alpha=0.99)
        else:
            plot_stacked(ax, config['x'], y_values, config, barw=barw)

        if 'xtick_labels' in config and config['xtick_labels']:
            ax.xaxis.set_ticklabels(config['xtick_labels'])

    if 'ylabel' in config and config['ylabel']:
        ax.set_ylabel(config['ylabel'])
    if 'xlabel' in config and config['xlabel']:
        ax.set_xlabel(config['xlabel'])
    if 'ylim' in config and config['ylim']:
        ax.set_ylim(config['ylim'])
    if 'xlim' in config and config['xlim']:
        ax.set_xlim(config['xlim'])

    if ('xlabel_rotation_deg' in config and
            config['xlabel_rotation_deg']):
        ax.tick_params(axis="x",
                rotation=config['xlabel_rotation_deg'])

    if 'yticks' in config and config['yticks']:
        ax.set_yticks(config['yticks'])
    if 'ytick_labels' in config and config['ytick_labels']:
        ax.set_yticklabels(config['ytick_labels'])

    if 'legend' in config and config['legend']:
        val = config['legend']
        if isinstance(val, dict):
            plt.legend(**val)
        else:
            plt.legend()
    if 'title' in config and config['title']:
        ax.set_title(config['title'])

    # draw annotations
    for a in config.get('annotate', []):
        plt.annotate(**a)
    for a in config.get('arrow', []):
        plt.arrow(**a)

    if config.get('ax_below', False):
        ax.set_axisbelow(True)
    if 'grid' in config:
        ax.grid(config['grid'])


file_path = sys.argv[1]
with open(file_path, 'r') as f:
    config = yaml.safe_load(f)

if 'rc' in config:
    for key, value in config['rc'].items():
        plt.rcParams[key] = value

fig = plt.figure(figsize=config['figsize'])
if 'subplots' in config:
    cols = len(config['subplots'])
    for i in range(cols):
        subconf = config['subplots'][i]
        ax = fig.add_subplot(1, cols, i+1)
        do_plot(subconf, ax)
    # do not let the code after this block use the ax
    ax = None
else:
    ax = fig.add_subplot(1,1,1)
    do_plot(config, ax)
    # do not let the code after this block use the ax
    ax = None


if 'title' in config and config['title']:
    plt.suptitle(config['title'])
plt.tight_layout()

outdir = './out'
if not os.path.isdir(outdir):
    os.mkdir(outdir)
output_file = os.path.join(outdir, config['output'])
plt.savefig(output_file, dpi=300, bbox_inches='tight', pad_inches=0)
plt.show()
