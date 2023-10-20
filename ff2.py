import itertools
from prettytable import PrettyTable

t = ["2.0", "8.0"]
hL = ["0.1", "1.0"]
L16 = ["0.16", "0.20"]
L14 = ["0.14", "0.18"]
r = ["0.01", "0.05"]
VF = [...]  # define VF
E = [...]  # define E
nu = [...]  # define nu

number = 1
table = PrettyTable()
table.field_names = ["#", "t", "hL", "L16", "L14", "r", "VF", "E", "nu"]
for combination in itertools.product(t, hL, L16, L14, r, VF, E, nu):
    row = [number] + list(combination)
    table.add_row(row)
    number += 1

print(table)
