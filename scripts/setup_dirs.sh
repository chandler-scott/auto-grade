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
            *)
                echo "Unknown parameter: $1"
                exit 1
                ;;
        esac
    done

    # Validate arguments
    if [[ -z "$ASSIGNMENT_DIR" || -z "$CLASSLIST_FILE" ]]; then
        echo "Usage: $0 -a <assignment_dir> -c <classlist_file>"
        exit 1
    fi
}

format_filenames() {
    # Loop through each file in the directory
    for file in "$ASSIGNMENT_DIR"/*; do
        # Extract the base filename from the path
        filename=$(basename "$file")
        newname=$(echo "$filename" | awk -F'- ' '{print $2,$4,$5}')
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
            #echo $file
            [ -d "$file" ] && continue

            if [[ "$file" == *"$first_name $last_name"* ]]; then
                new_file=$(basename "$file" | sed -E "s/$first_name $last_name \s*//" | tr -d '[:space:]')
                mv "$file" "$ASSIGNMENT_DIR/$username/$new_file"
            fi

        done

        echo "DEBUG: $username $ASSIGNMENT_DIR"

        for file in "$ASSIGNMENT_DIR/$username/"*.zip; do
            echo $file
            cd "$ASSIGNMENT_DIR/$username"
            pwd
            unzip "$file"
            rm "$file"
            cd -
        done

    done < $CLASSLIST_FILE
}

main() {
    # Parse arguments
    parse_args "$@"
    echo -e "Assignment Directory: $ASSIGNMENT_DIR"
    echo -e "Classlist File: $CLASSLIST_FILE"
   
    cd "$ASSIGNMENT_DIR"

    find "$ASSIGNMENT_DIR" -name "*.zip" -exec unzip {} \; -exec rm {} \;

    # Remove D2L index.html
    index_file="$ASSIGNMENT_DIR/index.html"
    if [[ -f $index_file ]]; then
        rm $index_file
    fi

    # Format file names
    format_filenames 
    
    # Associate file names with usernames
    setup_student_dirs
}   

main "$@"
