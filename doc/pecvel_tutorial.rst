Peculiar Velocity Simulation Tutorial
=====================================

This script generates mock galaxies with random distance and velocity properties, fitting H0 after simulating peculiar velocities for each mock galaxy. 

Command line arguments:
* h0 (float): value of h0 to use for simulating mock velocities
* distance (float): range of distances to simulate in Mpc
* disterr (float): mean and standard deviation of distance errors
* pecvel (float): standard deviation in km/s for Gaussian distribution of peculiar velocities
* ngal (int): number of galaxies to simulate
* nsim (int): number of simulations each containing ngal mock galaxies
* iterations (int): number of times to iterate after rejecting outliers
* plothist (bool): plot h0 histogram after initial fit
* plotprog (bool): plot progress of H0 average and rms after iterating

Example command line run::

$> pecvel --h0 70. --distance  5. 30. --disterr 0.2 0.05 --pecvel 300. --ngal 10 --nsim 1000 --iterations 30 --plothist --plotprog

The output is simply plots showing progression of h0 mean and standard deviation after rejecting outliers following each iteration as well as fit H0 values shown in the terminal.

