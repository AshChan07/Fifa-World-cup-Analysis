import numpy as np
from matplotlib import colormaps
from .common import heading, controls, chart_area, figure, embed, toggle


def show(parent):
    heading(parent, 'Correlation & covariance',
        '10 metrics · 128 team-match observations (paired within 64 matches). '
        'Correlation ranges from −1 to +1; covariance depends on units. Neither implies causation.')
    bar = controls(parent)
    area = chart_area(parent)
    def render(mode):
        matrix = parent.data.matrix(covariance=mode == 'Covariance')
        values = matrix.to_numpy()
        fig, ax = figure()
        limit = max(float(np.nanmax(np.abs(values))), 1e-12) if mode == 'Covariance' else 1
        cmap = colormaps['RdBu_r'].copy()
        cmap.set_bad('#dddddd')
        im = ax.imshow(values, cmap=cmap, vmin=-limit, vmax=limit)
        ax.set_xticks(range(len(matrix)), matrix.columns, rotation=45, ha='right', fontsize=9)
        ax.set_yticks(range(len(matrix)), matrix.index, fontsize=9)
        for (i, j), value in np.ndenumerate(values):
            label = 'N/A' if np.isnan(value) else f'{value:.2g}' if mode == 'Covariance' else f'{value:.2f}'
            ax.text(j, i, label, ha='center', va='center', fontsize=8,
                    color='white' if abs(value) > limit*.55 else '#25202b')
        fig.colorbar(im, ax=ax, shrink=.8, label=mode)
        ax.set_title(mode + (' (sample, n−1)' if mode == 'Covariance' else ' (Pearson)'))
        embed(area, fig)
    toggle(bar, ['Correlation', 'Covariance'], render)
    render('Correlation')
