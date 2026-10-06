import matplotlib.pyplot as plt
import numpy as np

def computeLowpassFilter(omega_c):
    
    # Solving sin(x)/x = 10^(-3/20)
    x_array = np.linspace(0.001,np.pi, 1000)
    f = np.sin(x_array)/x_array - 10**(-3/20)

    index = np.argmin(np.abs(f)) # Getting the index of the minimum value

    x = x_array[index]
    print(f"x : {x}")

    N_approx = 2*x/omega_c
    print(f"Valeur approximative de N : {N_approx}")

    # Computing G(omega_c) with values around N

    N_array = np.arange(round(N_approx)-5, round(N_approx)+6)

    G_array = 20*np.log10(1/N_array * (np.sin(omega_c/2 * N_array)/(np.sin(omega_c/2)))) + 3 # Add 3 to all computed gains, to choose the closest to -3

    final_N = int(N_array[np.argmin(np.abs(G_array))])

    print(f"Valeur choisie pour N : {final_N}")

    h = np.ones(final_N)/final_N

    nb_points = 4096
    omegas = np.linspace(0, 2*np.pi, nb_points)
    H = np.fft.fft(h, nb_points)

    plt.plot(omegas, 20*np.log10(np.abs(H)))
    plt.show()


computeLowpassFilter(np.pi/1000)