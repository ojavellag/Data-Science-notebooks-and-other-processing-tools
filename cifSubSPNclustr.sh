#!/bin/bash


# the next line needs to be sourced first outside the script
# . /projects/ojavellag/TrainData/ColinExpSPINS/Bash_run/CiftyColin.sh

instruct1="ciftify_subject_fmri  --SmoothingFWHM 8 --DilateBelowPct 4 $1 $2 $3"
echo "running ....... $instruct1" >> /path/to/logs/run_out.txt
$instruct1
instruct2="cifti_vis_fmri snaps $3 $2"
echo "running ....... $instruct2" >> /path/to/logs/run_out.txt
$instruct2
