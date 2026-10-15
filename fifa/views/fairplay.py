import numpy as np
from .common import heading, controls, chart_area, figure, embed, toggle, team_labels, PURPLE


def show(parent):
    heading(parent, 'Fair play', 'Cards across the tournament. Score = yellow + 3 × red; lower is better. This is a custom score, not FIFA’s official tie-breaker.')
    bar = controls(parent)
    area = chart_area(parent)
    rows = parent.data.discipline()
    def render(mode):
        fig, ax = figure()
        x = np.arange(len(rows))
        if mode == 'Cards':
            ax.bar(x-.2, rows['Yellow cards'], .4, color='#dca800', label='Yellow cards')
            ax.bar(x+.2, rows['Red cards'], .4, color='#c53d55', label='Red cards')
            ax.legend()
        else:
            ax.bar(x, rows.Score, color=PURPLE)
        ax.set_xticks(x, team_labels(parent.data, rows.Team), rotation=60)
        ax.set(ylabel='Cards' if mode == 'Cards' else 'Weighted card score', xlabel='Team (lowest score first)')
        embed(area, fig)
    toggle(bar, ['Cards', 'Fair play score'], render)
    render('Cards')
