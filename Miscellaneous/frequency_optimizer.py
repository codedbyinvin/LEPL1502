from scipy.optimize import minimize_scalar
import numpy as np
import matplotlib.pyplot as plt

VCC, RL, L = 5, 200, 0.66*1e-3
t = np.linspace(0, 1e-4, 100000)

def dVHdL(T):
    return VCC*(RL*T*np.exp(T*RL/(2*L)))/(2*L**2 * (1 + np.exp(T*RL/(2*L)))**2)

def f(T):
    return 1/dVHdL(T)

res = minimize_scalar(f, method='Golden')
print("\n#########  T = ", res.x, "[s]")
print("#########  f = ", 1/res.x, "[Hz]\n")
plt.plot(t*1e6, dVHdL(t), label=r"$\frac{\partial V_H}{\partial L}$")
plt.axhline(y=dVHdL(res.x), color='k', linestyle='--')
plt.axvline(x=res.x*1e6, color='k', linestyle='--')
plt.plot(res.x*1e6, dVHdL(res.x), 'ro')
plt.legend(loc="upper right", fontsize='x-large')
plt.xlabel(r'$T$ $(\mu s)$')
plt.text(res.x*1e6 + 5,dVHdL(res.x) - 100,r'$T^* = {}\mu s$'.format(str(round(res.x*1e6,4))), color='r')

ax = plt.gca()
ax.get_yaxis().set_visible(False)
# plt.savefig('./frequency_optimization.svg')
plt.show()