"""Ajuda a descobrir a posição (x, y) do campo RA na tela.
Rode, posicione o mouse sobre o campo RA do formulário e aguarde a contagem."""
import time

import pyautogui

print("Abra o formulário e coloque o mouse sobre o campo RA...")
for segundos in range(5, 0, -1):
    print(f"{segundos}...")
    time.sleep(1)

x, y = pyautogui.position()
print(f"\nPOSICAO_CAMPO_RA = ({x}, {y})")
print("Copie a linha acima para o topo do main.py")