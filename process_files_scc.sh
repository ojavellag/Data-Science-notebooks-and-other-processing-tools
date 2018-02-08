#!bin/bash

fmri_dir="/path/to/fmri_dataS/"
hcp_dir="/path/to/HCP_dataS/"
log_dir="/path/to/logs/"
comm_path="/path/to/Bash_run/"

declare -a task_arr=( "imob" "rest" "ea" )

declare -a imob_elems=("imitate_scaled" "observe_scaled")
declare -a rest_elems=("rest_filtered")
declare -a ea_elems=("EA_task1_scaled" "EA_task2_scaled" "EA_task3_scaled" )

cd ${hcp_dir}
#Here it looks only for the subjects that make sense excluding phantoms
declare -a subj_arr=( $(ls |grep "SPN" |grep -v "..._P") )

#this loop iterates over all subjects
for((i=0;i<${#subj_arr[@]};i++))
do
  subject="${subj_arr[$i]}"

  #"task being run"
  for((j=0;j<${#task_arr[@]};j++))
  do
#full path to all the files of interest i.e those with the string "scaled" in its name
    task_path="${fmri_dir}${task_arr[$j]}/$subject/"
    #  now, go to that path and search for files
    cd $task_path
    #if they exist file-names are captured in this array
     input_files=($(ls |grep "scaled"))

     if [ ${#input_files[@]} -gt 0 ]
     then
       for((k=0;k<${#input_files[@]};k++))
       do
         InputFile=$task_path${input_files[$k]}
         if [ $j -eq 0 ]
         then
           outName=${imob_elems[$k]}
         elif [ $j -eq 1 ]
         then
           outName=${rest_elems[$k]}
         elif [ $j -eq 2 ]
         then
           outName=${ea_elems[$k]}
         fi
         $(bash /path/to/cifSubSPN.sh $InputFile $subject $outName)
         echo "file $InputFile done ......." >> "$log_dir/logDone.txt"
       done
     else
        echo "scaled file missing in $task_path " >> "$log_dir/logFail.txt"
       continue
     fi
  done
done

# example commands
# qsub ciftify_subject_fmri --DilateBelowPct 4 \
# /home/ojavellag/Desktop/remote_home/TrainData/ColinExpSPINS/fmri_dataS/imob/\
# SPN01_CMH_0101_01/SPN01_CMH_0101_01_01_IMI_09_AxEPI-ImitateTask_scaled.nii.gz \
# SPN01_CMH_0101_01 Imitate_scaled
# cifti_vis_fmri snaps Imitate_scaled SPN01_CMH_0101_01
