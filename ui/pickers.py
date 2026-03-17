"""
Autocomplete interativo para terminal.

"""

import os
import sys
from typing import List, Optional, Tuple

from ui.terminal import (
    read_key, clear_line, move_up, clear_below, hide_cursor, show_cursor,
    KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_ENTER, KEY_BACKSPACE, KEY_ESC, KEY_TAB, KEY_CTRL_C,
)

# Paleta
R      = '\033[0m'
BOLD   = '\033[1m'
DIM    = '\033[2m'
CYAN   = '\033[96m'
GREEN  = '\033[92m'
WHITE  = '\033[97m'
BG_HI  = '\033[48;5;238m'

MAX_ITEMS = 7


# Pastas ignoradas no autocomplete
IGNORED_DIRS = {
    '__pycache__', '.git', '.hg', '.svn',
    'node_modules', '.terraform', '.tox',
    'venv', '.venv', 'env', '.env',
    'dist', 'build', '.build',
    '.mypy_cache', '.pytest_cache', '.ruff_cache',
    '.DS_Store', 'htmlcov', '.eggs',
}

# Listagem de filesystem 
def _scan(base: str, query: str, dirs_only: bool = False) -> List[Tuple[str, bool]]:
    try:
        raw = os.listdir(base)
    except PermissionError:
        return []

    q = query.lower()
    result = []
    for name in sorted(raw):
        if name.startswith('.'):
            continue
        if name in IGNORED_DIRS:
            continue
        full = os.path.join(base, name)
        is_dir = os.path.isdir(full)
        if dirs_only and not is_dir:
            continue
        if name.lower().startswith(q):
            result.append((name, is_dir))

    result.sort(key=lambda x: (not x[1], x[0].lower()))
    return result


# Renderização do dropdown
def _label(name: str, is_dir: bool) -> str:
    icon = '📁' if is_dir else '📄'
    return f'{icon} {name}{"/" if is_dir else ""}'


def _draw_dropdown(items: List[Tuple[str, bool]], sel: int, offset: int) -> int:
    visible = items[offset: offset + MAX_ITEMS]
    drawn = 0
    for i, (name, is_dir) in enumerate(visible):
        abs_i = offset + i
        lbl = _label(name, is_dir)
        if abs_i == sel:
            line = f'  {BG_HI}{CYAN}{BOLD} {lbl} {R}'
        else:
            color = CYAN if is_dir else WHITE
            line = f'  {DIM}│{R} {color}{lbl}{R}'
        sys.stdout.write(f'\n{line}\x1b[0K')
        drawn += 1
    if offset > 0:
        sys.stdout.write(f'\n  {DIM}  ↑  {R}\x1b[0K'); drawn += 1
    if offset + MAX_ITEMS < len(items):
        sys.stdout.write(f'\n  {DIM}  ↓  {R}\x1b[0K'); drawn += 1
    sys.stdout.flush()
    return drawn


# Núcleo do autocomplete 
class _Autocomplete:
    """
    TAB / Enter  — pasta: entra nela | arquivo: confirma → 'done'
    →            — confirma o item destacado sem entrar → 'done_right'
    ESC          — fecha popup → 'abort'
    ↑ / ↓        — move highlight
    Backspace    — remove da query; se vazia → 'cancel_trigger'
    """

    def __init__(self, base_dir: str, dirs_only: bool = False):
        self.base_dir  = os.path.abspath(base_dir)
        self.nav_dir   = self.base_dir
        self.dirs_only = dirs_only
        self.query     = ''
        self.sel       = 0
        self.offset    = 0
        self._items: List[Tuple[str, bool]] = []
        self._drawn    = 0
        self._refresh_items()

    def render(self, prompt_text: str):
        nav_display = os.path.relpath(self.nav_dir) + os.sep if self.nav_dir != self.base_dir else ''
        display = prompt_text + nav_display + self.query
        clear_line()
        sys.stdout.write(f'\r{CYAN}>{R} {display}')
        self._clear_dropdown()
        if self._items:
            self._drawn = _draw_dropdown(self._items, self.sel, self.offset)
            move_up(self._drawn)
        sys.stdout.flush()

    def feed(self, key: str) -> Tuple[str, Optional[str]]:
        if key == KEY_ESC:
            self._clear_dropdown()
            return 'abort', None

        if key == KEY_RIGHT:
            if not self._items:
                return 'continue', None
            name, is_dir = self._items[self.sel]
            chosen = os.path.join(self.nav_dir, name)
            self._clear_dropdown()
            rel = os.path.relpath(chosen) + (os.sep if is_dir else '')
            return 'done_right', rel

        if key in (KEY_TAB, KEY_ENTER):
            if not self._items:
                return 'propagate', None
            name, is_dir = self._items[self.sel]
            chosen = os.path.join(self.nav_dir, name)
            self._clear_dropdown()
            if is_dir:
                self.nav_dir = chosen
                self.query = ''; self.sel = 0; self.offset = 0
                self._refresh_items()
                return 'entered_dir', None
            return 'done', os.path.relpath(chosen)

        if key == KEY_UP:
            self._move(-1); return 'continue', None
        if key == KEY_DOWN:
            self._move(+1); return 'continue', None

        if key == KEY_LEFT:
            if self.nav_dir != self.base_dir:
                self.nav_dir = os.path.dirname(self.nav_dir)
                self.query = ''; self.sel = 0; self.offset = 0
                self._refresh_items()
            return 'continue', None

        if key == KEY_BACKSPACE:
            if self.query:
                self.query = self.query[:-1]
                self.sel = 0; self.offset = 0
                self._refresh_items()
                return 'backspace', None
            self._clear_dropdown()
            return 'cancel_trigger', None

        if key and len(key) == 1 and key.isprintable():
            if key == ',':
                self._clear_dropdown()
                return 'done_comma', None
            self.query += key
            self.sel = 0; self.offset = 0
            self._refresh_items()
            if len(self._items) == 1:
                name, is_dir = self._items[0]
                chosen = os.path.join(self.nav_dir, name)
                self._clear_dropdown()
                if is_dir:
                    self.nav_dir = chosen
                    self.query = ''; self.sel = 0; self.offset = 0
                    self._refresh_items()
                    return 'entered_dir', None
                return 'done', os.path.relpath(chosen)
            return 'typed', key

        return 'continue', None

    def cleanup(self):
        self._clear_dropdown()

    def _refresh_items(self):
        self._items = _scan(self.nav_dir, self.query, self.dirs_only)

    def _move(self, delta: int):
        if not self._items:
            return
        self.sel = max(0, min(len(self._items) - 1, self.sel + delta))
        if self.sel < self.offset:
            self.offset = self.sel
        elif self.sel >= self.offset + MAX_ITEMS:
            self.offset = self.sel - MAX_ITEMS + 1

    def _clear_dropdown(self):
        if self._drawn:
            clear_below(self._drawn)
            self._drawn = 0


# Loop genérico de picker
def _run_picker(
    trigger: str,
    base_dir: str,
    dirs_only: bool,
    multi: bool,
) -> str:
    """
    Loop principal compartilhado por PathPicker e FolderPicker.
    Retorna o buffer final como string.
    """
    buffer = ''
    ac: Optional[_Autocomplete] = None

    hide_cursor()
    try:
        while True:
            clear_line()
            sys.stdout.write(f'\r{CYAN}>{R} {buffer}')
            if ac:
                ac.render(buffer)
            sys.stdout.flush()

            key = read_key()

            if key == KEY_CTRL_C:
                if ac: ac.cleanup()
                show_cursor(); sys.stdout.write('\n')
                return ''

            if key == KEY_ENTER and ac is None:
                sys.stdout.write('\n'); break

            if key == KEY_BACKSPACE and ac is None:
                if buffer: buffer = buffer[:-1]
                continue

            # Ativa autocomplete pelo trigger
            if key == trigger and ac is None:
                buffer += trigger
                ac = _Autocomplete(base_dir, dirs_only=dirs_only)
                continue

            # Delega ao autocomplete
            if ac is not None:
                action, value = ac.feed(key)

                if action == 'abort':
                    trig_pos = buffer.rfind(trigger)
                    buffer = buffer[:trig_pos]
                    ac = None

                elif action == 'cancel_trigger':
                    trig_pos = buffer.rfind(trigger)
                    buffer = buffer[:trig_pos]
                    ac = None

                elif action == 'entered_dir':
                    pass  # buffer congelado no trigger

                elif action == 'done':
                    trig_pos = buffer.rfind(trigger)
                    sep = ', ' if multi else ''
                    buffer = buffer[:trig_pos] + value + sep
                    ac = None

                elif action == 'done_right':
                    trig_pos = buffer.rfind(trigger)
                    sep = ', ' if multi else ''
                    buffer = buffer[:trig_pos] + value + sep
                    ac = None

                elif action == 'done_comma':
                    if multi:
                        trig_pos = buffer.rfind(trigger)
                        buffer = buffer[:trig_pos] + ', '
                    ac = None

                elif action == 'propagate':
                    ac.cleanup(); ac = None
                    sys.stdout.write('\n'); break

                continue

            if key and len(key) == 1 and key.isprintable():
                buffer += key

    except KeyboardInterrupt:
        if ac: ac.cleanup()
        show_cursor(); sys.stdout.write('\n')
        return ''

    show_cursor()
    return buffer


class PathPicker:
    """Input com @ para seleção de arquivos/pastas. Retorna lista de paths absolutos."""

    def __init__(self, base_dir: str = '.'):
        self.base_dir = os.path.abspath(base_dir)

    def run(self) -> List[str]:
        print(f'\n{BOLD}Caminhos para analisar{R}')
        print(f'{DIM}Use {CYAN}@{R}{DIM} para autocomplete · Tab/Enter entra na pasta · [→] confirma {R}\n')

        raw = _run_picker('@', self.base_dir, dirs_only=False, multi=True)

        parts = [p.strip().rstrip(os.sep + '/\\') for p in raw.split(',') if p.strip()]
        return [os.path.abspath(p) for p in parts if p]


class FolderPicker:
    """Input com / para seleção de pasta destino. Mesmo comportamento do @. Retorna path absoluto."""

    def __init__(self, base_dir: str = '.'):
        self.base_dir = os.path.abspath(base_dir)

    def run(self) -> str:
        print(f'\n{BOLD}Onde salvar?{R}')
        print(f'{DIM}Use {CYAN}@{R}{DIM} para autocomplete · Tab/Enter entra na pasta · [→] confirma {R}\n')

        raw = _run_picker('@', self.base_dir, dirs_only=True, multi=False)

        raw = raw.strip().rstrip('/\\')
        if not raw:
            return self.base_dir
        return os.path.abspath(raw)