import yaml
import matplotlib.pyplot as plt
import argparse
import numpy as np


def parse():
    parser = argparse.ArgumentParser('Histogram plotting tool')
    parser.add_argument('config_file', type=str, help='path to config file')
    args = parser.parse_args()
    return args


def main():
    args = parse()
    with open(args.config_file) as f:
        conf = yaml.safe_load(f)

    figsize = conf.get('figsize')
    fig = plt.figure(figsize = figsize)
    ax = fig.add_subplot(1,1,1)
    for data in conf.get('data', tuple()):
        if 'file' not in data:
            raise Exception('field with the name of "file" not found in config file')
        d = np.loadtxt(data['file'])
        if 'plot_params' in data:
            params = data['plot_params']
        else:
            params = {}
        ax.hist(d, **params)

    if 'ylim' in conf and conf['ylim']:
        ax.set_ylim(conf['ylim'])
    if 'xlim' in conf and conf['xlim']:
        ax.set_xlim(conf['xlim'])

    fig.tight_layout()
    fig.legend()
    ax.grid(True)
    if 'output' in conf:
        plt.savefig(conf['output'], dpi=300)
    plt.show()


if __name__ == '__main__':
    main()
