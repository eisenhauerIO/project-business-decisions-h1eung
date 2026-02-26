#!/bin/bash
#SBATCH --account=p32484  ## YOUR ACCOUNT pXXXX or bXXXX
#SBATCH --partition=normal  ### PARTITION (buyin, short, normal, w10001, etc)
#SBATCH --array=0-2719 ## number of jobs to run "in parallel" 
#SBATCH --nodes=1 ## how many computers do you need
#SBATCH --ntasks-per-node=1 ## how many cpus or processors do you need on each computer
#SBATCH --time=48:00:00 ## how long does this need to run (remember different partitions have restrictions on this param)
#SBATCH --mem-per-cpu=1G ## how much RAM do you need per CPU (this effects your FairShare score so be careful to not ask for more than you need))
#SBATCH --job-name="sample_job_\${SLURM_ARRAY_TASK_ID}" ## use the task id in the name of the job
#SBATCH --output=/home/hgz5390/npnetwork_RR/RR_simulation_node_level/quest_output/sample_job.%A_%a.out ## use the jobid (A) and the specific job index (a) to name your log file

module purge all                ## Unload existing modules
module load python-miniconda3  		## Load necessary modules (software, libraries)

eval "$(conda shell.bash hook)"
conda activate my-virtenv-py38

# read in each row of the input_arguments text file into an array called input_args
IFS=$'\n' read -d '' -r -a input_arguments < input_arguments.txt

# Use the SLURM_ARRAY_TASK_ID varaible to select the correct index from input_arguments and then split the string by whatever delimiter you chose (in our case each input argument is split by a space)
IFS=' ' read -r -a input_args <<< "${input_arguments[$SLURM_ARRAY_TASK_ID]}"


# Pass the input arguments associated with this SLURM_ARRAY_TASK_ID to your function.
python /home/hgz5390/npnetwork_RR/RR_simulation_node_level/simulation_test_node_level_treatment.py --input-argument-1 ${input_args[0]} --input-argument-2 ${input_args[1]} --input-argument-3 ${input_args[2]} --input-argument-4 ${input_args[3]} --input-argument-5 ${input_args[4]} --input-argument-6 ${input_args[5]} --input-argument-7 ${input_args[6]} --input-argument-8 ${input_args[7]}



