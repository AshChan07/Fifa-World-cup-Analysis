from .common import heading, table


def show(parent):
    heading(parent, 'Premier League table',
        'Hypothetical ranking: 3 points per win, 1 per draw; shootouts count as draws. '
        'Teams played unequal numbers of matches. Ties: points, goal difference, goals, team name. '
        'Green = top 4; pink = bottom 3 (illustrative only).')
    rows = parent.data.standings()
    columns = ['Pos', 'Team', 'P', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts']
    tags = ['ucl' if i < 4 else 'rel' if i >= len(rows)-3 else 'even' if i % 2 == 0 else 'odd' for i in range(len(rows))]
    table(parent, columns, rows[columns].itertuples(index=False, name=None), height=20, tags=tags)
