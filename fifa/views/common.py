from tkinter import ttk
import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

PURPLE = '#3D195B'
TEAL = '#008577'


def heading(parent, title, subtitle):
    ctk.CTkLabel(parent, text=title, font=('Arial', 27, 'bold'), text_color=PURPLE).pack(anchor='w', padx=24, pady=(20, 4))
    ctk.CTkLabel(parent, text=subtitle, font=('Arial', 13), wraplength=900, justify='left').pack(anchor='w', padx=24, pady=(0, 12))


def controls(parent):
    frame = ctk.CTkFrame(parent, fg_color='transparent')
    frame.pack(fill='x', padx=24, pady=6)
    return frame


def chart_area(parent):
    frame = ctk.CTkFrame(parent, fg_color='white')
    frame.pack(fill='both', expand=True, padx=20, pady=12)
    return frame


def figure(polar=False):
    fig = Figure(figsize=(9, 5), dpi=100, layout='constrained', facecolor='white')
    return fig, fig.add_subplot(111, polar=polar)


def embed(parent, fig):
    for widget in parent.winfo_children():
        widget.destroy()
    old = getattr(parent, '_figure', None)
    if old is not None:
        old.clear()
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)
    parent._figure = fig
    parent._plot_canvas = canvas


def table(parent, columns, rows, height=8, tags=None):
    frame = ttk.Frame(parent)
    frame.pack(fill='both', expand=True, padx=24, pady=12)
    tree = ttk.Treeview(frame, columns=columns, show='headings', height=height)
    vertical = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
    horizontal = ttk.Scrollbar(frame, orient='horizontal', command=tree.xview)
    tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    tree.grid(row=0, column=0, sticky='nsew')
    vertical.grid(row=0, column=1, sticky='ns')
    horizontal.grid(row=1, column=0, sticky='ew')
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor='w' if col in ('Team', 'Metric') else 'center',
                    width=180 if col in ('Team', 'Metric') else 70, minwidth=60)
    for tag, color in [('even', '#f2eef6'), ('odd', '#ffffff'), ('ucl', '#e6f4ea'), ('rel', '#fde7e9')]:
        tree.tag_configure(tag, background=color)
    for i, row in enumerate(rows):
        tree.insert('', 'end', values=list(row), tags=(tags[i] if tags else ('even' if i % 2 == 0 else 'odd'),))
    return tree


def toggle(parent, values, callback):
    widget = ctk.CTkSegmentedButton(parent, values=values, command=callback, selected_color=PURPLE)
    widget.set(values[0])
    widget.pack(side='left', padx=(0, 12))
    return widget


def team_labels(data, names):
    return data.teams.set_index('display').loc[names, 'short'].tolist()
