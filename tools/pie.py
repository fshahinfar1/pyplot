import os
import sys
import yaml
import matplotlib.pyplot as plt
import math
from matplotlib.patches import ConnectionPatch
import common_matplot_config


def format_text(pct, allvals):
    absolute = int(round(pct/100.*sum(allvals)))
    return "{:.1f}%\n({:d})".format(pct, absolute)


def plot_pie(ax, config):
    x = config['pie']['x']
    wedges, texts, autotexts = ax.pie(**config['pie'],
            autopct=lambda pct: format_text(pct, x))
    ax.legend(loc='upper left', bbox_to_anchor=(-0.3, 1.00))
    if 'inside_text_prop' in config:
        plt.setp(autotexts, **config['inside_text_prop'])
    return wedges, texts, autotexts


def plot_bar(ax, config):
    stack = config['bar']['stack']
    labels = config['bar']['labels']
    unit = config['bar']['unit']
    count = len(stack)
    total = sum(stack)
    bottom = total
    width = 0.2
    for i, (value, label) in enumerate(zip(stack, labels)):
        bottom -= value
        alpha = min(1 - (1 / count) * i + 0.1, 1)
        bc = ax.bar(0, value, bottom=bottom, label=label,
                color='tab:blue', alpha=alpha, width=width)
        ax.bar_label(bc,
                labels=[f"{value} {unit}\n({value/total:.0%})"],
                label_type='center', color='wheat')
    ax.set_title(config.get('title'))
    ax.set_xlim(- 1.5 * width, 1.5 * width)
    ax.axis('off')
    ax.legend(loc='upper right', bbox_to_anchor=(1.25, 0.80))


def main():
    file_path = sys.argv[1]
    with open(file_path, 'r') as f:
        config = yaml.safe_load(f)

    if 'rc' in config:
        for key, value in config['rc'].items():
            plt.rcParams[key] = value

    count_subfig = 1
    if 'bar' in config:
        count_subfig = 2

    figsize = config.get('figsize', [4,4])
    fig = plt.figure(figsize=figsize)
    ax1 = fig.add_subplot(1,count_subfig,1)

    wedges, _, _ = plot_pie(ax1, config)

    if 'bar' in config:
        ax2 =  fig.add_subplot(1, count_subfig, 2)
        plot_bar(ax2, config)

        start_rotate = config['pie']['startangle']
        pie_data_index = config['bar']['pie_chart_index']
        bar_height = sum(config['bar']['stack'])
        line_width = 1
        line_color = [0,0,0]

        # use ConnectionPatch to draw lines between the two plots
        theta1 = wedges[pie_data_index].theta1
        theta2 = wedges[pie_data_index].theta2
        center = wedges[1].center
        r = wedges[1].r

        def draw_line(theta, bar_pos):
            # draw top connecting line
            x = r * math.cos(math.pi / 180 * theta) + center[0]
            y = r * math.sin(math.pi / 180 * theta) + center[1]
            con = ConnectionPatch(xyA=bar_pos, coordsA=ax2.transData,
                                  xyB=(x, y), coordsB=ax1.transData)
            con.set_color(line_color)
            con.set_linewidth(line_width)
            ax2.add_artist(con)

        bar_bottom = (-0.1, 0)
        bar_top = (-0.1, bar_height)
        draw_line(theta1, bar_bottom)
        draw_line(theta2, bar_top)

    if 'suptitle' in config and config['suptitle']:
        plt.suptitle(config['suptitle'])

    fig.subplots_adjust(wspace=0)
    # plt.tight_layout()

    outdir = './out'
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    output_file = os.path.join(outdir, config['output'])
    plt.savefig(output_file, dpi=300)
    plt.show()


if __name__ == '__main__':
    main()
