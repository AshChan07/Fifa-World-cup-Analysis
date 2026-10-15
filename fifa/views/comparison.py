import tkinter as tk
from tkinter import ttk
import numpy as np
from fifa.data import PLAYER_METRICS
from .common import heading, controls, chart_area, figure, embed, table, PURPLE, TEAL


def show(parent):
    heading(parent, 'Player comparison',
        'Tournament totals. Radar axes show % of the tournament maximum for each metric; '
        'raw values below. Missing values are shown as N/A, not zero.')
    selectors = controls(parent)
    area = chart_area(parent)
    raw = table(parent, ['Metric', 'Player 1', 'Player 2'], [], height=6)
    teams, players, player_boxes = [], [], []
    names = sorted(parent.data.players.team.unique())

    def render(*_):
        try:
            selected = [parent.data.player(teams[i].get(), players[i].get()) for i in range(2)]
        except ValueError as error:
            parent.set_status(str(error))
            return
        fig, ax = figure(polar=True)
        angles = np.linspace(0, 2*np.pi, len(PLAYER_METRICS), endpoint=False)
        angles = np.append(angles, angles[0])
        maxima = parent.data.players[PLAYER_METRICS].max().replace(0, 1)
        for row, color in zip(selected, [PURPLE, TEAL]):
            values = (row[PLAYER_METRICS].astype(float) / maxima * 100).to_numpy(dtype=float)
            values = np.append(values, values[0])
            ax.plot(angles, values, color=color, linewidth=2, label=f'{row.player} ({row.team})')
            ax.fill(angles, values, color=color, alpha=.12)
        ax.set_xticks(angles[:-1], [m.replace('_', ' ').title() for m in PLAYER_METRICS], fontsize=10)
        ax.set_ylim(0, 100)
        ax.set_yticks([25, 50, 75, 100], ['25%', '50%', '75%', '100%'], fontsize=8)
        ax.legend(loc='upper right', bbox_to_anchor=(1.7, 1.1), fontsize=9)
        embed(area, fig)
        raw.delete(*raw.get_children())
        for metric in PLAYER_METRICS:
            values = ['N/A' if np.isnan(float(row[metric])) else f'{float(row[metric]):g}' for row in selected]
            raw.insert('', 'end', values=[metric.replace('_', ' ').title()] + values)
        raw.heading('Player 1', text=selected[0].player)
        raw.heading('Player 2', text=selected[1].player)
        parent.set_status('Player comparison ready.')

    def update_players(index):
        options = sorted(parent.data.players.loc[parent.data.players.team == teams[index].get(), 'player'])
        player_boxes[index]['values'] = options
        preferred = 'Lionel Messi' if index == 0 else 'Kylian Mbappé'
        players[index].set(preferred if preferred in options else options[0] if options else '')
        if len(player_boxes) == 2:
            render()

    for i, default in enumerate(['Argentina', 'France']):
        group = ttk.Frame(selectors)
        group.pack(side='left', fill='x', expand=True, padx=(0, 20))
        ttk.Label(group, text=f'Player {i+1} • team and player').pack(anchor='w')
        teams.append(tk.StringVar(value=default if default in names else names[0]))
        players.append(tk.StringVar())
        team_box = ttk.Combobox(group, textvariable=teams[i], values=names, state='readonly')
        team_box.pack(fill='x', pady=3)
        team_box.bind('<<ComboboxSelected>>', lambda _, index=i: update_players(index))
        player_box = ttk.Combobox(group, textvariable=players[i], state='readonly')
        player_box.pack(fill='x', pady=3)
        player_box.bind('<<ComboboxSelected>>', render)
        player_boxes.append(player_box)
        update_players(i)
    render()
