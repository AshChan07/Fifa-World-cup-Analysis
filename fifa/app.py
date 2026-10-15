import logging
from tkinter import ttk
import customtkinter as ctk
from fifa.data import DataStore
from fifa.views import goals, pl_table, comparison, fairplay, possession, correlation

VIEWS = [('Goals per team', goals), ('Premier League table', pl_table),
         ('Player comparison', comparison), ('Fair play', fairplay),
         ('Possession study', possession), ('Correlation / covariance', correlation)]


class App(ctk.CTk):
    def __init__(self, data_directory=None):
        ctk.set_appearance_mode('light')
        super().__init__()
        self.title('FIFA World Cup 2022 — Analysis')
        self.geometry('1280x850')
        self.minsize(1050, 760)
        self.configure(fg_color='#f7f5fa')
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        sidebar = ctk.CTkFrame(self, width=225, corner_radius=0, fg_color='#241133')
        sidebar.grid(row=0, column=0, rowspan=2, sticky='nsew')
        sidebar.grid_propagate(False)
        sidebar.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(sidebar, text='FIFA / 2022', font=('Arial', 25, 'bold'), text_color='white').grid(row=0, column=0, padx=20, pady=(30, 4))
        ctk.CTkLabel(sidebar, text='WORLD CUP ANALYSIS', font=('Arial', 11), text_color='#c6b4d5').grid(row=1, column=0, pady=(0, 30))
        self.buttons = []
        for i, (label, module) in enumerate(VIEWS):
            button = ctk.CTkButton(sidebar, text=label, anchor='w', height=44,
                fg_color='transparent', hover_color='#5a3376', font=('Arial', 13),
                command=lambda view=module, title=label: self.navigate(view, title))
            button.grid(row=i+2, column=0, padx=12, pady=5, sticky='ew')
            self.buttons.append(button)
        sidebar.grid_rowconfigure(8, weight=1)
        ctk.CTkButton(sidebar, text='Exit', command=self.destroy, fg_color='#513365').grid(row=9, column=0, padx=20, pady=25, sticky='ew')
        self.content = ctk.CTkFrame(self, fg_color='#f7f5fa', corner_radius=0)
        self.content.grid(row=0, column=1, sticky='nsew')
        self.status = ctk.CTkLabel(self, text='', anchor='w', font=('Arial', 12), wraplength=950)
        self.status.grid(row=1, column=1, sticky='ew', padx=24, pady=8)
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('Treeview', font=('Arial', 12), rowheight=28, background='white', fieldbackground='white')
        style.configure('Treeview.Heading', font=('Arial', 12, 'bold'), foreground='white', background='#3D195B')
        style.map('Treeview', background=[('selected', '#62407d')], foreground=[('selected', 'white')])
        self.content.set_status = self.set_status
        try:
            self.content.data = DataStore(data_directory) if data_directory is not None else DataStore()
        except (OSError, ValueError, KeyError) as error:
            self.set_status(f'Could not load data: {error}. Check the five CSV files and restart.')
            for button in self.buttons:
                button.configure(state='disabled')
            ctk.CTkLabel(self.content, text='Data unavailable', font=('Arial', 28)).pack(pady=80)
        else:
            self.navigate(goals, 'Goals per team')

    def set_status(self, message):
        self.status.configure(text=message)

    def navigate(self, module, title):
        for widget in self.content.winfo_children():
            widget.destroy()
        for button, (_, view) in zip(self.buttons, VIEWS):
            button.configure(fg_color='#5a3376' if view is module else 'transparent')
        self.set_status(f'{title} · FIFA World Cup 2022 · bundled historical data')
        try:
            module.show(self.content)
        except Exception as error:
            logging.exception('Unable to render %s', title)
            self.set_status(f'Unable to display {title}: {error}')

    def report_callback_exception(self, exception, value, traceback):
        logging.error('GUI callback failed', exc_info=(exception, value, traceback))
        self.set_status(f'Unable to complete action: {value}')
