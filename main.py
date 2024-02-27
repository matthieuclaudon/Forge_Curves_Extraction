### This program was written by Matthieu Claudon, from Mines Paris - PSL. ###

from analyse import *

### IMPORTANT PARAMETERS ###

SENSORS_NAMES = {1: ["My Sensor"]}
# SENSORS_NAMES = {1: ["Center", "Left Notch", "Right Notch", "Middle left", "Middle right"], 2: ["Center", "Top left", "Top center", "Top Notch", "Bottom right", "Bottom center", "Bottom Notch"], 3: ["Center", "Top", "Bottom"]}
LEGENDS = {"3D_Upsetting_4": "Simulation 1", "3D_Upsetting_5": "Simulation 2", "3D_Upsetting_22": "test"}
PLOT_TYPE = "."
PLOT_TYPE_EXP = "+"

### OTHER PARAMETERS ###

DAMAGE_CRITERION = "LATANDCN"
PF_CRITERION = "Phase field"
UNIQUE_CURVES = {"Stress & PF vs. Strain": {"xvariable": "EQ_STRAIN", "yvariable1": "EQ_STRESS", "yvariable2": "Phase field", "xlabel": "Strain", "ylabel1": "Stress", "ylabel2": "Phase Field", "title": "Stress & Phase Field vs. Strain"}}
EXP_SURFACE = 15 * 1.18 # mm^2
EXP_STRAIN_VARIABLE = "eyy [1] - Hencky.1"
COMPLETE_TITLE = True

if __name__ == "__main__":
    a = analyse(legends=LEGENDS, sensors_names=SENSORS_NAMES, damage_criterion=DAMAGE_CRITERION, unique_curves=UNIQUE_CURVES, PF_criterion=PF_CRITERION, plot_type=PLOT_TYPE, plot_type_exp=PLOT_TYPE_EXP, exp_surface=EXP_SURFACE, exp_strain_variable=EXP_STRAIN_VARIABLE)


