import os
import re
import numpy as np
import pandas as pd
from decimal import Decimal

# Function to extract the number after ":" in the first line that has it
def extract_number(file_path):
    try:
        with open(file_path, 'r') as f:
            for line in f:
                match = re.search(r":\s*([\d\.]+)", line)
                if match:
                    return match.group(1)
        return ""
    except FileNotFoundError:
        return ""

# Define T values and corresponding q ranges
def txt_to_list(DGP, DGP_paras, err_bnd):
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
                filename = f"tiebreaking_C{T}_q{q}_{DGP}{DGP_paras}_alt_U{err_bnd}.txt"
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
            # table_row = table_row + str(Decimal(float(L[i])*100).quantize(Decimal("0.1"), rounding = "ROUND_HALF_UP")) + r"&"
            table_row = table_row + f"{float(np.array(L)[i])*100:.1f}" + r"&"
    if L[-1] == "":
        table_row = table_row + " " + r"\\"
    else:
        # table_row = table_row + str(Decimal(float(L[-1])*100).quantize(Decimal("0.1"), rounding = "ROUND_HALF_UP")) + r"\\"
        table_row = table_row + f"{float(np.array(L)[-1])*100:.1f}" + r"\\"
    return table_row

def table_power(DGP,DGP_paras,err_bnd_set,Cs,table_name):

    with open(table_name, 'w') as my_output:
        my_output.write(r"\begin{table}[htbp]")
        my_output.write(r"\centering")
        my_output.write(r"\caption{Rejection probabilities: $\alpha = 0.05$ ($2,000$ Monte Carlo iterations)}")
        my_output.write(r"\renewcommand{\arraystretch}{1.0}")
        my_output.write(r"\setlength{\tabcolsep}{1pt}")
        my_output.write(r"\begin{tabular}{@{}c*{17}{c}@{}}")
        my_output.write(r"\toprule")
    
        for err_bnd in err_bnd_set:
            if DGP == "ER":
                my_output.write(r"& \multicolumn{17}{c}{$H_0 : g_3 =_d g_4$ " + r"(Erd\"os-Renyi" + f"({DGP_paras}), " + r"$U_{ic} \sim U \in " + f"[-{int(err_bnd)},{int(err_bnd)}]$" + r")} \\")
            elif DGP == "WS":
                my_output.write(r"& \multicolumn{17}{c}{$H_0 : g_3 =_d g_4$ " + f"(Watts-Strogatz(2,{DGP_paras}), " + r"$U_{ic} \sim U \in " + f"[-{int(err_bnd)},{int(err_bnd)}]$" + r")} \\")
            elif DGP == "RG":
                my_output.write(r"& \multicolumn{17}{c}{$H_0 : g_3 =_d g_4$ " + f"(Random Geometric({DGP_paras}), " + r"$U_{ic} \sim U \in " + f"[-{int(err_bnd)},{int(err_bnd)}]$" + r")} \\")
            
            if err_bnd == err_bnd_set[0]:
                my_output.write(r"& \multicolumn{17}{c}{$q$}  \\")
                my_output.write(r"\cmidrule(lr){2-18}")
                my_output.write(r"$C$ & 4 & 5 & 6 & 7 & 8 & 9 & 10 & 11 & 12 & 13 &14 & 15 & 16 & 17 & 18 & 19 & 20  \\")
            my_output.write(r"\midrule")
            results = txt_to_list(DGP, DGP_paras, err_bnd)
            for i in range(len(results)):
                table_row = f"{Cs[i]}" + "&" + list_to_table(results[i])
                my_output.write(table_row)
                
            if err_bnd == err_bnd_set[-1]:
                my_output.write(r"\bottomrule")
            else:
                my_output.write(r"\midrule")
        
        my_output.write(r"\end{tabular}")
        if DGP == "ER":
            my_output.write(r"\label{tab:rej_prob_alt}")
        else:  
            my_output.write(r"\label{tab:rej_prob_alt_" + f"{DGP}{DGP_paras}" + r"}")
        my_output.write(r"\end{table}")

Cs = [20,50,100,200]
# DGP_paras_set = [0.1]
err_bnd_set = [5.0,4.0,3.0,2.0,1.0]
# DGP_set = ["ER","RG"]

# Tables 4 and 5 latex output

table_power("ER",0.1,err_bnd_set,Cs,"Table4.txt")
table_power("RG",0.1,err_bnd_set,Cs,"Table5.txt")

