squeue -t RUNNING -o "%b" | grep "gpu" | awk -F: '{print $NF}' | awk '{sum+=$1; count++} END {print "Running jobs with GPUs: " count "\nTotal GPUs in use: " sum}'
squeue -t PENDING -o "%b" | grep "gpu" | awk -F: '{print $NF}' | awk '{sum+=$1; count++} END {print "Pending jobs with GPUs: " count "\nTotal GPUs requested: " sum}'
echo "=== RUNNING JOBS BY USER ===" && squeue -t RUNNING -o "%.8u %b" | grep "gpu" | awk -F: '{user=$1; gsub(/^[ \t]+/, "", user); gpus=$NF+0; users[user]+=gpus; jobs[user]++} END {for(u in users) printf "%-12s %3d jobs  %4d GPUs\n", u, jobs[u], users[u]}' | sort -k5 -rn
echo "=== PENDING JOBS BY USER ===" && squeue -t PENDING -o "%.8u %b" | grep "gpu" | awk -F: '{user=$1; gsub(/^[ \t]+/, "", user); gpus=$NF+0; users[user]+=gpus; jobs[user]++} END {for(u in users) printf "%-12s %3d jobs  %4d GPUs\n", u, jobs[u], users[u]}' | sort -k5 -rn | head -30

squeue -t PENDING -o "%A" | tail -n +2 | awk -v target=11512128 'BEGIN {above=0; below=0} {if ($1 > target) above++; else if ($1 < target) below++} END {print "Jobs above 11512128: " above "\nJobs below 11512128: " below}'
squeue -t PENDING -o "%A %b" | tail -n +2 | grep "gpu" | awk -v target=11512128 'BEGIN {above=0; below=0} {if ($1 > target) above++; else if ($1 < target) below++} END {print "GPU jobs above 11512128: " above "\nGPU jobs below 11512128: " below}'
GPU jobs above 11512128: 1224
GPU jobs below 11512128: 122

YOUR_PRIORITY=$(squeue -u $USER -t PENDING -j 11512128 -o "%Q" | tail -1); echo "Your job priority: $YOUR_PRIORITY"; squeue -t PENDING -o "%Q %b" | tail -n +2 | grep "gpu" | awk -v prio="$YOUR_PRIORITY" '{if ($1 > prio) count++} END {print "GPU jobs with higher priority: " count}'
Your job priority: 1796878
GPU jobs with higher priority: 1036

YOUR_PRIORITY=$(squeue -u $USER -t PENDING -j 13486344 -o "%Q" | tail -1); echo "Your job priority: $YOUR_PRIORITY"; squeue -t PENDING -o "%Q %b" | tail -n +2 | grep "gpu" | awk -v prio="$YOUR_PRIORITY" '{if ($1 > prio) count++} END {print "GPU jobs with higher priority: " count}'
Your job priority: 1750944
GPU jobs with higher priority: 983
Use man squeue when:

You need detailed explanations
Looking for format specifier details (%Q, %i, etc.)
Want examples and context
Need to understand behavior in depth
Use squeue --help when:

Quick reminder of option flags
Checking if a flag exists (-t, -u, etc.)
Need a fast reference
Just want the syntax
Pro tip: Use squeue --helpformat to see all available format specifiers (the % codes for -o option).



SLURM Pending Reasons Explained:
Priority (15,958 jobs)
Job is waiting in queue due to lower priority
Other jobs with higher priority are ahead in the queue
Most common reason - just waiting your turn
Dependency (1,251 jobs)
Job has a dependency on another job (using --dependency flag)
Waiting for another job to complete before this one can start
Common in job chains or workflows
ReqNodeNotAvail, UnavailableNodes (743+ jobs)
Specific nodes requested by the job are unavailable
Nodes might be DOWN, DRAINED, or allocated to other jobs
Job specified particular nodes with --nodelist or --constraint
JobArrayTaskLimit (26 jobs)
Job array has hit the maximum number of simultaneously running tasks
Controlled by MaxArrayTasksPerJob limit or % limit in job array spec
Example: --array=1-100%10 limits to 10 concurrent tasks
Nodes required for job are DOWN, DRAINED or reserved (10 jobs)
Required compute nodes are unavailable due to:
DOWN: Node is not responding/broken
DRAINED: Admin is preventing new jobs (maintenance)
Reserved: Nodes reserved for higher priority partition jobs
Resources (5 jobs)
Insufficient resources available (CPU, memory, GPUs, etc.)
System doesn't have enough free resources to satisfy job requirements
PartitionConfig (3 jobs)
Job configuration doesn't match partition limits
May exceed partition's MaxTime, MaxNodes, or other constraints
ReqNodeNotAvail, May be reserved for other job (5 jobs)
Nodes are being held/reserved for backfill of other jobs
SLURM is reserving resources for a larger job coming soon
Reservation (1 job)
Waiting for a specific reservation time window to begin
JobHeldUser (1 job)
Job held by user using scontrol hold <jobid>
Won't run until released with scontrol release <jobid>
BeginTime (1 job)
Job scheduled to start at a specific future time (--begin)
