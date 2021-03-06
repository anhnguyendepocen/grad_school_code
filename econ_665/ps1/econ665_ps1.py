########################################################################################################################
### ECON 665: PS1 - Triangles and rectangles in schooling
########################################################################################################################

# Import necessary packages
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FormatStrFormatter
from mpl_toolkits.axes_grid1 import make_axes_locatable
from inspect import getsourcefile
from os import chdir, mkdir, path, mkdir

# Set graph options
plt.rc('font', **{'family': 'serif', 'serif': ['lmodern']})
plt.rc('text', usetex=True)
matplotlib.rcParams["text.latex.preamble"].append(r'\usepackage{amsmath}')

# Specify name for main directory (just uses the file's directory)
mdir = path.dirname(path.abspath(getsourcefile(lambda:0))).replace('\\', '/')

# Set figures directory (doesn't need to exist)
fdir = '/figures'

# Create the figures directory if it doesn't exist
if not path.isdir(mdir+fdir):
    mkdir(mdir+fdir)

# Change directory to figures
chdir(mdir+fdir)

########################################################################################################################
### PS1Q1: Heatmap of lower bound on Mincer's beta
########################################################################################################################

# Create vector of interest rates
r_min = 0
r_max = .2
r_num = 101
r = np.array(np.linspace(r_min, r_max, r_num), ndmin=2)

# Create vector of ideal years of schooling
s_min = 0
s_max = 20
s_num = 101
s = np.array(np.linspace(s_min, s_max, s_num), ndmin=2)

# Calculate lower bounds on Mincer's beta
beta_min = (r.transpose() @ np.ones(r.shape)) * np.exp(r.transpose() @ s) * (1 + r.transpose() @ s)**(-1)

# Set up matrix of betas to plot
beta_min_plot = np.zeros(beta_min.shape)

# Set up a vector of cutoffs to categorize beta (the upper bound matters most)
cutoffs = np.linspace(0, .2, 511)

# Go through all lower bounds and categorize them according to the cutoffs
for i, c in enumerate(np.flip(cutoffs, axis=0)):
    if i == 0:
        beta_min_plot[(beta_min > c)] = c
    else:
        beta_min_plot[(beta_min > c) & (beta_min <= np.flip(cutoffs, axis=0)[i-1])] = c

# Set up plot
fig, ax = plt.subplots(figsize=(6.5,6.5))

# Make the heat map
cm = 'tab20c'
heatmap = ax.imshow(beta_min_plot, cmap=cm, interpolation='nearest')

# Make a color bar; first, set up an axis divider, to be able to regulate its height
divider = make_axes_locatable(ax)

# Create an axis for the color bar
cax = divider.append_axes("right", size="5%", pad=0.2)

# Plot the color bar
cbar = ax.figure.colorbar(heatmap, cax=cax)

# Select how many ticks to use
n_ticks=11

# Set ticks
ax.set_xticks(np.linspace(0, beta_min.shape[0]-1, n_ticks))
ax.set_yticks(np.linspace(0, beta_min.shape[1]-1, n_ticks))

# Set tick labels
ax.set_xticklabels(np.linspace(s_min, s_max, n_ticks))
ax.set_yticklabels(np.linspace(r_min, r_max, n_ticks))

# Label color bar
cbar.ax.set_ylabel(r"Lower bound on Mincer's $\beta$", fontsize=11, rotation=-90, va="bottom")

# Set axis labels
ax.set_xlabel(r'$s$', fontsize=11)
ax.set_ylabel(r'$r$', fontsize=11, rotation=0)

# Add some more space after the horizontal axis label
ax.yaxis.labelpad = 10

# Get rid of unnecessary whitespace
fig.tight_layout()

# Save and close the figure (the bbox_inches='tight' helps remove even more unwanted whitespace)
plt.savefig('r_s_heatmap.pdf', bbox_inches='tight')
plt.close()

########################################################################################################################
### PS1Q2.1: Gains from reallocation triangle - Graph
########################################################################################################################

# Define discount rate, f(0), and c(s) = gamma
r = .02
f_0 = 20000
gamma = 10000

# Define initial allocation s_0 and reallocation point s_1
s_0 = 9.75
s_1 = 9.93

# Make a range of values between the two for later use
delta_s = np.linspace(s_0, s_1, 2)

# Calculate f'(s) = zeta to make sure s_1 is optimal
zeta = (f_0 + gamma) / (1/r - s_1)

# Define a marginal benefit function
def MB(s, zeta=zeta, r=r):
    try:
        mb = np.ones(s.shape) * (zeta/r)
    except:
        mb = zeta/r
    return mb

# Define a marginal cost function
def MC(s, zeta=zeta, f_0=f_0, gamma=gamma): return f_0 + zeta * s + gamma

# Select years of schooling to plot over
s_min = 9.4  # Minimum
s_max = 10.4  # Maximum
s = np.linspace(s_min, s_max, 10000)  # Linear spare of years to plot

# Set up plot
fig, ax = plt.subplots(figsize=(6.5, 4.5))

# Plot marginal benefit and marginal cost, add labels to the curves (inside the graph)
ax.plot(s, MB(s), color='green')
ax.annotate(r"MB$= \frac{\zeta}{r}$", xy=(s_min*1.0005, MB(s_min)*1.0005), color='green', fontsize=11)
ax.plot(s, MC(s), color='blue')
ax.annotate(r'MC$= f(0) + \zeta s + \gamma$', xy=(s_min*1.0005, MC(s_min)*.999), color='blue', fontsize=11)

# Plot T_$ triangle plus annotation
ax.fill_between(delta_s, MB(delta_s), MC(delta_s), facecolor='none', hatch='\\', edgecolor='red', interpolate=True)
ax.annotate(r'$T_{\$}$', xy=(.995*(s_1 + s_0) / 2, MC(s_0) + .6*(s_1 - s_0)*zeta), color='red',
    fontsize=11, bbox=dict(boxstyle="circle, pad=.4", fc="white", ec="red"))

# Plot initial allocation and reallocation point
ax.axvline(x=s_0, ymax=(MB(s_0) - MC(s_min)*.999) / (MC(s_max)*1.001 - MC(s_min)*.999),
    linestyle='--', color='black')
ax.axvline(x=s_1, ymax=(MB(s_1) - MC(s_min)*.999) / (MC(s_max)*1.001 - MC(s_min)*.999),
    linestyle='--', color='black')

# Remove y ticks
plt.tick_params(axis='y', which='both',
    bottom='off', top='off', labelbottom='off', right='off', left='off', labelleft='off')

# Set x ticks at allocations only
ax.set_xticks([s_0, s_1])
ax.set_xticklabels(['$s^*_0$', '$s^*_1$'], fontsize=11)

# Set axis limits
ax.set_xlim(s_min, s_max)
ax.set_ylim(MC(s_min)*.9985, MC(s_max)*1.001)

# Label y axis, set label position (getting the dollar sign to show up is a bit of a pain)
ax.set_ylabel(r'$\$$', fontsize=11, rotation=0)
ax.yaxis.set_label_coords(-0.025, 1)

# Label x axis, set label position
ax.set_xlabel('$s$', fontsize=11)
ax.xaxis.set_label_coords(1, -0.025)

# Remove top and right axis spines, to make this look more like a graph
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

# Get rid of unnecessary whitespace
fig.tight_layout()

# Save figure and close
plt.savefig('q2_triangle.pdf')
plt.close()

########################################################################################################################
### PS1Q2.2: Point elasticities
########################################################################################################################

# Specify vector of discount rates to use
R = np.linspace(.01, .1, 10000)

# Define point elasticity function
def elasticity(r, s_0=s_0): return (1 / (r * s_0)) - 1

# Set up plot
fig, ax = plt.subplots(figsize=(6.5, 6.5))

# Plot point elasticities as a function of interest rates
ax.plot(R, elasticity(R), color='blue')
ax.axhline(y=.0663, linestyle='--', color='black')

# Format horizontal axis
ax.set_xlim(0, max(R))
ax.set_xlabel('r', fontsize=11)

# Format vertical axis
ax.set_ylim(0, max(elasticity(R)))
ax.set_ylabel(r'$\varepsilon_{s^*, \frac{\zeta}{r}}$', fontsize=11, rotation=0)

# Remove unnecessary whitespace
fig.tight_layout()

# Add some more space after the horizontal axis label
ax.yaxis.labelpad = 10

# Save figure and close
plt.savefig('q2_point_elasticities.pdf')
plt.close()

########################################################################################################################
### PS1Q4: School construction in the model - Graph 1 (cost shift)
########################################################################################################################

# Calculate original intercept
gamma_0 = zeta / r - f_0 - zeta * s_0

# Set up plot
fig, ax = plt.subplots(figsize=(6.5, 4.5))

# Plot original marginal benefit and original marginal cost curve, add labels to the curves (inside the graph)
ax.plot(s, MB(s), color='green')
ax.annotate(r"MB$= \frac{\zeta}{r}$", xy=(s_min*1.0005, MB(s_min)*1.0005), color='green', fontsize=11)
ax.plot(s, MC(s, gamma=gamma_0), color='blue', linestyle='--')
ax.annotate(r'MC$= f(0) + \zeta s + \gamma_0$',
    xy=(s_min*1.0005, MC(s_min, gamma=gamma_0)*.9987), color='blue', fontsize=11,
    bbox=dict(boxstyle="square, pad=.01", fc="white", ec="none", alpha=.85))

# Plot changed marginal cost curve, add label to the curve (inside the graph)
ax.plot(s, MC(s), color='blue')
ax.annotate(r'$\widetilde{\text{MC}}= f(0) + \zeta s + \gamma_0 - \gamma$',
    xy=(s_min*1.0005, MC(s_min)*.9987), color='blue', fontsize=11)

# Plot initial allocation and reallocation point
ax.axvline(x=s_0, ymax=(MB(s_0) - MC(s_min)*.999) / (MC(s_max)*1.001 - MC(s_min)*.999),
    linestyle='--', color='black')
ax.axvline(x=s_1, ymax=(MB(s_1) - MC(s_min)*.999) / (MC(s_max)*1.001 - MC(s_min)*.999),
    linestyle='--', color='black')

# Remove y ticks
plt.tick_params(axis='y', which='both',
    bottom='off', top='off', labelbottom='off', right='off', left='off', labelleft='off')

# Set x ticks at allocations only
ax.set_xticks([s_0, s_1])
ax.set_xticklabels(['$s^*_0$', '$s^*_1$'], fontsize=11)

# Set axis limits
ax.set_xlim(s_min, s_max)
ax.set_ylim(MC(s_min)*.9985, MC(s_max)*1.001)

# Label y axis, set label position (getting the dollar sign to show up is a bit of a pain)
ax.set_ylabel(r'$\$$', fontsize=11, rotation=0)
ax.yaxis.set_label_coords(-0.025, 1)

# Label x axis, set label position
ax.set_xlabel('$s$', fontsize=11)
ax.xaxis.set_label_coords(1, -0.025)

# Remove top and right axis spines, to make this look more like a graph
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

# Get rid of unnecessary whitespace
fig.tight_layout()

# Save figure and close
plt.savefig('q4_shift_cost_only.pdf')
plt.close()

########################################################################################################################
### PS1Q4: School construction in the model - Graph 2 (double shift)
########################################################################################################################

# Set original zeta below current one, to get some action in the graph (different slopes have to be apparent)
zeta_0 = .45 * zeta

# Set original interest rate above current one, for the same reason (this doesn't change in this problem, but it will
# look much more dramatic in the graph, since there'll be two levers to pull instead of one; otherwise, the two MC
# curves often look quite parallel)
r_0 = 1.0025 * r

# Calculate original intercept, so that the original MC curve hits the original MB curve at s_0
gamma_0 = zeta / r_0 - f_0 - zeta_0 * s_0

# Set up plot
fig, ax = plt.subplots(figsize=(6.5, 4.5))

# Plot original marginal benefit and marginal cost, add labels to the curves (inside the graph)
ax.plot(s, MB(s, r=r_0), color='green', linestyle='--')
ax.annotate(r"MB$= \frac{\zeta}{r}$", xy=(s_min*1.0005, MB(s_min, r=r_0)*1.0005), color='green', fontsize=11,
    bbox=dict(boxstyle="square, pad=.01", fc="white", ec="none", alpha=.85))
ax.plot(s, MC(s, gamma=gamma_0, zeta=zeta_0), color='blue', linestyle='--')
ax.annotate(r'MC$= f(0) + \zeta s + \gamma_0$',
    xy=(s_min*1.0005, MC(s_min, gamma=gamma_0, zeta=zeta_0)*.9987), color='blue', fontsize=11,
    bbox=dict(boxstyle="square, pad=.01", fc="white", ec="none", alpha=.85))

# Plot modified marginal benefit curve, add label to the curve (inside the graph)
ax.plot(s, MB(s), color='green',)
ax.annotate(r"$\widetilde{\text{MB}}= \frac{\tilde{\zeta}}{r}$",
    xy=(s_min*1.0005, MB(s_min)*1.0005), color='green', fontsize=11)
ax.plot(s, MC(s), color='blue')
ax.annotate(r'$\widetilde{\text{MC}}= f(0) + \tilde{\zeta} s + \gamma_0 - \gamma$',
    xy=(s_min*1.0005, MC(s_min)*.9987), color='blue', fontsize=11)

# Plot initial allocation and reallocation point
ax.axvline(x=s_0, ymax=(MB(s_0, r=r_0) - MC(s_min)*.999) / (MC(s_max)*1.001 - MC(s_min)*.999),
    linestyle='--', color='black')
ax.axvline(x=s_1, ymax=(MB(s_1) - MC(s_min)*.999) / (MC(s_max)*1.001 - MC(s_min)*.999),
    linestyle='--', color='black')

# Remove y ticks
plt.tick_params(axis='y', which='both',
    bottom='off', top='off', labelbottom='off', right='off', left='off', labelleft='off')

# Set x ticks at allocations only
ax.set_xticks([s_0, s_1])
ax.set_xticklabels(['$s^*_0$', '$s^*_1$'], fontsize=11)

# Set axis limits
ax.set_xlim(s_min, s_max)
ax.set_ylim(MC(s_min)*.9985, MC(s_max)*1.001)

# Label y axis, set label position (getting the dollar sign to show up is a bit of a pain)
ax.set_ylabel(r'$\$$', fontsize=11, rotation=0)
ax.yaxis.set_label_coords(-0.025, 1)

# Label x axis, set label position
ax.set_xlabel('$s$', fontsize=11)
ax.xaxis.set_label_coords(1, -0.025)

# Remove top and right axis spines, to make this look more like a graph
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

# Get rid of unnecessary whitespace
fig.tight_layout()

# Save figure and close
plt.savefig('q4_shift_both.pdf')
plt.close()
