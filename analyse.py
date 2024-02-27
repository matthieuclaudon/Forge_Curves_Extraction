### This program was written by Matthieu Claudon, from Mines Paris - PSL. ###

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import shutil
import tkinter as tk
from tkinter import ttk
from tkfilebrowser import askopendirnames, askopenfilename

class analyse:

    def __init__(self, legends, sensors_names, damage_criterion, unique_curves, plot_type, exp_surface, exp_strain_variable, plot_type_exp="-", PF_criterion = "Phase field", complete_title=True): 
        self.folders_paths = []
        self.result_folders_paths = []
        self.folder_path = ""
        self.result_folder_path = ""
        self.legends = legends
        self.sensors_names = sensors_names
        self.damage_criterion = damage_criterion
        self.PF_criterion = PF_criterion
        self.curves = ["Force vs. Displacement", "Stress vs. Strain", "Strain vs. Time", "PF vs. Damage"]
        self.unique_curves = unique_curves
        self.plot_type = plot_type
        self.plot_type_exp = plot_type_exp
        self.exp_surface = exp_surface
        self.exp_strain_variable = exp_strain_variable
        self.complete_title = complete_title
        self.init_open_root_window()
        
### GUI ###

    def init_open_root_window(self): 
        """
        Open the simulation selection window at the opening of the software. It allows to select one or more simulations to analyze. 
        """
        self.window = tk.Tk()
        self.window.geometry("300x200")
        self.chosen = tk.Text(self.window, height=100, width=100)
        self.buttons = tk.Frame(self.window)
        self.buttonPlus = tk.Button(self.buttons, text="+", command=self.add_simulation)
        self.buttonMinus = tk.Button(self.buttons, text="-", command=self.remove_simulation)
        self.buttonOK = tk.Button(self.buttons, text="OK", command=self.choose_what_to_plot)
        self.buttonOK.pack(side="left")
        self.buttonPlus.pack(side='top')
        self.buttonMinus.pack(side='bottom')
        self.buttons.pack(side='left')
        self.add_simulation()
        self.window.mainloop()

    def open_root_window(self): 
        """
        Also open the simulation selection window, but if it is called after the opening of the software.
        """
        self.window = tk.Tk()
        self.window.geometry("300x200")
        self.chosen = tk.Text(self.window, height=100, width=100)
        self.update_text_widget()
        self.buttons = tk.Frame(self.window)
        self.buttonPlus = tk.Button(self.buttons, text="+", command=self.add_simulation)
        self.buttonMinus = tk.Button(self.buttons, text="-", command=self.remove_simulation)
        self.buttonOK = tk.Button(self.buttons, text="OK", command=self.choose_what_to_plot)
        self.buttonOK.pack(side="left")
        self.buttonPlus.pack(side='top')
        self.buttonMinus.pack(side='bottom')
        self.buttons.pack(side='left')
        self.window.mainloop()

    def update_text_widget(self): 
        """
        In the simulation selection window, update the Text widget containing the list of the chosen simulations.
        """
        temp_string = ""
        for path in self.folders_paths:
            temp_string += str(os.path.basename(path))
            temp_string += "\n"
        self.chosen.destroy()
        self.chosen = tk.Text(self.window, height=10, width=30)
        self.chosen.insert(tk.END, temp_string)
        self.chosen.pack(side='right')

    def add_simulation(self): 
        """
        Add one or more simulations to the list shown in the simulation selection window.
        """
        self.new_folders_paths = askopendirnames()
        for folder in self.new_folders_paths:
            if folder not in self.folders_paths:
                self.folders_paths.append(folder)
            result_folder_path = ""
            self.simulation_name = os.path.basename(folder)
            try: # from classic Forge folder
                for dir in os.listdir(folder + "/../Analysis/ResultDataBase/"):
                    if len(dir) >= len(self.simulation_name):
                        if dir[- len(self.simulation_name):] == self.simulation_name:
                            result_folder_path = folder + "/../Analysis/ResultDataBase/{}/results".format(dir)
                            break
            except: # from MOOPI
                result_folder_path = folder + "/results"
            self.result_folders_paths.append(result_folder_path)
        self.update_text_widget()
    
    def remove_simulation(self): 
        """
        Remove one or more simulations to the list shown in the simulation selection window.
        """
        paths_folders_to_remove = askopendirnames()
        for path_folder_to_remove in paths_folders_to_remove:
            if path_folder_to_remove in self.folders_paths:
                temp_index = self.folders_paths.index(path_folder_to_remove)
                del self.folders_paths[temp_index]
                del self.result_folders_paths[temp_index]
                self.update_text_widget()

    def on_closing(self): 
        """
        Open the simulation selection window when the curve selection window is closed.
        """
        self.window2.destroy()
        self.open_root_window()

    def choose_what_to_plot(self): 
        """
        Open the second window (curve selection) of the software. This window depends on the mode:
        - MODE 1: only one simulation is considered (len(self.folders_path) = 1),
        - MODE 2: two or more simulations are considered (len(self.folders_path) > 1).
        """
        self.window.destroy()
        if len(self.folders_paths) == 1:
            self.folder_path = self.folders_paths[0]
            self.result_folder_path = self.result_folders_paths[0]
            self.window2 = tk.Tk()
            self.window2.geometry("1000x260")
            self.window2.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.frame1 = tk.LabelFrame(self.window2, text="Curves (multiple plots)", height=400, width=200)
            self.frame3 = tk.LabelFrame(self.window2, text="Curves (unique plot)", height=400, width=200)
            tk.Label(self.frame3, text="Please choose only one sensor").pack(side="top")
            self.frame3.grid(row=0, column=2)
            self.frame1.grid(row=0, column=1)
            self.UniqueCurvesCheckButtons = {}
            self.UniqueCurvesCheckButtonsVariables = {}
            for curve in list(self.unique_curves.keys()):
                self.UniqueCurvesCheckButtonsVariables[curve] = tk.IntVar()
                self.UniqueCurvesCheckButtonsVariables[curve].set(0)
                self.UniqueCurvesCheckButtons[curve] = tk.Checkbutton(self.frame3, text=curve, variable=self.UniqueCurvesCheckButtonsVariables[curve], command = lambda curve=curve: self.erase_other_checkbuttons_unique_curves(curve))
                self.UniqueCurvesCheckButtons[curve].pack()
            self.unique_curves_plot_button = tk.Button(self.frame3, text="Plot", command=self.plot_unique_curve)
            self.unique_curves_plot_button.pack()
            self.frame2 = tk.LabelFrame(self.window2, text="Sensors")
            self.frame2.grid(row=0, column=0)
            self.plotButton = tk.Button(self.frame1, text="Plot", command=self.plot_curves)
            self.plotButton.pack(side="bottom")
            self.CurvesCheckButtons = {}
            self.CurvesCheckButtonsVariables = {}
            for curve in self.curves:
                self.CurvesCheckButtonsVariables[curve] = tk.IntVar()
                self.CurvesCheckButtonsVariables[curve].set(1)
                self.CurvesCheckButtons[curve] = tk.Checkbutton(self.frame1, text=curve, variable=self.CurvesCheckButtonsVariables[curve])
                self.CurvesCheckButtons[curve].pack()
            self.ButtonsGroupSensor = {}
            for key in list(self.sensors_names.keys()):
                self.ButtonsGroupSensor[key] = tk.Button(self.frame2, text="Group {}".format(str(key)), command=lambda nb=key: self.displayGroup(nb))
                self.ButtonsGroupSensor[key].pack()
            self.displayGroup(1)
            self.frame4 = tk.LabelFrame(self.window2, text="Others")
            self.frame4.grid(row=0, column=3)
            self.list_of_values = []
            self.currentXvar = tk.StringVar()
            self.currentYvar = tk.StringVar()
            temp_list1 = self.variables_to_plot(1, 1)
            temp_list2 = self.variables_to_plot_upper_die()
            for elem in temp_list1:
                self.list_of_values.append(elem + " (Sensor)")
            for elem in temp_list2:
                self.list_of_values.append(elem + " (Upper die)")
            tk.Label(self.frame4, text="X: ").grid(row=0, column=0)
            self.chooseX = ttk.Combobox(self.frame4, values=self.list_of_values, textvariable=self.currentXvar, width=30)
            self.chooseX.grid(row=0, column=1)
            tk.Label(self.frame4, text="Y: ").grid(row=1, column=0)
            self.chooseY = ttk.Combobox(self.frame4, values=self.list_of_values, textvariable=self.currentYvar, width=30)
            self.chooseY.grid(row=1, column=1)
            tk.Label(self.frame4, text=" Factor: ").grid(row=0, column=2)
            tk.Label(self.frame4, text=" Factor: ").grid(row=1, column=2)
            tk.Label(self.frame4, text=" Offset: ").grid(row=0, column=4)
            tk.Label(self.frame4, text=" Offset: ").grid(row=1, column=4)
            self.x_factor_forge = tk.Text(self.frame4, height=1, width=10)
            self.x_factor_forge.grid(row=0, column=3)
            self.y_factor_forge = tk.Text(self.frame4, height=1, width=10)
            self.y_factor_forge.grid(row=1, column=3)
            self.x_offset_forge = tk.Text(self.frame4, height=1, width=10)
            self.x_offset_forge.grid(row=0, column=5)
            self.y_offset_forge = tk.Text(self.frame4, height=1, width=10)
            self.y_offset_forge.grid(row=1, column=5)
            self.plot_others_button = tk.Button(self.frame4, text="Plot", command=self.plot_others)
            self.plot_others_button.grid(row=2, column=1)
            self.frame5 = tk.LabelFrame(self.frame4, text="Add Experimental Curve")
            self.frame5.grid(row=3, column=0, columnspan=6)
            tk.Label(self.frame5, text="File: ").grid(row=0, column=0)
            self.browseButton = tk.Button(self.frame5, text="Browse", command=self.browse_exp_file)
            self.browseButton.grid(row=0, column=1)
            self.exp_file_name_stringVar = tk.StringVar()
            self.exp_file_name_display = tk.Label(self.frame5, textvariable=self.exp_file_name_stringVar, width=30)
            self.exp_file_name_display.grid(row=0, column=2, columnspan=4)
            tk.Label(self.frame5, text="X: ").grid(row=1, column=0)
            self.currentXvar_exp, self.currentYvar_exp = tk.StringVar(), tk.StringVar()
            self.exp_list_of_values = []
            self.chooseX_exp = ttk.Combobox(self.frame5, values=self.exp_list_of_values, textvariable=self.currentXvar_exp, width=15)
            self.chooseX_exp.grid(row=1, column=1)
            tk.Label(self.frame5, text="Y: ").grid(row=2, column=0)
            self.chooseY_exp = ttk.Combobox(self.frame5, values=self.exp_list_of_values, textvariable=self.currentYvar_exp, width=15)
            self.chooseY_exp.grid(row=2, column=1)
            tk.Label(self.frame5, text=" Factor: ").grid(row=1, column=2)
            tk.Label(self.frame5, text=" Factor: ").grid(row=2, column=2)
            tk.Label(self.frame5, text=" Offset: ").grid(row=1, column=4)
            tk.Label(self.frame5, text=" Offset: ").grid(row=2, column=4)
            self.x_factor_exp = tk.Text(self.frame5, height=1, width=10)
            self.x_factor_exp.grid(row=1, column=3)
            self.y_factor_exp = tk.Text(self.frame5, height=1, width=10)
            self.y_factor_exp.grid(row=2, column=3)
            self.x_offset_exp = tk.Text(self.frame5, height=1, width=10)
            self.x_offset_exp.grid(row=1, column=5)
            self.y_offset_exp = tk.Text(self.frame5, height=1, width=10)
            self.y_offset_exp.grid(row=2, column=5)
            for factor in [self.x_factor_forge, self.x_factor_exp, self.y_factor_forge, self.y_factor_exp]:
                factor.insert(tk.END, "1")
            for offset in [self.x_offset_forge, self.x_offset_exp, self.y_offset_forge, self.y_offset_exp]:
                offset.insert(tk.END, "0")
            self.plot_others_button_exp = tk.Button(self.frame5, text="Plot", command=self.plot_others_exp)
            self.plot_others_button_exp.grid(row=3, column=1)
            self.window2.mainloop()
        else:
            self.window2 = tk.Tk()
            self.window2.geometry("870x260")
            self.window2.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.frame1 = tk.LabelFrame(self.window2, text="Curve", height=400, width=200)
            self.frame2 = tk.LabelFrame(self.window2, text="Sensors")
            self.frame2.grid(row=0, column=0)
            self.folder_path = self.folders_paths[0]
            self.result_folder_path = self.result_folders_paths[0]
            self.CurvesCheckButtons = {}
            self.CurvesCheckButtonsVariables = {}
            for curve in self.curves:
                self.CurvesCheckButtonsVariables[curve] = tk.IntVar()
                self.CurvesCheckButtonsVariables[curve].set(0)
                self.CurvesCheckButtons[curve] = tk.Checkbutton(self.frame1, text=curve, variable=self.CurvesCheckButtonsVariables[curve])
                self.CurvesCheckButtons[curve].pack()
            self.frame1.grid(row=0, column=1)
            self.ButtonsGroupSensor = {}
            for key in list(self.sensors_names.keys()):
                self.ButtonsGroupSensor[key] = tk.Button(self.frame2, text="Group {}".format(str(key)), command=lambda nb=key: self.displayGroup_multiple(nb))
                self.ButtonsGroupSensor[key].pack()
            self.displayGroup_multiple(1)
            self.plotButton = tk.Button(self.frame1, text="Plot", command=self.plot_curves_multiple)
            self.plotButton.pack(side="bottom")
            self.frame4 = tk.LabelFrame(self.window2, text="Others")
            self.frame4.grid(row=0, column=3)
            self.list_of_values = []
            self.currentXvar = tk.StringVar()
            self.currentYvar = tk.StringVar()
            temp_list1 = self.variables_to_plot(1, 1)
            temp_list2 = self.variables_to_plot_upper_die()
            for elem in temp_list1:
                self.list_of_values.append(elem + " (Sensor)")
            for elem in temp_list2:
                self.list_of_values.append(elem + " (Upper die)")
            tk.Label(self.frame4, text="X: ").grid(row=0, column=0)
            self.chooseX = ttk.Combobox(self.frame4, values=self.list_of_values, textvariable=self.currentXvar, width=30)
            self.chooseX.grid(row=0, column=1)
            tk.Label(self.frame4, text="Y: ").grid(row=1, column=0)
            self.chooseY = ttk.Combobox(self.frame4, values=self.list_of_values, textvariable=self.currentYvar, width=30)
            self.chooseY.grid(row=1, column=1)
            tk.Label(self.frame4, text=" Factor: ").grid(row=0, column=2)
            tk.Label(self.frame4, text=" Factor: ").grid(row=1, column=2)
            tk.Label(self.frame4, text=" Offset: ").grid(row=0, column=4)
            tk.Label(self.frame4, text=" Offset: ").grid(row=1, column=4)
            self.x_factor_forge = tk.Text(self.frame4, height=1, width=10)
            self.x_factor_forge.grid(row=0, column=3)
            self.y_factor_forge = tk.Text(self.frame4, height=1, width=10)
            self.y_factor_forge.grid(row=1, column=3)
            self.x_offset_forge = tk.Text(self.frame4, height=1, width=10)
            self.x_offset_forge.grid(row=0, column=5)
            self.y_offset_forge = tk.Text(self.frame4, height=1, width=10)
            self.y_offset_forge.grid(row=1, column=5)
            self.plot_others_button = tk.Button(self.frame4, text="Plot", command=self.plot_others_multiple2)
            self.plot_others_button.grid(row=2, column=1)
            self.frame5 = tk.LabelFrame(self.frame4, text="Add Experimental Curve")
            self.frame5.grid(row=3, column=0, columnspan=6)
            tk.Label(self.frame5, text="File: ").grid(row=0, column=0)
            self.browseButton = tk.Button(self.frame5, text="Browse", command=self.browse_exp_file)
            self.browseButton.grid(row=0, column=1)
            self.exp_file_name_stringVar = tk.StringVar()
            self.exp_file_name_display = tk.Label(self.frame5, textvariable=self.exp_file_name_stringVar, width=30)
            self.exp_file_name_display.grid(row=0, column=2, columnspan=4)
            tk.Label(self.frame5, text="X: ").grid(row=1, column=0)
            self.currentXvar_exp, self.currentYvar_exp = tk.StringVar(), tk.StringVar()
            self.exp_list_of_values = []
            self.chooseX_exp = ttk.Combobox(self.frame5, values=self.exp_list_of_values, textvariable=self.currentXvar_exp, width=15)
            self.chooseX_exp.grid(row=1, column=1)
            tk.Label(self.frame5, text="Y: ").grid(row=2, column=0)
            self.chooseY_exp = ttk.Combobox(self.frame5, values=self.exp_list_of_values, textvariable=self.currentYvar_exp, width=15)
            self.chooseY_exp.grid(row=2, column=1)
            tk.Label(self.frame5, text=" Factor: ").grid(row=1, column=2)
            tk.Label(self.frame5, text=" Factor: ").grid(row=2, column=2)
            tk.Label(self.frame5, text=" Offset: ").grid(row=1, column=4)
            tk.Label(self.frame5, text=" Offset: ").grid(row=2, column=4)
            self.x_factor_exp = tk.Text(self.frame5, height=1, width=10)
            self.x_factor_exp.grid(row=1, column=3)
            self.y_factor_exp = tk.Text(self.frame5, height=1, width=10)
            self.y_factor_exp.grid(row=2, column=3)
            self.x_offset_exp = tk.Text(self.frame5, height=1, width=10)
            self.x_offset_exp.grid(row=1, column=5)
            self.y_offset_exp = tk.Text(self.frame5, height=1, width=10)
            self.y_offset_exp.grid(row=2, column=5)
            for factor in [self.x_factor_forge, self.x_factor_exp, self.y_factor_forge, self.y_factor_exp]:
                factor.insert(tk.END, "1")
            for offset in [self.x_offset_forge, self.x_offset_exp, self.y_offset_forge, self.y_offset_exp]:
                offset.insert(tk.END, "0")
            self.plot_others_button_exp = tk.Button(self.frame5, text="Plot", command=self.plot_others_exp2)
            self.plot_others_button_exp.grid(row=3, column=1)
            self.window2.mainloop()
            self.window2.mainloop()
    
    def erase_other_checkbuttons_sensors(self, sensor): 
        """
        This function erases all the other check buttons when one is selected (in 'Sensors'). Used in MODE 2 (two or more simulations).
        """
        for item in self.sensorCheckButtonsVariables.items():
            if item[1].get() == 1 and not item[0] == sensor:
                self.sensorCheckButtonsVariables[item[0]].set(0)

    def displayGroup(self, i): 
        """ 
        Display the sensors from group i in the sensor selection frame. It is called in MODE 1 (only one simulation to study, multiple sensor selection is allowed).

        Parameters
        ----------
        i: int. The sensor group number.

        Output
        ------
        None.

        """
        self.current_sensor_group = i
        self.frame2.destroy()
        self.frame2 = tk.LabelFrame(self.window2, text="Sensors", height=400, width=200)
        self.frame2.grid(row=0, column=0)
        self.ButtonsGroupSensor = {}
        for key in list(self.sensors_names.keys()):
            self.ButtonsGroupSensor[key] = tk.Button(self.frame2, text="Group {}".format(str(key)), command= lambda nb=key: self.displayGroup(nb))
            self.ButtonsGroupSensor[key].pack()
        self.sensorCheckbuttons = {}
        self.sensorCheckButtonsVariables = {}
        for sensor in self.sensors_names[i]:
            self.sensorCheckButtonsVariables[sensor] = tk.IntVar()
            self.sensorCheckButtonsVariables[sensor].set(1)
            self.sensorCheckbuttons[sensor] = tk.Checkbutton(self.frame2, text=sensor, variable=self.sensorCheckButtonsVariables[sensor])
            self.sensorCheckbuttons[sensor].pack()
        
    def displayGroup_multiple(self, i): 
        """ 
        Display the sensors from group i in the sensor selection frame. It is called in MODE 2 (two or more simulations, two sensors cannot be selected at the same time).

        Parameters
        ----------
        i: int. The sensor group number.

        Output
        ------
        None.

        """
        self.current_sensor_group = i
        self.frame2.destroy()
        self.frame2 = tk.LabelFrame(self.window2, text="Sensors", height=400, width=200)
        self.frame2.grid(row=0, column=0)
        self.ButtonsGroupSensor = {}
        for key in list(self.sensors_names.keys()):
            self.ButtonsGroupSensor[key] = tk.Button(self.frame2, text="Group {}".format(str(key)), command=lambda nb=key: self.displayGroup_multiple(nb))
            self.ButtonsGroupSensor[key].pack()
        self.sensorCheckbuttons = {}
        self.sensorCheckButtonsVariables = {}
        for sensor in self.sensors_names[i]:
            self.sensorCheckButtonsVariables[sensor] = tk.IntVar()
            self.sensorCheckButtonsVariables[sensor].set(0)
            self.sensorCheckbuttons[sensor] = tk.Checkbutton(self.frame2, text=sensor, variable=self.sensorCheckButtonsVariables[sensor], command= lambda sensor=sensor: self.erase_other_checkbuttons_sensors(sensor))
            self.sensorCheckbuttons[sensor].pack()
        self.sensorCheckButtonsVariables[self.sensors_names[i][0]].set(1)

    def variables_to_plot(self, sensor_group, sensor_name): 
        """
        Returns the list of columns of the sensors .vtf data
        """
        try:
            data = self.extract_data_from_vtf("billet_group{}_{}.vtf".format(sensor_group, sensor_name))
            return list(data.columns)
        except:
            return []

    def variables_to_plot_upper_die(self): 
        """
        Return the list of columns of the upper_die.vtf data
        """
        data = self.extract_data_from_vtf("upper_die.vtf")
        return list(data.columns)
    
    def browse_exp_file(self): 
        """
        Add and experimental data file, in order to compare it with simulation.
        """
        self.exp_file_path = askopenfilename()
        self.exp_file_name_stringVar.set(os.path.basename(self.exp_file_path))
        self.exp_data = pd.read_csv(self.exp_file_path, sep=";", skiprows=1)
        self.exp_data = self.add_equivalent_strain_exp(self.exp_data)
        try:
            self.exp_data["stress"] = self.exp_data["force"] * np.exp(self.exp_data[self.exp_strain_variable]) / self.exp_surface
        except:
            pass
        self.exp_list_of_values = list(self.exp_data.columns)
        self.chooseX_exp.destroy()
        self.chooseY_exp.destroy()
        self.chooseX_exp = ttk.Combobox(self.frame5, values=self.exp_list_of_values, textvariable=self.currentXvar_exp, width=28)
        self.chooseX_exp.grid(row=1, column=1)
        tk.Label(self.frame5, text="Y: ").grid(row=2, column=0)
        self.chooseY_exp = ttk.Combobox(self.frame5, values=self.exp_list_of_values, textvariable=self.currentYvar_exp, width=28)
        self.chooseY_exp.grid(row=2, column=1)

    def erase_other_checkbuttons_unique_curves(self, curve): 
        """
        This function erases all the other check buttons when one is selected (in 'unique curves').
        """
        for item in self.UniqueCurvesCheckButtonsVariables.items():
            if item[1].get() == 1 and not item[0] == curve:
                self.UniqueCurvesCheckButtonsVariables[item[0]].set(0)

### DATA EXTRACTION ### 
    def duplicate_for_analysis(self, result_folder_path, file_name): 
        """
        Duplicate the *.vtf considered file, in order not to disturb the FORGE analysis. The new file is *_for_analysis.vtf. It will be used by the extraction function which will slightly modify it to be able to extract its data.
        """
        path = result_folder_path + "/" + file_name
        new_path = result_folder_path + "/" + file_name[:-4] + "_for_analysis.vtf"
        if os.path.exists(new_path):
            os.remove(new_path)
        shutil.copyfile(path, new_path)
        return file_name[:-4] + "_for_analysis.vtf"

    def extract_data_from_vtf(self, file_name): 
        """
        Extract the data from the file_name .vtf file. Used in MODE 1 (only one simulation to study).
        
        Parameters
        ----------
        file_name: str. The name of the file (e.g. "billet_group1_1.vtf").
        
        Output
        ------
        data: pd.DataFrame. The data from the file
        """
        file_name = self.duplicate_for_analysis(self.result_folder_path, file_name) # starts by duplicating the considered *.vtf file.
        while True: # Add wide columns None to the file until it is able to read it.
            try:
                data = pd.read_csv(self.result_folder_path + "/" + file_name, skiprows=7, sep="\t")
                break
            except:
                lines = []
                with open(self.result_folder_path + "/" + file_name, "r") as f:
                    lines = f.readlines()
                    lines[7] = lines[7][:-1] + '\t"none"\n'
                with open(self.result_folder_path + "/" + file_name, "w") as f:
                    f.writelines(lines)
        data = pd.read_csv(self.result_folder_path + "/" + file_name, skiprows=7, sep="\t")
        data.columns = data.columns.str.strip()
        data = data[3:]
        data = data.set_index("Step")
        data = data.dropna(axis=1, how="any")
        data = data.astype(float)
        data = self.add_stress_triaxiality(data, file_name)
        return data
    
    def extract_data_from_multiple_vtf(self, file_name, result_folder_path): 
        """
        Extract the data from the file_name .vtf file. Used in MODE 2 (two or more simulations to study).
        
        Parameters
        ----------
        file_name: str. The name of the file (e.g. "billet_group1_1.vtf").
        result_folder_path: str. The name of the result folder (e.g. .../4_3D_Upsetting_2).
        
        Output
        ------
        data: pd.DataFrame. The data from the file.
        """
        file_name = self.duplicate_for_analysis(result_folder_path, file_name)
        while True:
            try:
                data = pd.read_csv(result_folder_path + "/" + file_name, skiprows=7, sep="\t")
                break
            except:
                lines = []
                with open(result_folder_path + "/" + file_name, "r") as f:
                    lines = f.readlines()
                    lines[7] = lines[7][:-1] + '\t"none"\n'
                with open(result_folder_path + "/" + file_name, "w") as f:
                    f.writelines(lines)
        data = pd.read_csv(result_folder_path + "/" + file_name, skiprows=7, sep="\t")
        data.columns = data.columns.str.strip()
        data = data[3:]
        data = data.set_index("Step")
        data = data.astype(float)
        data = data.dropna(axis=1, how="all")
        self.add_stress_triaxiality(data, file_name)
        return data

    def extract_data_sensors(self, sensor_group, sensor_names=[]): 
        """
        Extract the data of sensors in one group. Used in MODE 1 (only one simulation to study).

        Parameters
        ----------
        sensor_group: int. The group number of the considered sensors.
        sensor_names: list. The consired sensors (str). It empty, all the sensors of the group are considered.

        Returns
        -------
        data_sensors: dictionary. Index: (sensor_number, sensor_name) [int, str]. Value: pd.DataFrame (output of self.extract_data_from_vtf).
        """
        data_sensors = {}
        if sensor_names == []:
            for i, sensor_name in enumerate(self.sensors_names[sensor_group]):
                data_sensors[(i+1, sensor_name)] = self.extract_data_from_vtf("billet_group" + str(sensor_group) + "_" + str(i+1) + ".vtf")
        else:
            for sensor_name in sensor_names:
                i = self.sensors_names[sensor_group].index(sensor_name)
                data_sensors[(i+1, sensor_name)] = self.extract_data_from_vtf("billet_group" + str(sensor_group) + "_" + str(i+1) + ".vtf")
        return data_sensors

    def extract_data_sensors_multiple(self, sensor_group, sensor_name): 
        """
        Extract the data of the same sensor for multiple simulations. Used in MODE 2 (two or more simulations to study).

        Parameters
        ----------
        sensor_group: int. The group number of the considered sensor.
        sensor_name: str. The name of the sensor.

        Returns
        -------
        all_data: dictionary. Index: result_folder_path [str]. Values: pd.DataFrame containing the data of one sensor)
        """

        all_data = {}
        for result_folder_path in self.result_folders_paths:
            i = self.sensors_names[sensor_group].index(sensor_name)
            all_data[result_folder_path] =  self.extract_data_from_multiple_vtf("billet_group" + str(sensor_group) + "_" + str(i+1) + ".vtf", result_folder_path)
        return all_data

    def extract_force_vs_displacement_data(self): 
        """
        Extract the data of the upper die for multiple simulations. Used in MODE 2 (two or more simulations to study).

        Parameters
        ----------
        None.

        Returns
        -------
        data: dictionary. Index: result_folder_path [str]. Values: pd.DataFrame containing the data of the upper die)
        """
        data = {}
        for result_folder_path in self.result_folders_paths:
            data[result_folder_path] = self.extract_data_from_multiple_vtf("upper_die.vtf", result_folder_path)
        return data

    def add_equivalent_strain_exp(self, df): 
        """
        Add columns to the pd.DataFrame df corresponding to the equivalent strains. The equivalent strain is computed for each group of exx, eyy and exy data.
        """
        nb_to_compute = 0
        for column_name in list(df.columns):
            if "exx [1] - Hencky" in column_name:
                nb_to_compute += 1
        for i in range(nb_to_compute):
            suffixe = ""
            if i != 0:
                suffixe=".{}".format(i)
            e_xx = df["exx [1] - Hencky{}".format(suffixe)]
            e_yy = df["eyy [1] - Hencky{}".format(suffixe)]
            e_xy = df["exy [1] - Hencky{}".format(suffixe)]
            produit_doublement_contracte = e_xx * e_xx + e_yy * e_yy + 2 * e_xy * e_xy
            df["Equivalent_strain{}".format(suffixe)] = np.sqrt(2 / 3 * produit_doublement_contracte)
        return df
      
    def add_stress_triaxiality(self, data, file_name): 
        """
        Add two columns to the simulation (FORGE) data:
        - The Von Mises Stress
        - The Stress Triaxiality.
        """
        if file_name != "upper_die_for_analysis.vtf":
            data["Von Mises Stress"] = np.sqrt(0.5 * ( (data["Sigma XX"] - data["Sigma YY"])**2 + (data["Sigma YY"] - data["Sigma ZZ"])**2 + (data["Sigma ZZ"] - data["Sigma XX"])**2 + 6 * (data["Sigma XY"]**2 + data["Sigma YZ"]**2 + data["Sigma XZ"]**2) ))
            data["Stress triaxiality"] = 1 / 3 * (data["Sigma XX"] + data["Sigma YY"] + data["Sigma ZZ"]) / data["Von Mises Stress"]
        return data

### PLOT ###
    def check_legend(self, legend): 
        """
        Check if the legend corresponds to one of the provided LEGEND in the main.py file.

        Parameters
        ----------

        legend: str. The default legend (e.g. 3D_Upsetting)

        Returns
        -------
        legend: str. The modified or not legend.
        
        """
        if legend in list(self.legends.keys()):
            return self.legends[legend]
        return legend
    
    def plot_curves(self): 
        """
        Plots the selected curves in a matplotlib.pyplot subplot. Used in MODE 1 (one simulation to study).
        """
        self.sensors_to_plot = []
        self.curve_to_plot = ""
        self.curves_to_plot = []
        for item in self.sensorCheckButtonsVariables.items():
            if item[1].get() == 1:
                self.sensors_to_plot.append(item[0])
        acc = 0
        for item in self.CurvesCheckButtonsVariables.items():
            if item[1].get() == 1:
                acc += 1
                self.curve_to_plot = item[0]
                self.curves_to_plot.append(item[0])
        if acc == 1:
            if self.curve_to_plot == "Force vs. Displacement":
                self.plot_force_vs_displacement()
            if self.curve_to_plot == "Stress vs. Strain":
                self.plot_stress_vs_strain(sensor_group=self.current_sensor_group, sensor_names=self.sensors_to_plot)
            if self.curve_to_plot == "Strain vs. Time":
                self.plot_strain_vs_time(sensor_group=self.current_sensor_group, sensor_names=self.sensors_to_plot)
            if self.curve_to_plot == "PF vs. Damage":
                self.plot_PF_vs_damage(PF_value="Phase field", sensor_group=self.current_sensor_group, sensor_names=self.sensors_to_plot)
        else:
            self.curve_to_plot = ""
            nb_lignes = int(np.sqrt(acc))
            if np.abs(np.sqrt(acc) - int(np.sqrt(acc))) > 1e-6:
                nb_lignes += 1
            nb_colonnes = int(acc / nb_lignes)
            if nb_lignes * nb_colonnes < acc:
                nb_colonnes += 1
            fig, axes = plt.subplots(nb_lignes, nb_colonnes, figsize=(12, 7))
            if nb_colonnes == 1:
                fig, axes = plt.subplots(nb_lignes, figsize=(12, 7))
            for i in range(acc):
                lgn = i // nb_lignes
                if nb_colonnes == 1:
                    lgn = i
                col = i % nb_colonnes
                if self.curves_to_plot[i] == "Force vs. Displacement":
                    data_upper_die = self.plot_force_vs_displacement(graph_in_subplot=True)
                    if nb_colonnes != 1:
                        self.plot_in_subplot(data_upper_die, axes[lgn, col], "Displacement_Z", "FORCE_Z", "Displacement_Z (mm)", "FORCE_Z (tonnes)", "Force vs. Displacement")
                    else:
                        self.plot_in_subplot(data_upper_die, axes[lgn], "Displacement_Z", "FORCE_Z", "Displacement_Z (mm)", "FORCE_Z (tonnes)", "Force vs. Displacement")
                else:
                    data_sensors = self.plot_stress_vs_strain(sensor_group=self.current_sensor_group, sensor_names=self.sensors_to_plot, graph_in_subplot=True)
                    if self.curves_to_plot[i] == "Stress vs. Strain":
                        if nb_colonnes != 1:
                            self.plot_in_subplot(data_sensors, axes[lgn, col], "EQ_STRAIN", "EQ_STRESS", "Equivalent strain", "Equivalent stress", "Equivalent Stress vs. Equivalent Strain (sensors from group {})".format(self.current_sensor_group))
                        else:
                            self.plot_in_subplot(data_sensors, axes[lgn], "EQ_STRAIN", "EQ_STRESS", "Equivalent strain", "Equivalent stress", "Equivalent Stress vs. Equivalent Strain (sensors from group {})".format(self.current_sensor_group))
                    if self.curves_to_plot[i] == "Strain vs. Time":
                        if nb_colonnes != 1:
                            self.plot_in_subplot(data_sensors, axes[lgn, col], "Time", "EQ_STRAIN", "Time", "Equivalent strain", "Equivalent Strain vs. Time (sensors from group {})".format(self.current_sensor_group))
                        else:
                            self.plot_in_subplot(data_sensors, axes[lgn], "Time", "EQ_STRAIN", "Time", "Equivalent strain", "Equivalent Strain vs. Time (sensors from group {})".format(self.current_sensor_group))
                    if self.curves_to_plot[i] == "PF vs. Damage":
                        if nb_colonnes != 1:
                            self.plot_in_subplot(data_sensors, axes[lgn, col], self.damage_criterion, "Phase field", self.damage_criterion, "Phase Field", "Phase Field vs. Damage criterion (sensors from group {})".format(self.current_sensor_group))
                        else:
                            self.plot_in_subplot(data_sensors, axes[lgn], self.damage_criterion, "Phase field", self.damage_criterion, "Phase Field", "Phase Field vs. Damage criterion (sensors from group {})".format(self.current_sensor_group))
            plt.suptitle(self.check_legend(os.path.basename(self.folder_path)))
            fig.tight_layout()
            plt.show()

    def plot_curves_multiple(self): 
        """
        Plots the selected curves in a matplotlib.pyplot subplot. Used in MODE 2 (two or more simulations to study).
        """
        sensor_name = ""
        for (name, value) in self.sensorCheckButtonsVariables.items():
            if value.get() == 1:
                sensor_name = name
                break
        data = self.extract_data_sensors_multiple(self.current_sensor_group, sensor_name)
        curve_to_plot = ""
        curves_to_plot = []
        acc = 0
        for (name, value) in self.CurvesCheckButtonsVariables.items():
            if value.get() == 1:
                acc += 1
                curves_to_plot.append(name)
                curve_to_plot = name

        if acc == 1: # only one graph to plot
            title = ""
            plt.clf()
            if curve_to_plot == "Force vs. Displacement":
                data_upper_die = self.extract_force_vs_displacement_data()
                for (result_folder_path, data_simulation) in data_upper_die.items():
                    index = self.result_folders_paths.index(result_folder_path)
                    legend = os.path.basename(self.folders_paths[index])
                    plt.plot(data_simulation["Displacement_Z"], - data_simulation["FORCE_Z"], self.plot_type, label=self.check_legend(legend))
                    plt.xlabel("Displacement_Z (mm)")
                    plt.ylabel("Force (tonnes)")
                title = "Force vs. Displacement"
            for (result_folder_path, data_simulation) in data.items():
                index = self.result_folders_paths.index(result_folder_path)
                legend = os.path.basename(self.folders_paths[index])
                if curve_to_plot == "Stress vs. Strain":
                    plt.plot(data_simulation["EQ_STRAIN"], data_simulation["EQ_STRESS"], self.plot_type, label=self.check_legend(legend))
                    plt.xlabel("Strain")
                    plt.ylabel("Stress")
                    title = "Equivalent Stress vs. Equivalent Strain"
                if curve_to_plot == "Strain vs. Time":
                    plt.plot(data_simulation["Time"], data_simulation["EQ_STRAIN"], self.plot_type, label=self.check_legend(legend))
                    plt.xlabel("Time (s)")
                    plt.ylabel("Strain")
                    title = "Equivalent Strain vs. Time"
                if curve_to_plot == "PF vs. Damage":
                    plt.plot(data_simulation[self.damage_criterion], data_simulation[self.PF_criterion], self.plot_type, label=self.check_legend(legend))
                    plt.xlabel(self.damage_criterion)
                    plt.ylabel(self.PF_criterion)
                    title = "Phase Field vs. Damage criterion"
            if curve_to_plot != "Force vs. Displacement":
                title += " (sensor: group {} - {})".format(self.current_sensor_group, sensor_name)
            plt.title(title)
            plt.grid()
            plt.legend()
            plt.show()

        else: # multiple graphs to plot
            nb_lignes = int(np.sqrt(acc))
            if np.abs(np.sqrt(acc) - int(np.sqrt(acc))) > 1e-6:
                nb_lignes += 1
            nb_colonnes = int(acc / nb_lignes)
            if nb_lignes * nb_colonnes < acc:
                nb_colonnes += 1
            fig, axes = plt.subplots(nb_lignes, nb_colonnes, figsize=(12, 7))
            if nb_colonnes == 1:
                fig, axes = plt.subplots(nb_lignes, figsize=(12, 7))
            for i in range(acc):
                lgn = i // nb_lignes
                if nb_colonnes == 1:
                    lgn = i
                col = i % nb_colonnes
                for result_folder_path in self.result_folders_paths:
                    index = self.result_folders_paths.index(result_folder_path)
                    legend = os.path.basename(self.folders_paths[index])
                    if curves_to_plot[i] == "Force vs. Displacement":
                        data_upper_die = self.extract_force_vs_displacement_data()
                        if nb_colonnes != 1:
                            self.plot_in_subplot2(data_upper_die[result_folder_path], axes[lgn, col], "Displacement_Z", "FORCE_Z", self.check_legend(legend), "Displacement_Z (mm)", "FORCE_Z (tonnes)", "Force vs. Displacement")
                        else:
                            self.plot_in_subplot2(data_upper_die[result_folder_path], axes[lgn], "Displacement_Z", "FORCE_Z", self.check_legend(legend), "Displacement_Z (mm)", "FORCE_Z (tonnes)", "Force vs. Displacement")
                    else:
                        if curves_to_plot[i] == "Stress vs. Strain":
                            if nb_colonnes != 1:
                                self.plot_in_subplot2(data[result_folder_path], axes[lgn, col], "EQ_STRAIN", "EQ_STRESS", self.check_legend(legend), "Equivalent strain", "Equivalent stress", "Equivalent Stress vs. Equivalent Strain")
                            else:
                                self.plot_in_subplot2(data[result_folder_path], axes[lgn], "EQ_STRAIN", "EQ_STRESS", self.check_legend(legend), "Equivalent strain", "Equivalent stress", "Equivalent Stress vs. Equivalent Strain")
                        if curves_to_plot[i] == "Strain vs. Time":
                            if nb_colonnes != 1:
                                self.plot_in_subplot2(data[result_folder_path], axes[lgn, col], "Time", "EQ_STRAIN", self.check_legend(legend), "Time", "Equivalent strain", "Equivalent Strain vs. Time")
                            else:
                                self.plot_in_subplot2(data[result_folder_path], axes[lgn], "Time", "EQ_STRAIN", self.check_legend(legend), "Time", "Equivalent strain", "Equivalent Strain vs. Time")
                        if curves_to_plot[i] == "PF vs. Damage":
                            if nb_colonnes != 1:
                                self.plot_in_subplot2(data[result_folder_path], axes[lgn, col], self.damage_criterion, "Phase field", self.check_legend(legend), self.damage_criterion, "Phase Field", "Phase Field vs. Damage criterion")
                            else:
                                self.plot_in_subplot2(data[result_folder_path], axes[lgn], self.damage_criterion, "Phase field", self.check_legend(legend), self.damage_criterion, "Phase Field", "Phase Field vs. Damage criterion")
            title = "Comparison (sensor: group {} - {}) between\n".format(self.current_sensor_group, sensor_name)
            for i, folder_path in enumerate(self.folders_paths):
                title += os.path.basename(folder_path)
                if i == len(self.folders_paths) - 2:
                    title += " and "
                elif i == len(self.folders_paths) - 1:
                    title += "."
                else:
                    title += ", "
            plt.suptitle(title)
            fig.tight_layout()
            plt.show()

    def plot_others_exp(self): 
        """
        Manages the Others Frame (allowing to the select the X and Y variables, factors and offsets) WITH Experimental Curve. Used in MODE 1 (one studied simulation).
        """
        x_to_plot = self.currentXvar.get()
        y_to_plot = self.currentYvar.get()
        x_variable, partX = x_to_plot.split(" (")[0], x_to_plot.split(" (")[1][:-1]
        y_variable, partY = y_to_plot.split(" (")[0], y_to_plot.split(" (")[1][:-1]
        if partX == partY:
            plt.clf()
            plt.plot(self.exp_data[self.currentXvar_exp.get()]*float(self.x_factor_exp.get("1.0", "end-1c"))+float(self.x_offset_exp.get("1.0", "end-1c")), self.exp_data[self.currentYvar_exp.get()]*float(self.y_factor_exp.get("1.0", "end-1c"))+float(self.y_offset_exp.get("1.0", "end-1c")), self.plot_type_exp, label="EXPERIMENTAL")
            if partX == "Sensor":
                self.sensors_to_plot = []
                self.curve_to_plot = ""
                self.curves_to_plot = []
                for item in self.sensorCheckButtonsVariables.items():
                    if item[1].get() == 1:
                        self.sensors_to_plot.append(item[0])
                data = self.extract_data_sensors(self.current_sensor_group, self.sensors_to_plot)
                self.unitary_plot_factor(data, x_variable, y_variable, float(self.x_factor_forge.get("1.0", "end-1c")), float(self.y_factor_forge.get("1.0", "end-1c")), float(self.x_offset_forge.get("1.0", "end-1c")), float(self.y_offset_forge.get("1.0", "end-1c")), x_variable, y_variable, "{} vs. {} (sensors from group {})".format(x_variable, y_variable, self.current_sensor_group), legend="Simulation")
            else:
                data_upper_die = self.extract_data_from_vtf("upper_die.vtf")
                self.unitary_plot_factor(data_upper_die, x_variable, y_variable, float(self.x_factor_forge.get("1.0", "end-1c")), float(self.y_factor_forge.get("1.0", "end-1c")), float(self.x_offset_forge.get("1.0", "end-1c")), float(self.y_offset_forge.get("1.0", "end-1c")), x_variable, y_variable, "{} vs. {}".format(y_variable, x_variable), legend="Simulation")
            plt.legend()
            plt.show()

    def plot_others(self): 
        """
        Manages the Others Frame (allowing to the select the X and Y variables, factors and offsets) WITHOUT Experimental Curve. Used in MODE 1 (one studied simulation).
        """
        x_to_plot = self.currentXvar.get()
        y_to_plot = self.currentYvar.get()
        x_variable, partX = x_to_plot.split(" (")[0], x_to_plot.split(" (")[1][:-1]
        y_variable, partY = y_to_plot.split(" (")[0], y_to_plot.split(" (")[1][:-1]
        if partX == partY:
            if partX == "Sensor":
                self.sensors_to_plot = []
                self.curve_to_plot = ""
                self.curves_to_plot = []
                for item in self.sensorCheckButtonsVariables.items():
                    if item[1].get() == 1:
                        self.sensors_to_plot.append(item[0])
                data = self.extract_data_sensors(self.current_sensor_group, self.sensors_to_plot)
                self.unitary_plot_factor(data, x_variable, y_variable, float(self.x_factor_forge.get("1.0", "end-1c")), float(self.y_factor_forge.get("1.0", "end-1c")), float(self.x_offset_forge.get("1.0", "end-1c")), float(self.y_offset_forge.get("1.0", "end-1c")), x_variable, y_variable, "{} vs. {} (sensors from group {})".format(x_variable, y_variable, self.current_sensor_group))
            else:
                data_upper_die = self.extract_data_from_vtf("upper_die.vtf")
                self.unitary_plot_factor(data_upper_die, x_variable, y_variable, float(self.x_factor_forge.get("1.0", "end-1c")), float(self.y_factor_forge.get("1.0", "end-1c")), float(self.x_offset_forge.get("1.0", "end-1c")), float(self.y_offset_forge.get("1.0", "end-1c")), x_variable, y_variable, "{} vs. {}".format(y_variable, x_variable))
            plt.legend()
            plt.show()

    def plot_others_multiple2(self, clear=True): 
        """
        Manages the Others Frame (allowing to the select the X and Y variables, factors and offsets) WITHOUT Experimental Curve. Used in MODE 2 (two or more studied simulations).
        """
        if clear:
            plt.clf()
        x_to_plot = self.currentXvar.get()
        y_to_plot = self.currentYvar.get()
        x_variable, partX = x_to_plot.split(" (")[0], x_to_plot.split(" (")[1][:-1]
        y_variable, partY = y_to_plot.split(" (")[0], y_to_plot.split(" (")[1][:-1]
        if partX == partY:
            if partX == "Sensor":
                self.sensors_to_plot = []
                self.curve_to_plot = ""
                self.curves_to_plot = []
                for item in self.sensorCheckButtonsVariables.items():
                    if item[1].get() == 1:
                        self.sensors_to_plot.append(item[0])
                data = self.extract_data_sensors_multiple(self.current_sensor_group, self.sensors_to_plot[0])
                title = ""
                if self.complete_title:
                    title = "{} vs. {} (sensor: {} from group {})".format(y_variable, x_variable, self.sensors_to_plot[0], self.current_sensor_group)
                else:
                    title = "{} vs. {}".format(y_variable, x_variable)
                self.unitary_plot_factor2(data, x_variable, y_variable, float(self.x_factor_forge.get("1.0", "end-1c")), float(self.y_factor_forge.get("1.0", "end-1c")), float(self.x_offset_forge.get("1.0", "end-1c")), float(self.y_offset_forge.get("1.0", "end-1c")), x_variable, y_variable, title)
            else:
                data_upper_die = self.extract_force_vs_displacement_data()
                self.unitary_plot_factor2(data_upper_die, x_variable, y_variable, float(self.x_factor_forge.get("1.0", "end-1c")), float(self.y_factor_forge.get("1.0", "end-1c")), float(self.x_offset_forge.get("1.0", "end-1c")), float(self.y_offset_forge.get("1.0", "end-1c")), x_variable, y_variable, "{} vs. {}".format(y_variable, x_variable))
            plt.show()

    def plot_others_exp2(self): 
        """
        Manages the Others Frame (allowing to the select the X and Y variables, factors and offsets) WITH Experimental Curve. Used in MODE 2 (two or more studied simulations).
        """
        x_to_plot = self.currentXvar.get()
        y_to_plot = self.currentYvar.get()
        x_variable, partX = x_to_plot.split(" (")[0], x_to_plot.split(" (")[1][:-1]
        y_variable, partY = y_to_plot.split(" (")[0], y_to_plot.split(" (")[1][:-1]
        if partX == partY:
            plt.clf()
            plt.plot(self.exp_data[self.currentXvar_exp.get()]*float(self.x_factor_exp.get("1.0", "end-1c"))+float(self.x_offset_exp.get("1.0", "end-1c")), self.exp_data[self.currentYvar_exp.get()]*float(self.y_factor_exp.get("1.0", "end-1c"))+float(self.y_offset_exp.get("1.0", "end-1c")), self.plot_type_exp, label="EXPERIMENTAL")
            self.plot_others_multiple2(clear=False)

    def plot_unique_curve(self): 
        """
        The 'unique curves' are plots containing two y-axis. This function is used to plot only one of them (hence 'unique').
        """
        sensor_name = ""
        for (name, value) in self.sensorCheckButtonsVariables.items():
            if value.get() == 1:
                sensor_name = name
                break
        curve_to_plot = ""
        for (name, value) in self.UniqueCurvesCheckButtonsVariables.items():
            if value.get() == 1:
                curve_to_plot = name
                break
        i = self.sensors_names[self.current_sensor_group].index(sensor_name)
        data = self.extract_data_from_multiple_vtf("billet_group" + str(self.current_sensor_group) + "_" + str(i+1) + ".vtf", self.result_folders_paths[0])
        plt.clf()
        fig, host = plt.subplots(figsize=(8, 5), layout="constrained")
        ax1 = host.twinx()
        p0 = host.plot(data[self.unique_curves[curve_to_plot]["xvariable"]], data[self.unique_curves[curve_to_plot]["yvariable1"]], self.plot_type, color="blue", label=self.unique_curves[curve_to_plot]["ylabel1"])
        p1 = ax1.plot(data[self.unique_curves[curve_to_plot]["xvariable"]], data[self.unique_curves[curve_to_plot]["yvariable2"]], self.plot_type, color="red", label=self.unique_curves[curve_to_plot]["ylabel2"])
        host.set_xlabel(self.unique_curves[curve_to_plot]["xlabel"])
        host.set_ylabel(self.unique_curves[curve_to_plot]["ylabel1"])
        ax1.set_ylabel(self.unique_curves[curve_to_plot]["ylabel2"])
        host.yaxis.label.set_color(p0[0].get_color())
        ax1.yaxis.label.set_color(p1[0].get_color())
        host.legend(handles=p0+p1, loc="best")
        host.grid()
        plt.title(self.unique_curves[curve_to_plot]["title"] + " (sensor: {} from group {})".format(sensor_name, self.current_sensor_group))
        plt.show()

    def plot_in_subplot2(self, data, ax, xvariable, yvariable, label, xlabel, ylabel, title): 
        """
        Plots a curve in an matplotlib.pyplot subplot ax.
        
        Parameters
        ----------
        data: pd.DataFrame. Data.
        ax: <AxesSubplot: >. the subplot.
        xvariable: str. The column name of x data.
        yvariable: str. The column name of y data.
        xlabel: str. The label of x axis.
        ylabel: str. The label of y axis.
        title: str. The title of the plot.

        Returns
        ------
        None.

        """
        if xvariable == "Displacement_Z":
            ax.plot(data[xvariable], - data[yvariable], self.plot_type, label=label)
        else:
            ax.plot(data[xvariable], data[yvariable], self.plot_type, label=label)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend()
        ax.grid()

    def plot_force_vs_displacement(self, graph_in_subplot=False): 
        """
        Plot the Force vs. Displacement graph.
        If graph_in_subplot: does not plot anything, but return the pd.DataFrame extracte data.
        """
        data_upper_die = self.extract_data_from_vtf("upper_die.vtf")
        data_upper_die["FORCE_Z"] = - data_upper_die["FORCE_Z"]
        if graph_in_subplot:
            return data_upper_die
        self.unitary_plot(data_upper_die, "Displacement_Z", "FORCE_Z", "Displacement_Z (mm)", "FORCE_Z (tonnes)", "Force vs. Displacement")
        plt.show()

    def plot_stress_vs_strain(self, sensor_group, sensor_names=[], graph_in_subplot=False): 
        """
        Plot the Stress vs. Strain graph.
        If graph_in_subplot: does not plot anything, but return the pd.DataFrame extracte data.
        """
        data_sensors = self.extract_data_sensors(sensor_group, sensor_names)
        if graph_in_subplot:
            return data_sensors
        self.unitary_plot(data_sensors, "EQ_STRAIN", "EQ_STRESS", "Equivalent strain", "Equivalent stress", "Equivalent Stress vs. Equivalent Strain (sensors from group {})".format(sensor_group))
        plt.show()

    def plot_strain_vs_time(self, sensor_group, sensor_names=[], graph_in_subplot=False): 
        """
        Plot the Strain vs. Time graph.
        If graph_in_subplot: does not plot anything, but return the pd.DataFrame extracte data.
        """
        data_sensors = self.extract_data_sensors(sensor_group, sensor_names)
        if graph_in_subplot:
            return data_sensors
        self.unitary_plot(data_sensors, "Time", "EQ_STRAIN", "Time", "Equivalent strain", "Equivalent Strain vs. Time (sensors from group {})".format(sensor_group))
        plt.show()
        
    def plot_PF_vs_damage(self, PF_value, sensor_group, sensor_names=[], graph_in_subplot=False): 
        """
        Plot the Phase Field vs. Damage graph.
        If graph_in_subplot: does not plot anything, but return the pd.DataFrame extracte data.
        """
        data_sensors = self.extract_data_sensors(sensor_group, sensor_names)
        if graph_in_subplot:
            return data_sensors
        self.unitary_plot(data_sensors, self.damage_criterion, PF_value, self.damage_criterion, PF_value, "Phase Field vs. Damage criterion (sensors from group {})".format(sensor_group))
        plt.show()

    def unitary_plot(self, data, xvariable, yvariable, xlabel, ylabel, title): 
        """
        Plots a unique curve.
        
        Parameters
        ----------
        data: pd.DataFrame. Data.
        xvariable: str. The column name of x data.
        yvariable: str. The column name of y data.
        xlabel: str. The label of x axis.
        ylabel: str. The label of y axis.
        title: str. The title of the plot.

        Returns
        ------
        None.

        """
        plt.clf()
        if type(data) is dict: # sensor
            for data_sensor in data.items():
                plt.plot(data_sensor[1][xvariable], data_sensor[1][yvariable], self.plot_type, label="{} ({})".format(data_sensor[0][0], data_sensor[0][1]))
        else: # pd.DataFrame
            plt.plot(data[xvariable], data[yvariable], self.plot_type)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title + "\n" + os.path.basename(self.folder_path))
        plt.grid()
        plt.legend()

    def unitary_plot_factor(self, data, xvariable, yvariable, x_factor, y_factor, x_offset, y_offset, xlabel, ylabel, title, legend=""): 
        """
        Plots a unique curve with factor and offset for variables. Used in MODE 1 (only one simulation is studied).
        
        Parameters
        ----------
        data: pd.DataFrame. Data.
        xvariable: str. The column name of x data.
        yvariable: str. The column name of y data.
        x_factor: float. The factor for x variable.
        y_factor: float. The factor for y variable.
        x_offset: float. The offset for x variable.
        y_offset: float. The offset for y variable.
        xlabel: str. The label of x axis.
        ylabel: str. The label of y axis.
        title: str. The title of the plot.
        legend: str. the legend of the curve. If "", no legend is displayed.

        Returns
        ------
        None.

        """
        if type(data) is dict: # sensor
            for data_sensor in data.items():
                plt.plot(data_sensor[1][xvariable]*x_factor+x_offset, data_sensor[1][yvariable]*y_factor+y_offset, self.plot_type, label="{} ({})".format(data_sensor[0][0], data_sensor[0][1]))

        else: # pd.DataFrame
            if legend == "":
                plt.plot(data[xvariable]*x_factor+x_offset, data[yvariable]*y_factor+y_offset, self.plot_type)
            else:
                plt.plot(data[xvariable]*x_factor+x_offset, data[yvariable]*y_factor+y_offset, self.plot_type, label=legend)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title + "\n" + self.check_legend(os.path.basename(self.folder_path)))
        plt.grid()
        plt.legend()
    
    def unitary_plot_factor2(self, data, xvariable, yvariable, x_factor, y_factor, x_offset, y_offset, xlabel, ylabel, title, legend=""): 
        """
        Plots a unique curve with factor and offset for variables. Used in MODE 2 (two or more simulations are studied). The difference with function self.unitary_plot_factor is only the title of the plot.
        
        Parameters
        ----------
        data: pd.DataFrame. Data.
        xvariable: str. The column name of x data.
        yvariable: str. The column name of y data.
        x_factor: float. The factor for x variable.
        y_factor: float. The factor for y variable.
        x_offset: float. The offset for x variable.
        y_offset: float. The offset for y variable.
        xlabel: str. The label of x axis.
        ylabel: str. The label of y axis.
        title: str. The title of the plot.
        legend: str. the legend of the curve. If "", no legend is displayed.

        Returns
        ------
        None.

        """
        if type(data) is dict: # sensor
            for data_sensor in data.items():
                label = self.check_legend(os.path.basename(self.folders_paths[self.result_folders_paths.index(data_sensor[0])]))
                plt.plot(data_sensor[1][xvariable]*x_factor+x_offset, data_sensor[1][yvariable]*y_factor+y_offset, self.plot_type, label=label)

        else: # pd.DataFrame
            if legend == "":
                plt.plot(data[xvariable]*x_factor+x_offset, data[yvariable]*y_factor+y_offset, self.plot_type)
            else:
                plt.plot(data[xvariable]*x_factor+x_offset, data[yvariable]*y_factor+y_offset, self.plot_type, label=legend)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.grid()
        plt.legend()

    def plot_in_subplot(self, data, ax, xvariable, yvariable, xlabel, ylabel, title): 
        """
        Plot a curve in a subplot.
        
        Parameters
        ----------
        data: pd.DataFrame. The data.
        ax: <AxesSubplot: >. the subplot.
        xvariable: str. The column name of the x variable (in the data).
        yvariable: str. The column name of the y variable (in the data).
        xlabel: str. The label of x axis.
        ylabel: str. The label of y axis.
        title: str. The title of the plot.

        Returns
        -------
        None.

        """
        if type(data) is dict: # sensor
            for data_sensor in data.items():
                ax.plot(data_sensor[1][xvariable], data_sensor[1][yvariable], self.plot_type, label="{} ({})".format(data_sensor[0][0], data_sensor[0][1]))
        else: # pd.DataFrame
            ax.plot(data[xvariable], data[yvariable], self.plot_type)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid()
        ax.legend()

    def global_plot(self, sensor_group, sensor_names=[], phase_field="Phase Field"): 
        """
        This function is NOT ANYMORE USED in the code. It plots a (2, 2) subplot with the following curves:
        - Force vs. Displacement,
        - Stress vs. Strain,
        - Strain vs . Time,
        - Phase Field vs. Damage criterion.
        """
        fig, axes = plt.subplots(2, 2, figsize=(12, 7))
        data_upper_die = self.plot_force_vs_displacement(graph_in_subplot=True)
        self.plot_in_subplot(data_upper_die, axes[0, 0], "Displacement_Z", "FORCE_Z", "Displacement_Z (mm)", "FORCE_Z (tonnes)", "Force vs. Displacement")
        data_sensors = self.plot_stress_vs_strain(sensor_group=sensor_group, sensor_names=sensor_names, graph_in_subplot=True)
        self.plot_in_subplot(data_sensors, axes[0, 1], "EQ_STRAIN", "EQ_STRESS", "Equivalent strain", "Equivalent stress", "Equivalent Stress vs. Equivalent Strain (sensors from group {})".format(sensor_group))
        self.plot_in_subplot(data_sensors, axes[1, 0], "Time", "EQ_STRAIN", "Time", "Equivalent strain", "Equivalent Strain vs. Time (sensors from group {})".format(sensor_group))
        self.plot_in_subplot(data_sensors, axes[1, 1], self.damage_criterion, phase_field, self.damage_criterion, phase_field, "Phase Field vs. Damage criterion (sensors from group {})".format(sensor_group))
        plt.suptitle(os.path.basename(self.folder_path))
        fig.tight_layout()
        plt.show()
    
