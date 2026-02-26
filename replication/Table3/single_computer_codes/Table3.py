import os
import re
import numpy as np
import pandas as pd
from decimal import Decimal

# Function to extract the number after ":" in the first line that has it
def extract_number(file_path):
    try:
        with open(file_path, 'r') as f:
            if re.search(r"WS.txt", file_path):
                for line in f:
                    search = re.search(r"g_1 =_d g_2:", line)
                    match = re.search(r":\s*([\d\.]+)", line)
                    if search:
                        return match.group(1)
                    else:
                        continue
            else:
                for line in f:
                    match = re.search(r":\s*([\d\.]+)", line)
                    if match:
                        return match.group(1)
                    else:
                        continue
        return ""
    except FileNotFoundError:
        return ""

# Define T values and corresponding q ranges
def txt_to_list(DGP_para_pair):
    Ts = [20, 50, 100, 200]
    q_dict = {
        20: list(range(4, 11)),     # q = 4 to 10 for T=20
        50: list(range(4, 21)),     # q = 4 to 20 for T=50
        100: list(range(4, 21)),    # q = 4 to 20 for T=100
        200: list(range(4, 21))     # q = 4 to 20 for T=200
    }
    
    # Collect results row by row
    results = []
    max_q_len = max(len(qs) for qs in q_dict.values())

    directory = os.getcwd() 
    for T in Ts:
        row = []
        for q in range(4, 4 + max_q_len):
            if q in q_dict[T]:
                filename = f"tiebreaking_C{T}_q{q}_" + DGP_para_pair + r".txt"
                filepath = os.path.join(directory, filename)
                value = extract_number(filepath)
            else:
                value = ""
            row.append(value)
        results.append(row)

    return results

def list_to_table(L):
    # L is a list (a row in the table)
    table_row = ""
    for i in range(len(L)-1):
        if L[i] == "":
            table_row = table_row + " " + r"&"
        else:
            number_str = str(Decimal(float(L[i])*100).quantize(Decimal("0.1"), rounding = "ROUND_HALF_UP"))
            table_row = table_row + number_str + r"&"
    if L[-1] == "":
        table_row = table_row + " " + r"\\"
    else:
        number_str = str(Decimal(float(L[-1])*100).quantize(Decimal("0.1"), rounding = "ROUND_HALF_UP"))
        table_row = table_row + number_str + r"\\"
    return table_row


## Table 3 latex output
Cs = [20,50,100,200]
DGP_para_pair_set = ["ER","WS_g38","WS_g67","WS","RG_g45","RG_g12"]

with open(f"Table3.txt", 'w') as my_output:
    my_output.write(r"\begin{table}[htbp]")
    my_output.write(r"\centering")
    my_output.write(r"\caption{Rejection probabilities: $\alpha = 0.05$ ($2,000$ Monte Carlo iterations)}")
    my_output.write(r"\renewcommand{\arraystretch}{1.0}")
    my_output.write(r"\setlength{\tabcolsep}{4pt}")
    my_output.write(r"\begin{tabular}{@{}c*{17}{c}@{}}")
    my_output.write(r"\toprule")
    
    my_output.write(r"& \multicolumn{17}{c}{$H_0 : g_1 =_d g_2$ (Erd\"os-Renyi(0.1))} \\")
    my_output.write(r"& \multicolumn{17}{c}{$q$}  \\")
    my_output.write(r"\cmidrule(lr){2-18}")
    my_output.write(r"$C$ & 4 & 5 & 6 & 7 & 8 & 9 & 10 & 11 & 12 & 13 & 14 & 15 & 16 & 17 & 18 & 19 & 20  \\")
    my_output.write(r"\midrule")

    results = txt_to_list(DGP_para_pair_set[0])
    for i in range(len(Cs)):
        table_row = f"{Cs[i]}" + "&" + list_to_table(results[i])
        my_output.write(table_row)
    
    my_output.write(r"\midrule")
    my_output.write(r"& \multicolumn{17}{c}{$H_0 : g_3 =_d g_8$ (Watts-Strogatz(2, 0.2))} \\")
    my_output.write(r"\midrule")
    
    results = txt_to_list(DGP_para_pair_set[1])
    for i in range(len(Cs)):
        table_row = f"{Cs[i]}" + "&" + list_to_table(results[i])
        my_output.write(table_row)
    
    my_output.write(r"\midrule")
    my_output.write(r"& \multicolumn{17}{c}{$H_0 : g_6 =_d g_7$  (Watts-Strogatz(2, 0.8))} \\")
    my_output.write(r"\midrule")
    
    results = txt_to_list(DGP_para_pair_set[2])
    for i in range(len(Cs)):
        table_row = f"{Cs[i]}" + "&" + list_to_table(results[i])
        my_output.write(table_row)
    
    my_output.write(r"\midrule")
    my_output.write(r"& \multicolumn{17}{c}{$H_0 : g_1 =_d g_2$  (Watts-Strogatz(2, 0.275))} \\")
    my_output.write(r"\midrule")

    results = txt_to_list(DGP_para_pair_set[3])
    for i in range(len(Cs)):
        table_row = f"{Cs[i]}" + "&" + list_to_table(results[i])
        my_output.write(table_row)
    
    my_output.write(r"\midrule")
    my_output.write(r"& \multicolumn{17}{c}{$H_0 : g_4 =_d g_5$  (Random Geometric(0.2))} \\")
    my_output.write(r"\midrule")
    
    results = txt_to_list(DGP_para_pair_set[4])
    for i in range(len(Cs)):
        table_row = f"{Cs[i]}" + "&" + list_to_table(results[i])
        my_output.write(table_row)
    
    my_output.write(r"\midrule")
    my_output.write(r"& \multicolumn{17}{c}{$H_0 : g_1 =_d g_2$ (Random Geometric(0.2))} \\")
    my_output.write(r"\midrule")
    
    results = txt_to_list(DGP_para_pair_set[5])
    for i in range(len(Cs)):
        table_row = f"{Cs[i]}" + "&" + list_to_table(results[i])
        my_output.write(table_row)
    
    my_output.write(r"\bottomrule")
    my_output.write(r"\end{tabular}")
    my_output.write(r"\label{tab:rej_prob_null}")
    my_output.write(r"\end{table}")

