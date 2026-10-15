from .common import heading, chart_area, figure, embed, PURPLE, TEAL


def show(parent):
    outcomes = parent.data.possession_outcomes()
    heading(parent, 'Does possession win matches?',
        f'Each match counted once. Outcomes for the team with higher possession; '
        f'{outcomes["Equal possession"]} equal-possession matches excluded. '
        'Shootouts count as draws. Association does not establish causation.')
    fig, ax = figure()
    values = [outcomes[key] for key in ['Won', 'Drew', 'Lost']]
    bars = ax.bar(['Won', 'Drew', 'Lost'], values, color=[TEAL, '#92849f', PURPLE], width=.55)
    total = sum(values)
    ax.bar_label(bars, labels=[f'{v} ({v/total:.0%})' if total else '0' for v in values], padding=5)
    ax.set(ylabel='Matches', title='Result of the team with more possession', ylim=(0, max(values, default=0)+6))
    embed(chart_area(parent), fig)
