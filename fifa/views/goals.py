from .common import heading, controls, chart_area, figure, embed, toggle, team_labels, PURPLE


def show(parent):
    heading(parent, 'Goals per team', 'Tournament totals • all 64 matches • penalty shootout goals excluded')
    bar = controls(parent)
    area = chart_area(parent)
    rows = parent.data.standings().sort_values(['GF', 'Team'], ascending=[False, True])
    def render(mode):
        fig, ax = figure()
        labels = team_labels(parent.data, rows.Team)
        if mode == 'Bar':
            ax.bar(labels, rows.GF, color=PURPLE)
        else:
            ax.plot(labels, rows.GF, color=PURPLE, marker='o')
        ax.set(ylabel='Goals', xlabel='Team', title='Goals scored at World Cup 2022')
        ax.tick_params(axis='x', labelrotation=60)
        ax.grid(axis='y', alpha=.18)
        embed(area, fig)
    toggle(bar, ['Bar', 'Line'], render)
    render('Bar')
