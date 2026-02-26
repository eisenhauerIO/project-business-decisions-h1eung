import os
import re
import numpy as np
import pandas as pd

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
def txt_to_list(coeff, pair):
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
                filename = f"tiebreaking_C{T}_q{q}_coeff{coeff}_WS_g{pair}.txt"
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
            table_row = table_row + f"{float(np.array(L)[i])*100:.1f}" + r"&"
    if L[-1] == "":
        table_row = table_row + " " + r"\\"
    else:
        table_row = table_row + f"{float(np.array(L)[-1])*100:.1f}" + r"\\"
    return table_row

def table_size(coeff,pairs_size,Cs,table_name):
    with open(table_name, 'w') as my_output:
        my_output.write(r"\begin{table}[htbp]")
        my_output.write(r"\centering")
        my_output.write(r"\caption{Rejection probabilities: $\alpha = 0.05$ ($2,000$ Monte Carlo iterations)}")
        my_output.write(r"\renewcommand{\arraystretch}{1.0}")
        my_output.write(r"\setlength{\tabcolsep}{4pt}")
        my_output.write(r"\begin{tabular}{@{}c*{17}{c}@{}}")
        my_output.write(r"\toprule")
    
        for pair in pairs_size:
            my_output.write(r"& \multicolumn{17}{c}{$H_0 : " + r"\tilde " + f"g_{int(str(pair)[0])} =_d " + r"\tilde " +  f"g_{int(str(pair)[1])}$" + r"(Watts-Strogatz(2,0.3), $U_{ic} \sim U\in [-4,4]$, $\theta=(0,2,0," + f"{int(str(coeff)[0])},{int(str(coeff)[1])},{int(str(coeff)[2])}" + r")$)} \\")
            if pair == pairs_size[0]:
                my_output.write(r"& \multicolumn{17}{c}{$q$}  \\")
                my_output.write(r"\cmidrule(lr){2-18}")
                my_output.write(r"$C$ & 4 & 5 & 6 & 7 & 8 & 9 & 10 & 11 & 12 & 13 &14 & 15 & 16 & 17 & 18 & 19 & 20  \\")
            my_output.write(r"\midrule")
            results = txt_to_list(coeff, pair)
            for i in range(len(results)):
                table_row = f"{Cs[i]}" + "&" + list_to_table(results[i])
                my_output.write(table_row)
                
            if pair == pairs_size[-1]:
                my_output.write(r"\bottomrule")
            else:
                my_output.write(r"\midrule")
            
        my_output.write(r"\end{tabular}")
        my_output.write(r"\label{tab:rej_prob_null_" + str(coeff) + r"}")
        my_output.write(r"\end{table}")

def table_power(coeff,pairs_power,Cs,table_name):
    with open(table_name, 'w') as my_output:
        my_output.write(r"\begin{table}[htbp]")
        my_output.write(r"\centering")
        my_output.write(r"\caption{Rejection probabilities: $\alpha = 0.05$ ($2,000$ Monte Carlo iterations)}")
        my_output.write(r"\renewcommand{\arraystretch}{1.0}")
        my_output.write(r"\setlength{\tabcolsep}{2pt}")
        my_output.write(r"\begin{tabular}{@{}c*{17}{c}@{}}")
        my_output.write(r"\toprule")
    
        for pair in pairs_power:
            my_output.write(r"& \multicolumn{17}{c}{$H_0 : " + r"\tilde " + f"g_{int(str(pair)[0])} =_d" + r"\tilde " +  f"g_{int(str(pair)[1])}$" + r"(Watts-Strogatz(2,0.3), $U_{ic} \sim \text{Unif}[-4,4]$, $\theta=(0,2,0," + f"{int(str(coeff)[0])},{int(str(coeff)[1])},{int(str(coeff)[2])}" + r")$)} \\")
            if pair == pairs_power[0]:
                my_output.write(r"& \multicolumn{17}{c}{$q$}  \\")
                my_output.write(r"\cmidrule(lr){2-18}")
                my_output.write(r"$C$ & 4 & 5 & 6 & 7 & 8 & 9 & 10 & 11 & 12 & 13 &14 & 15 & 16 & 17 & 18 & 19 & 20  \\")
            my_output.write(r"\midrule")
            results = txt_to_list(coeff, pair)
            for i in range(len(results)):
                table_row = f"{Cs[i]}" + "&" + list_to_table(results[i])
                my_output.write(table_row)
                
            if pair == pairs_power[-1]:
                my_output.write(r"\bottomrule")
            else:
                my_output.write(r"\midrule")
            
        my_output.write(r"\end{tabular}")
        my_output.write(r"\label{tab:rej_prob_power_" + str(coeff) + r"}")
        my_output.write(r"\end{table}")
    
Cs = [20,50,100,200]
coeffs = [654,543,432,321]
pairs_size = [15,26,37,48]
pairs_power = [12,13,14,56,57,58]


## Tables 6-10 latex output

table_size(coeffs[3],pairs_size,Cs,"Table6.txt")
table_power(coeffs[3],pairs_power,Cs,"Table7.txt")
table_power(coeffs[2],pairs_power,Cs,"Table8.txt")
table_power(coeffs[1],pairs_power,Cs,"Table9.txt")
table_power(coeffs[0],pairs_power,Cs,"Table10.txt")