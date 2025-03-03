#!/bin/bash

# Description: Script to grade the Bomb Lab for CSCI-3160 
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
            -o|--output)
                OUTPUT_FILE="$2"
                shift 2
                ;;
            *)
                echo "Unknown parameter: $1"
                exit 1
                ;;
        esac
    done

    # Validate arguments
    if [[ -z "$ASSIGNMENT_DIR" || -z "$OUTPUT_FILE" ]]; then
        echo "Usage: $0 -a <assignment_dir> -o <output_file>"
        exit 1
    fi
}

grade_students() {
    touch "$OUTPUT_FILE"
    rm $OUTPUT_FILE

    for user_dir in "$ASSIGNMENT_DIR"/*; do
        defuse="$user_dir/defuse.txt"
        bomb="$user_dir/bomb"
        user_grade="$user_dir/grade"
        out="$user_dir/out"
        class_grade="$OUTPUT_FILE"
        user=$(basename "$user_dir")

        echo -e "  > INFO: $user" 

        if [[ ! -f "$defuse" ]]; then
            echo 0 > $user_grade
            echo "$user,0" >> $class_grade
            echo -e "  > INFO: grade:\t0\n" 
            continue
        fi

        # Purge blank lines
        dos2unix $defuse
        sed -i '/^$/d' "$defuse"

        # Get number of defuses
        defuses=$(wc -l < "$defuse")

        # Run with defuse.txt to check if all are correct
        timeout 0.5s stdbuf -o0 bash -c "$bomb $defuse > $out"

        # Validate
        phrases=(
            "Phase 1 defused. How about the next one?"
            "That's number 2.  Keep going!"
            "Halfway there!"
            "So you got that one.  Try this one."
            "Good work!  On to the next..."
            "Curses, you've found the secret phase!"
            "But finding it and solving it are quite different..."
            "Wow! You've defused the secret stage!"
            "Congratulations! You've defused the bomb!"
        )
        
        count=0
        output=$(cat "$out")
        
        for phrase in "${phrases[@]}"; do
            if [[ "$output" =~ $phrase ]]; then
                ((count++))
            fi
        done

        [[ $count == 9 ]] && count=7
        echo "$user,$count" >> $class_grade
        echo $count > $user_grade

        echo -e "  > INFO: phrases:\t$defuses" 
        echo -e "  > INFO: grade:\t$count\n" 
    done
}

main() {
    # Parse arguments
    parse_args "$@"
    echo -e "Assignment Directory: $ASSIGNMENT_DIR"
    echo -e "Grade Output File: $OUTPUT_FILE"
   
    # Grade student and write grade to file
    grade_students

    # Finished!
    echo -e "\nBomb Lab grading finished."
}   

main "$@"
