#!/bin/sh

for i in $(seq 0 1 77)
do
   echo $i
   bsub -W 48:00 -n 4 -R rusage[mem=4096] mpirun python covid19nepal.py -nodeinfect $i &
   sleep 2
done

wait
