import yaml
import matplotlib.pyplot as plt
import argparse
import numpy as np


def parse():
    parser = argparse.ArgumentParser('CDF plot tool')
    parser.add_argument('config_file', type=str, help='path to config file')
    args = parser.parse_args()
    return args


def ecdf(x, n):
    x = sorted(x)
    def _ecdf(v):
        # side='right' because we want Pr(x <= v)
        return (np.searchsorted(x, v, side='right') ) / n
    return _ecdf


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
        k = len(d)
        _max = np.max(d)
        x = np.arange(0, _max, (_max - 0) / 1000)
        y = ecdf(d, k)(x)
        if 'plot_params' in data:
            params = data['plot_params']
        else:
            params = {}
        ax.plot(x, y, **params)

    fig.tight_layout()
    ax.legend()
    ax.grid(True)
    if 'output' in conf:
        plt.savefig(conf['output'], dpi=300)
    plt.show()


if __name__ == '__main__':
    main()
