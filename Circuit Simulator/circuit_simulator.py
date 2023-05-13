import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

########################## 
### Circuit Parameters ###

## Time parameters ##
SAMPLES = 100000
t_start, t_end = 0, 1e-3
t = np.linspace(t_start, t_end, SAMPLES)

## CIRCUIT PARAMETERS ##

PARAM = {
    'RG1':10e4,
    'RG2':10e4,
    'RG3':10e4,
    'RG': 13e3,
    'CG': 470e-12,
    'L1':0.67e-3,
    'L2':0.61e-3,
    'RL':200,
    'CDET': 1e-6,
    'RDET': 100e3,
    'Rsous1': 20e3,
    'Rsous2': 80e3,
    'Rsous3': 20e3,
    'Rsous4': 80e3,
    'VZ': 4.3,
    'VCC': 5
}

##########################

##########################
### PLOT CONFIGURATION ###
X_START, X_END = 0, 50
Y_START, Y_END = -1, 6
TITLE = "Simulation du circuit complet"
##########################

##########################
### Circuit Simulation ###

def oscillator(T, data):
    """
    Simulate the oscillator circuit
    """
    RG1, RG2, RG3, RG, CG, VCC = data['RG1'], data['RG2'], data['RG3'], data['RG'], data['CG'], data['VCC']
    f = 1 / (2*RG*CG*np.log(2))
    return T, signal.square(2*np.pi*f*T)*VCC/2 + VCC/2


def coil(T, data, VS, metal = False):
    """Simulate the coil

    Args:
        T (numpy array): Array of time values
        data (numpy array): Array of circuit parameters
        VS (numpy array): Array of input voltages

    Returns:
        Array: times values at which the coil voltage was calculated
        Array: coil voltage values
    """
    RL = data['RL']
    if metal:
        L = data['L2']
    else:
        L = data['L1']
    VL = np.zeros(len(T))
    for i in range(1, len(T)):
        h = T[i] - T[i-1]
        VL[i] = VL[i-1] + h*RL*(VS[i-1] - VL[i-1])/L
    return T, VL


def spike_detector(T, data, VL):
    """Simulate the spike detector circuit

    Args:
        T (Numpy array): array of time values
        data (Numpy array): array of circuit parameters
        VL (Numpy array): array of input voltages

    Returns:
        Numpy array: array of times at which the spike detector voltage was calculated
        Numpy array: array of spike detector voltage values
    """
    RDET, CDET = data['RDET'], data['CDET']
    VC = np.zeros(len(T))
    for i in range(1, len(T)):
        if VC[i-1] <= VL[i]:
            VC[i] = VL[i]
        else:
            h = T[i] - T[i-1]
            VC[i] = VC[i-1] - h*VC[i-1]/(RDET*CDET)
    return T, VC

def soustractor(T, data, VC):
    """Simulate the soustractor circuit
    """
    Rsous1, Rsous2, Rsous3, Rsous4, VZ = data['Rsous1'], data['Rsous2'], data['Rsous3'], data['Rsous4'], data['VZ']
    VF = np.zeros(len(T))
    for i in range(1, len(T)):
        VF[i] = Rsous2*(Rsous3+Rsous4)/(Rsous3*(Rsous1+Rsous2))*VZ - Rsous4/Rsous3*VC[i]
    return T, VF

if __name__ == "__main__":
    # Run simulation
    VS = oscillator(t, PARAM)[1]
    VL1 = coil(t, PARAM, VS, False)[1]
    VL2 = coil(t, PARAM, VS, True)[1]
    VC1 = spike_detector(t, PARAM, VL1)[1]
    VC2 = spike_detector(t, PARAM, VL2)[1]
    VF1 = soustractor(t, PARAM, VC1)[1]
    VF2 = soustractor(t, PARAM, VC2)[1]

    # Plot results
    plt.plot(t*1e6 - 100, VS, label="$V_{S}$", color="darkred")
    plt.plot(t*1e6 - 100, VL1, label="$V_{L1}$", color="darkred")
    plt.plot(t*1e6 - 100, VL2, label="$V_{L2}$", color="blue")
    plt.plot(t*1e6 - 100, VC1, label="$V_{C1}$", color="darkred")
    plt.plot(t*1e6 - 100, VC2, label="$V_{C2}$", color="blue")
    plt.plot(t*1e6 - 100, VF1, label="$V_{F1}$", color="darkred")
    plt.plot(t*1e6 - 100, VF2, label="$V_{F2}$", color="blue")

    plt.xlim(X_START, X_END)
    plt.ylim(Y_START, Y_END)
    plt.xlabel('Temps (µs)')
    plt.ylabel('Tension (V)')
    plt.title (TITLE)
    plt.legend(loc="upper right", fontsize='x-large')
    plt.rcParams["figure.figsize"] = [7.00, 3.50]
    plt.rcParams["figure.autolayout"] = True
    plt.show()