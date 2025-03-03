#!/bin/bash

# Description: Script to grade the Data Lab for CSCI-3160 
# Author: Chandler Scott (scottcd1@etsu.edu)
# Date: 02/07/25 
# License: GNU General Public License v3.0

parse_args() {
    while [[ "$#" -gt 0 ]]; do
        case "$1" in
            -a|--assignment)
                ASSIGNMENT_DIR="$2"
                shift 2
                ;;
            -c|--classlist)
                CLASSLIST_FILE="$2"
                shift 2
                ;;
            -d|--datalab)
                DATALAB_DIR="$2"
                shift 2
                ;;
            *)
                echo "Unknown parameter: $1"
                exit 1
                ;;
        esac
    done

    # Validate arguments
    if [[ -z "$ASSIGNMENT_DIR" || -z "$CLASSLIST_FILE" || -z "$DATALAB_DIR" ]]; then
        echo "Usage: $0 -a <assignment_dir> -c <classlist_file> -d <datalab_dir>"
        echo $DATALAB_DIR
        exit 1
    fi
}

format_filenames() {
    # Loop through each file in the directory
    for file in "$ASSIGNMENT_DIR"/*; do
        # Extract the base filename from the path
        filename=$(basename "$file")
        newname=$(echo "$filename" | awk -F'- ' '{print $2,$4,$45}')
        # Rename to 'Fistname Last Name FileName'
        mv "$ASSIGNMENT_DIR/$filename" "$ASSIGNMENT_DIR/$newname"
    done
}

setup_student_dirs() {
    while IFS=',' read -r username last_name first_name; do
        username=$(echo "$username" | xargs)
        last_name=$(echo "$last_name" | xargs)
        first_name=$(echo "$first_name" | tr -d '\r' | xargs)

        mkdir -p "$ASSIGNMENT_DIR/$username"
        for file in "$ASSIGNMENT_DIR"/*; do
            [ -d "$file" ] && continue

            if [[ "$file" == *"$first_name $last_name"* ]]; then
                if [[ "$file" == *.c || "$file" == *.c\  ]]; then
                     mv "$file" "$ASSIGNMENT_DIR/$username/bits.c"
                else
                    mv "$file" "$ASSIGNMENT_DIR/$username"
                fi
            fi

        done

    done < $CLASSLIST_FILE
}

grade_students() {
    find "$ASSIGNMENT_DIR" -mindepth 1 -type d -exec sh -c '
        user=$(basename "$1")
        # Copy bits.c, and exit if it fails
        cp "$1/bits.c" "$2" 2>/dev/null || { printf "%-15s %-20s\n" "$user" "FILE NOT PRESENT"; echo 0 > $1/grade; echo "$user,0,F" >> grades.csv; echo "FILE NOT PRESENT" > $1/error; exit 1; } && 
   
        # Change to the target directory
        cd "$2" && 

        # Run the driver.pl grading script
        ./driver.pl "$1/bits.c" 2>$1/error > "$1/out" || { printf "%-15s %-20s\n" "$user" "DID NOT COMPILE"; cd - >/dev/null; echo 0 > $1/grade; echo "$user,0,C" >> grades.csv ; echo "DID NOT COMPILE" >> $1/error; exit 1; } &&

        # Parse their grade to a file
        printf "%-15s %-20s\n" "$user" "SUCCESSFULLY GRADED"
        grade=$(tail -n 1 "$1/out" | awk "{ print \$3 }" | cut -d"/" -f1)
        echo $grade > $1/grade
        cd - >/dev/null
        echo $user,$grade,S >> grades.csv
        ' _ {} "$DATALAB_DIR" \; 
        cat grades.csv | sort > tmp && cat tmp > grades.csv && rm tmp
}

main() {
    # Parse arguments
    parse_args "$@"
    echo -e "Assignment Directory: $ASSIGNMENT_DIR"
    echo -e "Classlist File: $CLASSLIST_FILE"
    echo -e "Data Lab Directory: $DATALAB_DIR\n"
   
    # Remove D2L index.html
    index_file="$ASSIGNMENT_DIR/index.html"
    if [[ -f $index_file ]]; then
        rm $index_file
    fi



    # Format file names
    #format_filenames 
    
    # Associate file names with usernames
    #setup_student_dirs
    

    # Unzip, Untar, Unrar
    for dir in "$ASSIGNMENT_DIR"/*; do
        # Find compressed files and uncompress them
        find "$dir" -type f -regex ".*\.\(tar\|rar\|zip\).*" -exec 7z e {} -o"$dir" bits.c -r -y \; 

        # Get rid of directories uncompressed; we only want bits.c and reports.
        find "$dir" -mindepth 1 -type d -exec rm -rf {} \;
    done

    #   Grade student and write grade to file
    grade_students

    # Finished!
    echo -e "\nData Lab grading finished."
}   

main "$@"
