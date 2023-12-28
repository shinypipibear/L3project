#!/bin/bash
#SBATCH -N 1 # Request a single node
#SBATCH -c 4 # Request four CPU cores
#SBATCH -p cpu # Use the res-gpu-small partition
#SBATCH --qos=short # Use the short QOS
#SBATCH -t 1-0 # Set maximum walltime to 1 day
#SBATCH --job-name=project # Name of the job
#SBATCH --mem=4G # Request 4Gb of memory

# Source the bash profile (required to use the module command)
source /etc/profile


# Run your program (replace this with your program)
python3 crime_data.py