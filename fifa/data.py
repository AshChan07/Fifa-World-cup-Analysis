"""Load source files once and provide independently testable analysis."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
METRICS = {
    'Goals': 'number_of_goals', 'Possession %': 'possession',
    'Shots': 'total_attempts', 'On target': 'on_target_attempts',
    'Completed passes': 'passes_completed', 'Fouls': 'fouls_against',
    'Yellow cards': 'yellow_cards', 'Red cards': 'red_cards',
    'Offsides': 'offsides', 'Corners': 'corners',
}
PLAYER_METRICS = ['goals', 'assists', 'shots', 'shots_on_target', 'tackles', 'tackles_won']


class DataStore:
    def __init__(self, directory=ROOT):
        directory = Path(directory)
        frames = {name: pd.read_csv(directory / f'{name}.csv') for name in
                  ('matches', 'results', 'player_stats', 'player_shooting', 'player_defense')}
        self.matches = frames['matches']
        self.results = frames['results']  # Retained source; match statistics are authoritative.
        sides = []
        for side, opponent in ((1, 2), (2, 1)):
            frame = pd.DataFrame({'match_id': self.matches.index,
                                  'Team': self.matches[f'team{side}'].str.title(),
                                  'Opponent': self.matches[f'team{opponent}'].str.title()})
            for label, source in METRICS.items():
                frame[label] = pd.to_numeric(self.matches[f'{source}_team{side}']
                                             .astype(str).str.rstrip('%'), errors='raise')
            frame['GA'] = pd.to_numeric(self.matches[f'number_of_goals_team{opponent}'])
            sides.append(frame)
        self.team_matches = pd.concat(sides, ignore_index=True)
        if self.team_matches[list(METRICS) + ['GA']].isna().any().any():
            raise ValueError('Match statistics contain missing values.')
        names = sorted(self.team_matches.Team.unique())
        # Unique abbreviations rather than ambiguous first-three-letter labels.
        codes = 'ARG AUS BEL BRA CMR CAN CRC CRO DEN ECU ENG FRA GER GHA IRN JPN MEX MAR NED POL POR QAT KSA SEN SRB KOR ESP SUI TUN USA URU WAL'.split()
        code_names = ['Argentina','Australia','Belgium','Brazil','Cameroon','Canada','Costa Rica','Croatia','Denmark','Ecuador','England','France','Germany','Ghana','Iran','Japan','Mexico','Morocco','Netherlands','Poland','Portugal','Qatar','Saudi Arabia','Senegal','Serbia','South Korea','Spain','Switzerland','Tunisia','United States','Uruguay','Wales']
        code_map = dict(zip(code_names, codes))
        code_map['Korea Republic'] = 'KOR'
        self.teams = pd.DataFrame({'display': names, 'upper': [n.upper() for n in names],
                                   'short': [code_map.get(n, n[:3].upper()) for n in names]})
        self.players = frames['player_stats'][['team', 'player', 'goals', 'assists']].copy()
        for source, columns in [('player_shooting', ['shots', 'shots_on_target']),
                                 ('player_defense', ['tackles', 'tackles_won'])]:
            self.players = self.players.merge(frames[source][['team', 'player'] + columns],
                                               on=['team', 'player'], how='left', validate='one_to_one')
        self.players['team'] = self.players['team'].replace({'IR Iran': 'Iran', 'South Korea': 'Korea Republic'})
        self.players[PLAYER_METRICS] = self.players[PLAYER_METRICS].apply(pd.to_numeric, errors='raise')

    def standings(self):
        rows = self.team_matches.copy()
        rows['W'] = (rows.Goals > rows.GA).astype(int)
        rows['D'] = (rows.Goals == rows.GA).astype(int)
        rows['L'] = (rows.Goals < rows.GA).astype(int)
        table = rows.groupby('Team').agg(P=('match_id', 'size'), W=('W', 'sum'),
            D=('D', 'sum'), L=('L', 'sum'), GF=('Goals', 'sum'), GA=('GA', 'sum')).reset_index()
        table['GD'] = table.GF - table.GA
        table['Pts'] = 3 * table.W + table.D
        table = table.sort_values(['Pts', 'GD', 'GF', 'Team'], ascending=[False, False, False, True])
        table.insert(0, 'Pos', range(1, len(table) + 1))
        return table.reset_index(drop=True)

    def discipline(self):
        table = self.team_matches.groupby('Team')[['Yellow cards', 'Red cards']].sum()
        table['Score'] = table['Yellow cards'] + 3 * table['Red cards']
        return table.sort_values(['Score', 'Yellow cards']).reset_index()

    def possession_outcomes(self):
        rows = self.team_matches.merge(self.team_matches[['match_id', 'Team', 'Possession %']],
            left_on=['match_id', 'Opponent'], right_on=['match_id', 'Team'], suffixes=('', '_opponent'),
            validate='one_to_one')
        higher = rows[rows['Possession %'] > rows['Possession %_opponent']]
        return {'Won': int((higher.Goals > higher.GA).sum()),
                'Drew': int((higher.Goals == higher.GA).sum()),
                'Lost': int((higher.Goals < higher.GA).sum()),
                'Equal possession': int((rows['Possession %'] == rows['Possession %_opponent']).sum() // 2)}

    def matrix(self, covariance=False):
        values = self.team_matches[list(METRICS)]
        return values.cov() if covariance else values.corr()

    def player(self, team, name):
        rows = self.players[(self.players.team == team) & (self.players.player == name)]
        if len(rows) != 1:
            raise ValueError('Choose a player from the selected team.')
        return rows.iloc[0]
