"""
Banner do Nawi
"""

def print_banner():
    # Definição das Cores ANSI
    RST = "\033[0m"             # Reset
    VERDE = "\033[92m"          # Cor do Nawi
    RED = "\033[91m"            # Cor dos Olhos
    MARROM = "\033[38;5;94m"    # Cor do Tronco (Marrom/Ocre)
    TXT = "\033[96m"            # Cor do Texto (Ciano)
    BORDA = "\033[34m"          # Cor das linhas

    # Imprimindo o banner
    banner = rf"""
{BORDA}========================================================{RST}

                 {VERDE}/^----^\{RST}
                 {VERDE}| {TXT}0{RST}  {RED}0{RST}{VERDE} |{RST}
    NAWI         {VERDE}|  \/  |{RST}
                 {VERDE}/       \{RST}
    Agent       {VERDE}|     |;;;|{RST}
                {VERDE}|     |;;;|{RST}           {MARROM}\   \\{RST}
                {VERDE}|      \;;|{RST}          {MARROM}\\\\//{RST}
                 {VERDE}\       \|{RST}           {MARROM}/ /{RST}
{MARROM}------------------{RST}{VERDE}(((--((({RST}{MARROM}------------\ \----------,{RST}
{MARROM}--  ___  ----  __ ---  ____  ---- _____ -- __ - \{RST}
{MARROM}__ --   __ -- _____ --- __  ----  ___  ---- __ -- /{RST}
{MARROM}---------------/ /---------------\  \--------------`{RST}
                {MARROM}\ \{RST}               {MARROM}/ /{RST}
                {MARROM}//               {MARROM}//{RST}
                {MARROM}\{RST}                {MARROM}\\{RST}

{BORDA}========================================================{RST}
"""

    print(banner)