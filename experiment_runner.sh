#!/bin/bash

#----------------------------Functions-----------------

#Filter 
#only grep necessary information
function filter {
    cat $1 | grep 'Time\|GCLOCK\|Overflows' >> $2
}

#run nclients contention repetition dest
function run {
    echo
    echo "INFO: configurations for this batch of runs:"
    echo "INFO: nclients-$1 contention-"$2" repetition-$3 dest-$4"

    #arguments for contention
    low_contension='-n4 -q60 -u90 -r16384 -t4096'
    high_contension='-n8 -q10 -u80 -r65536 -t4194304'

    contention=$low_contension
    if [ "$2" == "high" ]; then
        echo "INFO: contention setting: $high_contension" 
        contention=$high_contension 
    elif [ "$2" == "low" ]; then
        echo "INFO: contention setting: $low_contension" 
        contention=$low_contension 
    fi

    echo
    i=0
    touch $4
    while [ $i -lt $3 ]; do
        echo "INFO: run $i with command: "
        echo "INFO: $5/vacation -c$1 $contention"
        echo "INFO: run starts at `date`"
        start_time=`date +%s`
        $5/vacation -c$1 `echo $contention` >> $4
        end_time=`date +%s`
        #filter tmp $4 #only grep necessary information
        echo "INFO: run takes $(($end_time - $start_time)) seconds."
        echo
        #rm -f tmp
        i=$(( i+1 ))
    done
}

#experiment version dest_dir
function experiment {
    #set up application
    echo "INFO: set up application"
    application_path=../vacation-boost
    if [ "$1" == "boost" ]; then
        application_path=../vacation-boost
    elif [ "$1" == "default" ]; then
        application_path=../vacation-tl2
    else
        echo "ERRO: WRONG VERSION"
        exit
    fi

    #variables
    echo "INFO: set up variables"
    max_client=32
    rep=40

    #run experiment
    echo "INFO: experiment is running."
    echo "INFO: version-$1 dest_dir-$2"
    nclient=1
    while [ $nclient -le $max_client ]; do
        echo "INFO: Run with $nclient clients"
        echo "INFO: set up destination file for current run"

        dest_file=$2/output_$1_low_$nclient
        run $nclient low $rep $dest_file $application_path
        dest_file=$2/output_$1_high_$nclient
        run $nclient high $rep $dest_file $application_path
        nclient=$(( nclient*2 ))
    done
}


#------------------test run----------------------



#-----------------------------Environment Setup---------------
#Test environment configuration
#create test directory
echo "INFO: setup experiment environment."
output_dir="output"
if [ -f $output_dir ]; then
    echo "INFO: output direcoty exists as file, it will be removed."
    rm -f $output_dir
fi

if [ -d $output_dir ]; then
    echo "INFO: output directory exists."
else
    echo "INFO: create output directory."
    mkdir $output_dir
fi

#create directory to hold this run's experiment data
time_stamp=`date -d 'today' "+%s"`
current_output_dir=$output_dir/output_$time_stamp
mkdir $current_output_dir

#output the hashtable configuration
echo "hashtable configuration: size = $2" > $current_output_dir/hashtable_info
#run by version
version="default"
if [ "$1" == "boost" ]; then
    echo "INFO: experiment version-$1"
    experiment boost $current_output_dir
elif [ "$1" == "default" ]; then
    echo "INFO: experiment version-$1"
    experiment default $current_output_dir
elif [ "$1" == "all" ]; then
    echo "INFO: experiment version-$1"
    echo "INFO: both versions will run"
    experiment default $current_output_dir
    experiment boost $current_output_dir
else
    echo "ERRO: wrong argument. Usage: ./run_test [ default|boost|all ]"
fi

cp -r $current_output_dir experiment/
echo "INFO: experiment completes."
exit

