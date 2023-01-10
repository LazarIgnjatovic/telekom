import csv
import pandas as pd
import sys

import tkinter as tk 
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showinfo

#source_path='./test_source.csv'
#dest_path='./test_destination.csv'

def csv_import(path):
    with open(path, newline='\n') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        dataframes=[]
        for row in spamreader:
            if(len(row)<3):
                continue
            if(row[0][0]=='$'):
                dataframes.append(pd.DataFrame(columns=row))
            else:
                dataframes[-1] = pd.concat([pd.DataFrame(data=[row], columns=dataframes[-1].columns), dataframes[-1]], ignore_index=True)

        res=pd.concat(dataframes)
        return res

window = tk.Tk()
window.title("Unify CSV")
frame = tk.Frame(window,height = 200, width = 300)
frame.pack()
lb_file=tk.Label(frame, text="[no file chosen]")
save_btn = tk.Button(frame, text="Save")

def info():
    text='''
CSV Document Unifier
    lazari@telekom

    Purpose:
Unifies multiple .CSV configurations within a single .CSV file into a single dataset containing all fields from multiple datasets contained in a document

    Requirements:
First row in a dataset header MUST start with '$' (As seen in exported NOKIA .csv configurations)
Headers with less than 2 parameters will be ignored!
If overwrite is attempted (destination file exists) program will throw an Error!
    '''
    showinfo(title="About", message=text)

def save(file):
    if(file is None or file==''):
        return
    dest = asksaveasfilename(filetypes=[("CSV files", "*.csv")], defaultextension='csv')
    if(dest is None or dest==''):
        return
    csv_import(file).to_csv(path_or_buf=dest,index=False)
    showinfo(title="Success", message="File converted Succesfuly")

def open_file():
    file = askopenfilename(filetypes=[("CSV files", "*.csv")])
    if(file!='' and file is not None):
        lb_file['text'] = file
        save_btn.configure(text="Save",command= lambda *args: save(file))
        save_btn.grid(row = 3, column = 1, ipadx=10, ipady=10, padx=10, pady=10)
    else:
        save_btn.grid_forget()
        lb_file['text'] = '[no file chosen]'

save_btn['command']=save
tk.Label(frame, text="Unify CSV").grid(row = 1, column = 1, ipadx=10, ipady=10, padx=10, pady=10)
tk.Label(frame, text="Source file:").grid(row = 2, column = 0, ipadx=10, ipady=10, padx=10, pady=10)
lb_file.grid(row = 2, column = 1, ipadx=10, ipady=10, padx=10, pady=10)
tk.Button(frame, text="Open", command=open_file).grid(row = 2, column = 2, ipadx=10, ipady=10, padx=10, pady=10)

tk.Button(frame, text="Info", command=info).grid(column=1, row=5,sticky ='s')

window.geometry('800x400')
window.mainloop()
