"""
rotsesim.pecvel

This code runs a peculiar velocity simulation that adds
random peculiar velocities to a simulated galaxy sample,
then finds H0 using a linear fit, attempting to mitigate
the effects of peculiar motion.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.odr import *

#- Define necessary functions for fitting and plotting
def fit_velocity(distance, h0):
    """
    Linear fit of velocity vs. distance
    """
    return h0 * distance

def fit_h0_disterrors(distance,disterr,velocity):
    """
    Use ODR to fit h0 using distance errors
    """
    model   = Model(fit_velocity)
    data    = RealData(distance,velocity,sx=disterr)
    odr     = ODR(data,model,beta0=[0.])
    out     = odr.run()
    fith0   = out.beta[0]
    errh0   = out.sd_beta[0]
    chi2dof = out.res_var

    return fith0,errh0,chi2dof

def fit_h0_dist_vel_errors(distance,disterr,velocity,velerr,beta=None):
    """
    Use ODR to fit h0 using errors in distance and velocity
    """
    if beta:
        beta0 = beta
    else:
        beta0 = 0.
    model   = Model(fit_velocity)
    data    = RealData(distance,velocity,sx=disterr,sy=velerr)
    odr     = ODR(data,model,beta0=[beta0])
    out     = odr.run()
    fith0   = out.beta[0]
    errh0   = out.sd_beta[0]
    chi2dof = out.res_var
    yerr    = out.eps

    return fith0,errh0,chi2dof,yerr

def plot_h0_histogram(h0values,h0mean,h0std):
    """
    Plot histogram fit h0 values
    """
    nbins = np.int(np.max(h0values) - np.min(h0values))
    plt.xlabel('H0',fontsize=20)
    plt.ylabel('counts per bin',fontsize=20)
    plt.title('H0 distribution (H0 mock: avg = {:0.4f}, std = {:0.4f}'.format(h0mean,h0std),fontsize=20)
    plt.hist(h0values,bins=nbins)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.show()

def plot_h0errors_histogram(h0errors,h0errors_mean,h0errors_std):
    """
    Plot histogram fit h0 errors
    """
    nbins = np.int(np.max(h0errors) - np.min(h0errors))
    plt.xlabel('H0 errors',fontsize=20)
    plt.ylabel('counts per bin',fontsize=20)
    plt.title('H0 error distribution (H0 error: avg = {:0.4f}, std = {:0.4f}'.format(h0errors_mean,h0errors_std),fontsize=20)
    plt.hist(h0errors,bins=nbins)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.show()

def plot_h0_mean_iterations(h0mean):
    """
    Plot progression of h0 mean after iterating
    """
    plt.title('H0 average progression, final H0 = {:0.4f}'.format(h0mean[-1]),fontsize=20)
    plt.xlabel('iteration',fontsize=20)
    plt.ylabel('H0 mean',fontsize=20)
    iteration = np.arange(len(h0mean)) + 1
    plt.plot(iteration,h0mean)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.show()

def plot_h0_std_iterations(h0std):
    """
    Plot progression of h0 rms after iterating
    """
    plt.title('H0 rms progression, final H0 rms = {:0.4f}'.format(h0std[-1]),fontsize=20)
    plt.xlabel('iteration',fontsize=20)
    plt.ylabel('H0 rms',fontsize=20)
    iteration = np.arange(len(h0std)) + 1
    plt.plot(iteration,h0std)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.show()

def pecvel_sim(h0,distance,disterr,pecvel,ngal,nsim,iterations,plothist,plotprog,seed):
    if seed is not None:
        np.random.seed(seed)
        seeds = np.random.randint(2**30, size=nsim)

    #- Generate ngal mock galaxies for nsim simulations
    dist_all    = []
    disterr_all = []
    vel_all     = []
    velerr_all  = []
    fith0_all   = []
    h0err       = []
    totchi2     = []
    for sim in range(nsim):
        #- Simulate distances shifted by random amount based on measurement error
        if seed:
            np.random.seed(seeds[sim])
        dist = np.random.uniform(distance[0],distance[1],ngal)
        if seed:
            np.random.seed(seeds[sim])
        derr = np.random.normal(disterr[0],disterr[1],ngal)
        disterror = dist*derr
        vel = h0*dist
        if seed:
            np.random.seed(seeds[sim])
        dist = dist + np.random.uniform(-np.abs(disterror),np.abs(disterror),ngal)
        dist_all.append(dist)
        disterr_all.append(disterror)

        #- Simulate galaxy velocities including peculiar velocities
        if seed:
            np.random.seed(seeds[sim])
        vpec = np.random.uniform(-pecvel,pecvel,ngal)
        vel = vel + vpec
        vel_all.append(vel)

        #- Fit h0
        fith0, errh0, chi2 = fit_h0_disterrors(dist,disterror,vel)
        fith0_all.append(fith0)
        h0err.append(errh0)
        totchi2.append(chi2)

        #- Save difference in velocities from fit as errors
        fitvel = fith0 * dist
        verr = fitvel - vel
        velerr_all.append(verr)

    h0mean = np.mean(fith0_all)
    h0std = np.std(fith0_all)
    h0errmean = np.mean(h0err)
    chi2mean = np.mean(totchi2)

    print("Initial fit of H0 average = {:0.4f}, rms = {:0.4f}, err = {:0.4f}, chi2 = {:0.4f}\n".format(h0mean,h0std,h0errmean,chi2mean))

    #- Plot histogram of h0 values after inital fit
    if plothist:
        plot_h0_histogram(fith0_all,h0mean,h0std)

    #- Refit h0 after taking errors into accounts and removing outliers
    h0mean_tot = []
    h0std_tot  = []
    for iteration in range(iterations):
        print("Iteration",iteration+1)
        if iteration == 0:
            dist_iter = dist_all
            disterr_iter = disterr_all
            vel_iter = vel_all
            velerr_iter = 300.*np.ones(len(velerr_all))
            beta = fith0_all
        else:
            velerr_iter = 300.*np.ones(len(velerr_all))
            beta = fith0_iter

        fith0_iter      = []
        velerr_iter_new = []
        h0err_iter      = []
        chi2_iter       = []
        for sim in range(len(dist_iter)):
            #- Fit h0, update velocity errors, refit
            fith0_new, h0err, chi2, yerr = fit_h0_dist_vel_errors(dist_iter[sim],disterr_iter[sim],vel_iter[sim],velerr_iter[sim],beta=beta[sim])

            #- Calculate new velocity errors
            fitvel_new = fith0_new * dist_iter[sim]
            velerr_new = 300.*np.ones(ngal)

            fith0_iter.append(fith0_new)
            velerr_iter_new.append(velerr_new)
            h0err_iter.append(h0err)
            chi2_iter.append(chi2)

        h0mean_iter = np.mean(fith0_iter)
        h0std_iter = np.std(fith0_iter)

        h0mean_tot.append(h0mean_iter)
        h0std_tot.append(h0std_iter)

        h0errmean_iter = np.mean(h0err_iter)
        h0errstd_iter = np.std(h0err_iter)
        chi2mean_iter = np.mean(chi2_iter)

        print("H0 average = {:0.4f}, rms = {:0.4f}, err = {:0.4f}, rmserr = {:0.4f}\n".format(h0mean_iter,h0std_iter,h0errmean_iter,h0errstd_iter))

    #- Plot histogram of h0 values after final fit
    if plothist:
        plot_h0_histogram(fith0_iter,h0mean_iter,h0std_iter)
        plot_h0errors_histogram(h0err_iter,h0errmean_iter,h0errstd_iter)

    #- Plot progression of h0 average and rms
    if plotprog:
        plot_h0_mean_iterations(h0mean_tot)
        plot_h0_std_iterations(h0std_tot)

    
