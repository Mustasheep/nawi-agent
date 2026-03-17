"""
Leitura de tecla única cross-platform (Linux/Mac/Windows).
Expõe apenas: read_key() → str
"""

import sys
import os

KEY_UP        = '\x00UP'
KEY_DOWN      = '\x00DOWN'
KEY_LEFT      = '\x00LEFT'
KEY_RIGHT     = '\x00RIGHT'
KEY_ENTER     = '\r'
KEY_BACKSPACE = '\x7f'
KEY_ESC       = '\x1b'
KEY_TAB       = '\t'
KEY_CTRL_C    = '\x03'

if os.name == 'nt':
    import msvcrt

    def read_key() -> str:
        ch = msvcrt.getwch()
        if ch in ('\x00', '\xe0'):
            ch2 = msvcrt.getwch()
            return KEY_UP if ch2 == 'H' else KEY_DOWN if ch2 == 'P' else KEY_LEFT if ch2 == 'K' else KEY_RIGHT if ch2 == 'M' else f'\x00{ch2}'
        if ch == '\r':   return KEY_ENTER
        if ch == '\t':   return KEY_TAB
        if ch == '\x03': return KEY_CTRL_C
        if ch in ('\x08', '\x7f'): return KEY_BACKSPACE
        return ch

else:
    import tty, termios

    def read_key() -> str:
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                try:
                    seq = sys.stdin.read(2)
                    return KEY_UP if seq == '[A' else KEY_DOWN if seq == '[B' else KEY_RIGHT if seq == '[C' else KEY_LEFT if seq == '[D' else KEY_ESC
                except Exception:
                    return KEY_ESC
            if ch in ('\r', '\n'): return KEY_ENTER
            if ch == '\t':         return KEY_TAB
            if ch == '\x03':       return KEY_CTRL_C
            if ch in ('\x08', '\x7f'): return KEY_BACKSPACE
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


# ANSI helpers
def _w(s: str):
    sys.stdout.write(s)

def clear_line():   _w('\r\x1b[2K')
def move_up(n=1):   _w(f'\x1b[{n}A')
def hide_cursor():  _w('\x1b[?25l'); sys.stdout.flush()
def show_cursor():  _w('\x1b[?25h'); sys.stdout.flush()

def clear_below(n: int):
    """Apaga n linhas abaixo do cursor e volta para a posição original."""
    for i in range(n):
        _w('\n\r\x1b[2K')
    if n:
        move_up(n)
    sys.stdout.flush()