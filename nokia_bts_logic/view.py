import tkinter as tk 
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showinfo
import logic as l

class View(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.geometry('400x400')
        self.title("Nokia BTS Logic v0.1")
        self.resizable(0,0)

        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=3)
        self.columnconfigure(2,weight=1)

        self.station_name_text = tk.StringVar()
        self.station_label_text = tk.StringVar()
        self.station_location_text = tk.StringVar()
        self.bcf_id_text = tk.StringVar()
        self.omusig_addr_text = tk.StringVar()
        self.lte_path_text = tk.StringVar()
        self.ip_path_text = tk.StringVar()
        self.template_path_text = tk.StringVar()
        self.out_path_text = tk.StringVar()

        self.status=tk.StringVar()

        self.station_name_label = tk.Label(self, text="Station Name:")
        self.station_label_label = tk.Label(self, text="Station Label:")
        self.station_location_label = tk.Label(self, text="Station Location:")
        self.bcf_id_label = tk.Label(self, text="BCF ID:")
        self.omusig_addr_label = tk.Label(self, text="Omusig Address:")
        self.lte_path_label = tk.Label(self, text="LTE Table:")
        self.lte_button = tk.Button(self, text="Choose", command=self.open_lte)
        self.ip_path_label = tk.Label(self, text="IP Table:")
        self.ip_button = tk.Button(self, text="Choose", command=self.open_ip)
        self.template_path_label = tk.Label(self, text="Template Station:")
        self.template_button = tk.Button(self, text="Choose", command=self.open_template)
        self.out_path_label = tk.Label(self, text="Output path:")
        self.out_button = tk.Button(self, text="Choose", command=self.save_file)
        self.status_label = tk.Label(self, textvariable=self.status)
        self.submit_button=tk.Button(self, text="Apply", command=self.run)

        self.station_name_entry = tk.Entry(self, textvariable=self.station_name_text)
        self.station_label_entry = tk.Entry(self, textvariable=self.station_label_text)
        self.station_location_entry = tk.Entry(self, textvariable=self.station_location_text)
        self.bcf_id_entry = tk.Entry(self, textvariable=self.bcf_id_text)
        self.omusig_addr_entry = tk.Entry(self, textvariable=self.omusig_addr_text)
        self.lte_path_entry = tk.Entry(self,state='disabled', textvariable=self.lte_path_text)
        self.ip_path_entry = tk.Entry(self,state='disabled', textvariable=self.ip_path_text)
        self.template_path_entry = tk.Entry(self,state='disabled', textvariable=self.template_path_text)
        self.out_path_entry = tk.Entry(self,state='disabled', textvariable=self.out_path_text)

        self.station_name_label.grid(column=0,row=1,sticky=tk.E,padx=5,pady=5)
        self.station_label_label.grid(column=0,row=2,sticky=tk.E,padx=5,pady=5)
        self.station_location_label.grid(column=0,row=3,sticky=tk.E,padx=5,pady=5)
        self.bcf_id_label.grid(column=0,row=4,sticky=tk.E,padx=5,pady=5)
        self.omusig_addr_label.grid(column=0,row=5,sticky=tk.E,padx=5,pady=5)
        self.lte_path_label.grid(column=0,row=6,sticky=tk.E,padx=5,pady=5)
        self.ip_path_label.grid(column=0,row=7,sticky=tk.E,padx=5,pady=5)
        self.template_path_label.grid(column=0,row=8,sticky=tk.E,padx=5,pady=5)
        self.out_path_label.grid(column=0,row=9,sticky=tk.E,padx=5,pady=5)

        self.status_label.grid(column=0,row=11,sticky=tk.SW,padx=5,pady=5)

        self.lte_button.grid(column=2,row=6,sticky=tk.W,padx=5,pady=5)
        self.ip_button.grid(column=2,row=7,sticky=tk.W,padx=5,pady=5)
        self.template_button.grid(column=2,row=8,sticky=tk.W,padx=5,pady=5)
        self.out_button.grid(column=2,row=9,sticky=tk.W,padx=5,pady=5)

        self.submit_button.grid(column=0,columnspan=3,row=10,padx=5,pady=5)

        self.station_name_entry.grid(column=1,row=1,padx=5,pady=5)
        self.station_label_entry.grid(column=1,row=2,padx=5,pady=5)
        self.station_location_entry.grid(column=1,row=3,padx=5,pady=5)
        self.bcf_id_entry.grid(column=1,row=4,padx=5,pady=5)
        self.omusig_addr_entry.grid(column=1,row=5,padx=5,pady=5)
        self.lte_path_entry.grid(column=1,row=6,padx=5,pady=5)
        self.ip_path_entry.grid(column=1,row=7,padx=5,pady=5)
        self.template_path_entry.grid(column=1,row=8,padx=5,pady=5)
        self.out_path_entry.grid(column=1,row=9,padx=5,pady=5)

        

    def open_lte(self):
        file = askopenfilename(title="Open a File", filetypes=[("Excel files", ".xlsx .xls .xlsm")])
        if(file!='' and file is not None):
            self.lte_path_text.set(file)

    def open_ip(self):
        file = askopenfilename(title="Open a File", filetypes=[("Excel files", ".xlsx .xls .xlsm")])
        if(file!='' and file is not None):
            self.ip_path_text.set(file)
    
    def open_template(self):
        file = askopenfilename(title="Open a File", filetypes=[("XML files", ".xml")])
        if(file!='' and file is not None):
            self.template_path_text.set(file)

    def save_file(self):
        file = asksaveasfilename(title="Save as", filetypes=[("XML files", ".xml")], defaultextension='.xml')
        if(file!='' and file is not None):
            self.out_path_text.set(file)

    def show_status(self,message):
        self.status.set(message)

    def run(self):
        worker = l.Logic(
            self.station_name_text.get(),
            self.station_label_text.get(),
            self.station_location_text.get(),
            self.bcf_id_text.get(),
            self.omusig_addr_text.get(),
            self.lte_path_text.get(),
            self.ip_path_text.get(),
            self.template_path_text.get(),
            self.out_path_text.get(),
        )
        worker.set_logger(self.show_status)
        worker.start()

    def start(self):
        self.mainloop()

if __name__ == "__main__":
    gui = View()
    gui.start()
