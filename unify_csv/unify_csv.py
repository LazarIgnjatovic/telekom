import csv
import pandas as pd
import sys

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

def print_help():
    text='''
    CSV Document Unifier
        lazari@telekom

    Purpose:
        Unifies multiple .CSV configurations within a single .CSV file into a single dataset containing all fields from multiple datasets contained in a document
    
    Requirements:
        First row in a dataset header MUST start with '$' (As seen in exported NOKIA .csv configurations)
        Headers with less than 2 parameters will be ignored!
        If overwrite is attempted (destination file exists) progra will throw an Error!

    Usage (executed from cmd):
        >unify_csv.exe ["source_file_path"] ["destination_file_path"]
    '''
    print(text)

if(len(sys.argv)!=3):
    print_help()
    sys.exit()
source_path=sys.argv[1]
dest_path=sys.argv[2]
csv_import(source_path).to_csv(path_or_buf=dest_path,index=False)
