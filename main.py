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

        # top_frame
        self.top_frame = Tk.Frame(self.master)
        self.top_frame.grid(row = 0, column = 0, columnspan=3, sticky="NW")

        self.createBrowseButton()
        self.createConvertButton()
        self.path_label = Tk.Label(self.top_frame, text = "Path  :   ").grid(row = 0, column = 0)
        self.entry = Tk.Entry(self.top_frame, textvariable = self.path, width = 30).grid(row = 0, column = 1)


    def createBrowseButton(self):
        self.browseButton = Tk.Button(self, text='Browse',
            command=self.choose_path)
        self.browseButton.grid()

    def createConvertButton(self):
        self.convertButton = Tk.Button(self, text='Convert',
            command=self.convert)
        self.convertButton.grid()

    def choose_path(self):
        """
        Called when users press the 'Browse' button in order to choose a path on their system.
        """
        path_ = tkFileDialog.askdirectory()
        self.path.set(path_)
        print ("Opened %s"%self.path.get())
        self.load_file()

    def convert(self):
        """
        Called when users press the 'Convert' button in order to convert data.
        """
        print ("Converting")
        # TODO
        for file_name in self.wscan_ls:
            with open(self.path.get() + "/" + file_name) as f:
                data = json.load(f)
                request_path = self.jsonToString(data)
                res = self.send_request(request_path)
                print("\n%s"%res.text)
        print("\nFinish!")
        # self.write2CSV()


    def load_file(self):
        """
        To load all the 'wscan.json' files into wscan_ls
        """
        print("loading file")
        # TODO
        for file_name in os.listdir(self.path.get()):
            if file_name.endswith(".wscan.json"):
                self.wscan_ls.append(file_name)
        print(self.wscan_ls)
    
    def jsonToString(self,data):
        """
        Get a json object and return a request path in string.
        """
        # TODO: Combine all mac addresses
        path = "https://api.mylnikov.org/geolocation/wifi?v=1.1&search="
        for i in range(len(data["aps"])):
            mac = data["aps"][i]["mac"]
            signal = data["aps"][i]["level"]
            string = mac + "," + str(signal) + ";"
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

    def write2CSV():
        """
        Write a directory into a CSV which contains lines of lat & long
        """

root = MainApplication()
root.title('Wifi Position Convertor')
root.mainloop()