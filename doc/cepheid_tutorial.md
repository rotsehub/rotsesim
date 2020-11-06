Cepheid Tutorial
================

MESA Instructions:

You must first copy the Cepheid module from the MESA directory to your home directory:

-the Cepheid module is called rsp_Cepheid and is located at /hpc/applications/mesa/r12115/star/test_suite/rsp_Cepheid


example:

cp -r /hpc/applications/mesa/r12115/star/test_suite/rsp_Cepheid /users/aawallace




In the rsp_Cepheid directory, there are several files which must be changed to properly use the module.



First, you must open two files, one called inlist and the other called inlist_rsp_Cepheid_header, and make the following changes:

1) delete the lines which contain mesa_dir = '../../..'


2) change the following lines from this:


extra_star_job_inlist1_name = '../../inlist_rsp_common'

extra_controls_inlist1_name = '../../inlist_rsp_common'

extra_pgstar_inlist1_name = '../../inlist_rsp_common'


to this:


extra_star_job_inlist1_name = 'inlist_rsp_common'

extra_controls_inlist1_name = 'inlist_rsp_common'

extra_pgstar_inlist1_name = 'inlist_rsp_common'




Now, you must copy the file called inlist_rsp_common to the rsp_Cepheid directory in your home directory; the file is located at /hpc/applications/mesa/r12115/star

example:

cp -r /hpc/applications/mesa/r12115/star/inlist_rsp_common /users/aawallace/rsp_Cepheid


In the rsp_Cepheid directory in your home directory, you must now edit the file inlist_rsp_Cepheid. This is where you will specify the starting parameters for your star's model. You can edit any combination of the five parameters: initial mass (RSP_mass), initial effetive temperature (RSP_Teff), initial luminosity (RSP_L), initial hydrogen mass fraction (RSP_X), and initial metal mass fraction (RSP_Z). The initial mass and luminosity are recorded in solar units, and the initial effective temperature is recorded in Kelvin. The hydrogen and metal mass fractions are dimensionless. Be sure to note what your values are, as these are critically important to the Cepheid simulation. The Cepheid module itself comes preloaded with the following values:

   RSP_mass = 4.165d0
   RSP_Teff = 6050
   RSP_L = 1438.8d0
   RSP_X = 0.73d0
   RSP_Z = 0.007d0

The d after the number represents the number of digits to the right of the decimal place (if my fortran is correct); this should not be changed.


You must also make the following changes to this file:

1) add an exclamation point before the following lines:

max_model_number = 16000

x_integer_ctrl(1) = 10 ! which period to check

x_ctrl(1) = 3.93338d0 ! expected period (in days)

2) add the following line under the section labelled & controls

RSP_max_num_periods = (insert a number here)

	-this last line specifies how many periods of pulsations you want your model to calculate. I was instructed by one of the developers to use 1000 as a benchmark; however, your models may converge before or after the 1000 periods are reached, depending on your initial conditions. Be aware that my preliminary test run on November 10-11 required around 2.5-3 hours to reach 1000 periods. I will provide more accurate data regarding simulation times at a later date.


The next file to edit is the file labelled history_columns.list. This file specifies the output of the MESA program. To change which of the listed variables are shown, either add or remove an exlamation point before the variable names; adding the exclamation point removes the variable from the output, while removing it leaves it in the output. The variables I have been using thus far are:

model_number
star_age
star_age_day
rsp_phase
rsp_period_in_days
rsp_num_periods
star_mass
radius
luminosity
effective_T

There are other potentially useful variables there, but these are the only ones I have worked with, as they are the most basic/familiar to me, in my opinion. Feel free to add and remove variables at will; however, I must note that I suspect that increasing the output of variables may prolong computation time, which is the rate-limiting factor in this program.

The next file that must be edited is called makefile and is located in the subdirectory make. You must delete the below line:


MESA_DIR = ../../../..


You must edit one final file before you can run your program in ManeFrame II: rn. Use vim to open the rn file:

vim rn

Then, you must add the following (instructions/info as to what each part does are written to the right of the hash symbol #):

#SBATCH -J <Name of file>       # job name to display in squeue
#SBATCH -p <name of partition>      # requested partition
#SBATCH -t <runtime> #max runtime in minutes; the more pulsation periods you choose to run, the higher this number should be. For 2000 cycles, I recommend about 500.
#SBATCH -p <some processor name> --mem= <some number> #tells Maneframe 2 to run in parallel processor
#SBATCH --mail-user <your email address> #tells Maneframe 2 to email aawallace@smu.edu with updates
#SBATCH --mail-type=all #tells Maneframe 2 to update me for when run begins, ends, fails, or is requeued

To see where these additions came from, look online at: http://faculty.smu.edu/csc/documentation/slurm.html#the-slurm-job-scheduler

Lastly, you must enter the following command to run the module:

export MESA_DIR=/hpc/applications/mesa/r12115 ; export OMP_NUM_THREADS=X ; export MESASDK_ROOT=/hpc/applications/mesa/mesasdk ; source $MESASDK_ROOT/bin/mesasdk_init.sh

-note that you must enter this command from the directory you have copied to wherever (likely your home directory) you have copied the rsp_Cepheid module in the very first step (ie where you have been editing all the files thus far)
-you must replace the X in "export OMP_NUM_THREADS=X" to a number; this number represents the number of cores on whatever processor you intend to use for the simulations

Then, while still in this directory, enter the following commands:

./mk

-this command will configure your module according to your instructions


chmod +x ./rn

sbatch ./rn

-this command will run your simulation

These codes will submit the simulation work to ManeFrame II to process; you will receive emails in the email address listed in the rn file with updates as to the state of the simulation. 

Once the simulation has finished, which will occur once the number of periods you specified is reached, the data you have simulated will be located in a file called history.data in the subdirectory LOGS. The data is ready for use.

However, you will likely find it extraordinarily easier to use the data from your computer/laptop via a user interface; in that case, secure copy the history.data file to a directory of your choice and try to open it using some kind of spreadsheet software (like excel or libreoffice).

==========================================================================================================================================================================

Ceph_init_params.py

This script generates the initial parameters necessary to simulate a star using MESA's rsp_Cepheid module. 

To use the script, use python3 to run the script as you would with a normal python3 script:

python3 Ceph_init_params.py


The command line will prompt you for an initial luminosity (in solar units) for the Cepheid you wish to simulate. The script will output all relevant values for MESA's rsp_Cepheid module: M (mass of star in solar units), L (luminosity of star in solar units; this value is the input which is entered when starting the script), T_eff (effetive temperature of star in K), X (initial hydrogen mass fraction), and Z (initial metal mass fraction).

The script does not produce an output file; all output is produced in the terminal.

The script calculates these parameters using the initial value for L, using equations that have been designed to model Milky Way Cepheid variable stars. Citations for the equations used in the script are provided at the bottom of the script's text.

==========================================================================================================================================================================

phot_per_sec.py

This script uses output generated by MESA (see above for details about MESA) to determine how many photons are generated by a star. The needed parameters from MESA are Rstar (the radius of the star in solar units), Teff (effective temperature of star in K), and star_age_day (age of star in day starting from beginning of MESA's simulation; this parameter is not used). You must specify the file which contains MESA's output in the line:

inputcsv = pd.read_csv(' ')

Note that the output from MESA must be contained in a csv file.

However, it must be noted that you must choose which parts of the simulated star file you use to create the star. For example, it likely occurs that early in the simulation, the star has not reached high amplitude pulsation as MESA works to create a stable model of the star. This can be observed if you create a plot of the luminosity output against time. Once you have decided on a period to use for the star, copy the period's values for Rstar, Teff, and star_age_day to a separate csv file. This file will be used as the base of the phot_per_sec.py script.

This file produces two output csv files: output1.txt and output2.txt. 

The file output1.txt contains three columns: the first column is Rstar (as provided by MESA), the second column is Teff (as provided by MESA), and the third column is the number of photons emitted per second by the star. It must be noted that there are ~70 rows for each set of Rstar-Teff; this is because the photons per second are calculated for all wavelengths in the ROTSE-III sensitivity range (from 299 nm to 1001 nm).

The file output2.txt contains three columns: Rstar, Teff, and the total number of photons emitted by the star per second across all wavelengths of the ROTSE-III sensitivity range (i.e. the number of photons emitted per second for each ~700 rows in output1.txt are summed to a single value; the single value is listed next to the corresponding pair of Rstar and Teff for which the photons per second have been calculated).

These two files exist because the ROTSE-III CCD has a different efficiency for each wavelength of light; at certain wavelengths, more photons may be necessary to excite electrons on the CCD than for other wavelengths. The response function has been provided by Govinda Dhungana and is available at the following link: https://github.com/gdhungana/SNEPM/blob/master/data/rotse_response_normalized.ecsv.

Be sure to either rename these files or move them out of this directory before running this script again, as this script will overwrite the preexisting files if they exist in the same directory.
