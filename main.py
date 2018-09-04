#!/usr/bin/env python
import os, sys
import Tkinter as Tk
import tkFileDialog
import json
import base64
import requests
import csv

class MainApplication(Tk.Tk):
    def __init__(self):
        Tk.Tk.__init__(self)
        self.path = Tk.StringVar()
        self.wscan_ls=[]
        self.dirname = os.path.dirname(__file__)
        self.csv_path = ""

        # main_frame
        self.main_frame = Tk.Frame(self.master)
        self.main_frame.grid(sticky="NWSE")

        self.createBrowseButton()
        self.createConvertButton()
        self.path_label = Tk.Label(self.main_frame, text = "Path  :   ").grid(row = 0, column = 0)
        self.entry = Tk.Entry(self.main_frame, textvariable = self.path, width = 30).grid(row = 0, column = 1)
        self.var_msg = Tk.StringVar()
        self.msg_lbl = Tk.Label(self.main_frame, textvariable=self.var_msg, font=("Helvetica", 12)).grid(row = 1, column = 0, columnspan = 3)

    def createBrowseButton(self):
        self.browseButton = Tk.Button(self, text='Browse',
            command=self.choose_path)
        self.browseButton.grid(row = 0, column = 2)

    def createConvertButton(self):
        self.convertButton = Tk.Button(self, text='Convert',
            command=self.convert)
        self.convertButton.grid(row = 2)

    def choose_path(self):
        """
        Called when users press the 'Browse' button in order to choose a path on their system.
        """
        path_ = tkFileDialog.askdirectory()
        self.path.set(path_)
        print ("Opened %s"%self.path.get())
        self.var_msg.set("Opened %s"%self.path.get())
        self.load_file()

    def convert(self):
        """
        Called when users press the 'Convert' button in order to convert data.
        """
        print ("Start Converting")
        self.var_msg.set("Converting to '{0}'.".format(self.csv_path))
        count = 0
        for file_name in self.wscan_ls:
            with open(self.path.get() + "/" + file_name) as f:
                data = json.load(f)
                request_path = self.jsonToString(data)
                res = self.send_request(request_path)
                print("\n%s"%res.text)
                csv_name = self.getFolderName(self.path.get()) + ".csv"
                self.csv_path = os.path.join(self.dirname, 'output/{0}'.format(csv_name))
                # To handle export same csv multiple times
                if count == 0:
                    # if csv file existed, do not export
                    if os.path.isfile(self.csv_path) == True:
                        self.var_msg.set("'{0}' already existed, do not export again".format(self.csv_path))
                        print("'{0}' already existed, do not export again".format(self.csv_path))
                        break
                    else:
                        self.export_csv(res,file_name)
                        count += 1
                else:
                    self.export_csv(res,file_name)
                    count += 1
        self.var_msg.set("Exported to '{0}' file successfully.".format(self.csv_path))
        print("\nCompleted!")

    def load_file(self):
        """
        To load all the 'wscan.json' files into wscan_ls
        """
        # print("loading file")
        self.wscan_ls = []
        for file_name in os.listdir(self.path.get()):
            if file_name.endswith(".wscan.json"):
                self.wscan_ls.append(file_name)
        print("List of wscan files: {0}".format(self.wscan_ls))
    
    def jsonToString(self,data):
        """
        Get a json object and return a request path in string.
        """
        path = "https://api.mylnikov.org/geolocation/wifi?v=1.1&search="
        for i in range(len(data["aps"])):
            mac = data["aps"][i]["mac"]
            signal = data["aps"][i]["level"]
            string = mac + "," + str(signal) + ";"
            # print(string)
            encoded_string = base64.b64encode(string)
            path += encoded_string

        path = path[:-1]
        # print ("\n%s"%path)
        return(path)

    def send_request(self,request_path):
        """
        Send a requst to API & return a responce object
        """
        res = requests.get(request_path)
        return res

    def export_csv(self,res,file_name):
        """
        Write a directory into a CSV which contains lines of lat & long & others...
        """
        # Read from csv name
        csv_name = self.getFolderName(self.path.get())
        ind1 = csv_name.rfind('_')
        ind2 = csv_name.rfind(' ') + 1
        # print (ind1, ind2)
        if ind2 == -1 or ind2 == 0:
            ind2 = csv_name.rfind('y') + 1

        if ind1 == -1 :
            participant_id = csv_name
        else:
            participant_id = csv_name[0:ind1]

        day = csv_name[ind2:]

        # Read from response object
        data = res.json()
        if data["result"] == 200:
            lat = data["data"]["lat"]
            lon = data["data"]["lon"]
            ran = data["data"]["range"]
            row = [participant_id,day,file_name,self.get_datetime(file_name),lat,lon,ran]
        else:
            row = [participant_id,day,file_name,self.get_datetime(file_name),"Unknown","Unknown","Unknown"]

            
        # write csv
        if os.path.isfile(self.csv_path) == False:
            with open(self.csv_path, 'w') as csv_file:
                writer = csv.writer(csv_file, delimiter = ',')
                writer.writerow(['participant_id','day','file_name','datetime','lat','long','range'])
                print("Created a new csv file called '{0}'".format(self.csv_path))
            with open(self.csv_path, 'a') as csv_file:
                writer = csv.writer(csv_file, delimiter = ',')
                writer.writerow(row)
            print ("Added 1 row to '{0}' file successfully.".format(self.csv_path))
        else:
            with open(self.csv_path, 'a') as csv_file:
                writer = csv.writer(csv_file, delimiter = ',')
                writer.writerow(row)
                print ("Added 1 row to '{0}' file successfully.".format(self.csv_path))

    def get_datetime(self, file_name):
        name = file_name  # 20000101_030548_000.wscan.json  -->  YYYY-MM-DD HH:MI:SS
        try:
			datetime = name[0:4] + "-" + name[4:6] + "-" + name[6:8] + " " + name[9:11] + ":" + name[11:13] + ":" + name[13:15]
        except:
			datetime = None
        return datetime

    def getFolderName(self, path):
        index = path.rfind('/')
        return path[index+1:]

root = MainApplication()
root.title('Wifi Position Convertor')
root.mainloop()