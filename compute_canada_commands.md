# Compute Canada / Digital Research Alliance Commands Reference

## User & Job Monitoring

### Active Users & Job Status
```bash
who                           # Show active users on current node
squeue                        # See all running/pending jobs
sq                           # Shorthand for squeue -u $USER
scontrol show job JOBID      # Detailed information about specific job
```

### Resource Monitoring
```bash
# Monitor latest output file
tail -f output/$(ls -t output/ | head -1)

# 3-pane monitoring (htop + nvidia-smi + log tail)
srun --jobid JOBID --pty tmux new-session -d 'htop -u $USER' \; split-window -h 'watch nvidia-smi' \; split-window -v 'tail -f output/*-JOBID.out' \; attach

# Alternative with dynamic file detection
srun --jobid JOBID --pty tmux new-session -d 'htop -u $USER' \; split-window -h 'watch nvidia-smi' \; split-window -v 'tail -f output/$(ls -t output/ | head -1)' \; attach

# 2-pane monitoring (htop + nvidia-smi)
srun --jobid JOBID --pty tmux new-session -d 'htop -u $USER' \; split-window -h 'watch nvidia-smi' \; attach
```

## Job Management

### Job Control
```bash
scancel JOBID                # Cancel specific job
scancel -u $USER             # Cancel all your jobs
sinfo                        # Show partition/node information
scontrol hold JOBID          # Hold a job
scontrol release JOBID       # Release a held job
```

### Job Information
```bash
sacct                        # Show accounting information for jobs
sacct -j JOBID               # Show details for specific job
sstat JOBID                  # Show live statistics for running job
sprio -j JOBID               # Show job priority information
```

## File Transfer & Management

### Data Transfer
```bash
# Basic rsync
rsync mydata user@remote-host:/data/

# Recursive transfer with progress
rsync -avP source/ user@host:/destination/

# Example transfer to compute canada
rsync -r NEU_DETYOLOV63/ rayen@dtn.siku.ace-net.ca:/gpfs/scratch/rayen/NEU_DET_YOLOV63
```

### Git & Version Control
```bash
module load git-lfs          # Load Git LFS module
git lfs track "*.pkl"        # Track large files
```

## System Information

### Node & Resource Info
```bash
sinfo -N                     # Show all nodes and their state
squeue -t RUNNING            # Show only running jobs
squeue -t PENDING            # Show only pending jobs
free -h                      # Show memory usage
df -h                        # Show disk usage
lscpu                        # Show CPU information
nvidia-smi                   # Show GPU information
```

### Environment & Modules
```bash
module list                  # Show loaded modules
module avail                 # Show available modules
module load MODULE_NAME      # Load a module
module unload MODULE_NAME    # Unload a module
```

## Interactive Sessions

### Start Interactive Jobs
```bash
salloc --time=1:00:00 --ntasks=1 --gres=gpu:1    # Allocate interactive resources
srun --pty bash                                   # Start interactive shell
srun --jobid JOBID --pty bash                    # Connect to existing job
```

## Useful Aliases & Shortcuts

```bash
# Add to your ~/.bashrc
alias sq='squeue -u $USER'
alias myjobs='squeue -u $USER -o "%.10i %.20j %.8T %.10M %.6D %R"'
alias gpu='nvidia-smi'
alias nodes='sinfo -N'
```

## Tmux Quick Reference

```bash
# Inside tmux session:
Ctrl+b + "          # Split horizontally
Ctrl+b + %          # Split vertically  
Ctrl+b + arrow      # Navigate panes
Ctrl+b + d          # Detach session
Ctrl+b + x          # Close current pane
tmux attach         # Reattach to session
```

## Common SLURM Job Script Template

```bash
#!/bin/bash
#SBATCH --job-name=my_job
#SBATCH --account=def-username
#SBATCH --time=02:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --gres=gpu:1
#SBATCH --output=output/%N-%j.out
#SBATCH --error=output/%N-%j.err

# Load modules
module load python/3.9
module load cuda

# Your commands here
python your_script.py
```

## Quick Troubleshooting

### Job Issues
```bash
# Check job details if it's not running
scontrol show job JOBID

# Check available resources
sinfo -p PARTITION_NAME

# Check job efficiency after completion
seff JOBID
```

### File & Permission Issues
```bash
# Check disk quotas
quota -u $USER

# Check file permissions
ls -la filename

# Make script executable
chmod +x script.sh
```

## Resource Monitoring Commands

```bash
# Check GPU usage in real-time
watch -n 1 nvidia-smi

# Check CPU and memory usage
htop -u $USER

# Monitor network usage
iftop

# Check I/O usage
iotop
```