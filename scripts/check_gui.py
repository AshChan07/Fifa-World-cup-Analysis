"""Exercise real widgets; optionally capture the app window on macOS.
Run: python scripts/check_gui.py [--screenshots]
Requires a graphical desktop. Screenshots use macOS screencapture.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import subprocess
import os
import time

if '--screenshots' in sys.argv:
    if sys.platform != 'darwin':
        raise SystemExit('Automatic screenshots currently require macOS. Run without --screenshots for GUI checks.')
    try:
        import Quartz
    except ImportError:
        raise SystemExit('Install the screenshot helper: python -m pip install pyobjc-framework-Quartz') from None
    if not Quartz.CGPreflightScreenCaptureAccess():
        raise SystemExit(
            'macOS has not granted screen-recording access to this process.\n'
            'Open System Settings > Privacy & Security > Screen & System Audio Recording '
            '(called Screen Recording on older macOS versions).\n'
            'Enable the app running this command: Terminal, iTerm, your editor, or Codex.\n'
            'Fully quit and reopen that app, then rerun this command. '
            'Enabling Terminal does not grant access to Codex, or vice versa.\n'
            'No screenshots were captured.'
        )

import customtkinter as ctk
from tkinter import ttk
from fifa.app import App, VIEWS

app = App()
errors = []
app.report_callback_exception = lambda exc, value, tb: errors.append(str(value))


def descendants(widget):
    for child in widget.winfo_children():
        yield child
        yield from descendants(child)


def exercise():
    try:
        for button, (title, module) in zip(app.buttons, VIEWS):
            button.invoke()
            app.update()
            assert not app.status.cget('text').startswith('Unable'), app.status.cget('text')
            for widget in list(descendants(app.content)):
                if isinstance(widget, ctk.CTkSegmentedButton):
                    for value in widget.cget('values'):
                        widget.set(value)
                        widget.cget('command')(value)
                        app.update()
                if isinstance(widget, ttk.Combobox) and widget.cget('values'):
                    widget.current(len(widget.cget('values'))-1)
                    widget.event_generate('<<ComboboxSelected>>')
                    app.update()
            assert not errors, errors
            # Return to the default view before recording documentation screenshots.
            app.navigate(module, title)
            app.update()
            if '--screenshots' in sys.argv:
                target = Path(__file__).resolve().parents[1] / 'assets/screenshots' / f'{module.__name__.split(".")[-1]}.png'
                target.parent.mkdir(parents=True, exist_ok=True)
                app.lift()
                app.update()
                time.sleep(.3)
                windows = Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionAll, Quartz.kCGNullWindowID)
                window = next((w for w in windows if w.get('kCGWindowOwnerPID') == os.getpid() and w.get('kCGWindowName') == app.title()), None)
                if window is None:
                    raise RuntimeError('The dashboard window could not be found. Keep the desktop unlocked and retry.')
                result = subprocess.run(['screencapture', '-x', '-o', '-l', str(window['kCGWindowNumber']), str(target)], capture_output=True, text=True)
                if result.returncode:
                    raise RuntimeError(
                        'Window capture failed even though the permission preflight passed. '
                        'Keep the desktop unlocked, restart the app running this command, and retry. '
                        f'macOS reported: {result.stderr.strip()}'
                    )
            print('PASS', title, flush=True)
        app.geometry('1050x760')
        for title, module in VIEWS:
            app.navigate(module, title)
            app.update()
            assert not app.status.cget('text').startswith('Unable'), app.status.cget('text')
            for widget in descendants(app.content):
                if hasattr(widget, '_plot_canvas'):
                    assert widget.winfo_height() >= 200, f'{title}: chart too short'
        print('PASS minimum window size', flush=True)
        assert not errors, errors
    finally:
        app.destroy()

app.after(1000, exercise)
app.mainloop()
if errors:
    raise SystemExit('\n'.join(errors))
