import argparse
import json
import zipfile
import os
import sys
import pandas
import shutil
from d2l_scraper import *

def parse_args():

    # CLI Argument Parsing Logic
    parser = argparse.ArgumentParser(prog="python3 app.py", description="Pull submissions from D2L for a given course and assignment.")
    
    parser.add_argument("-c", "--course", help="Course identifier in the format ####-### (e.g., 1250-001)", required=True)
    parser.add_argument("-t", "--type", choices=["assignment", "quiz", "classlist", "grades"], help="Course identifier in the format ####-### (e.g., 1250-001)", required=True)
    parser.add_argument("-n", "--name", help="Assignment name (case sensitive)")
    parser.add_argument("-d", "--download_dir", default="$HOME/Downloads", help="Directory to handle file downloads.")
    parser.add_argument("-l", "--classlists_dir", default="classlists", help="Directory with classlist CSVs.")
    parser.add_argument("-f", "--feedback", action='store_true', help="Flag to scrape evaluation feedback")
    parser.add_argument("-g", "--gui", action='store_true', help="Headless by default; Set this flag to get the GUI")
    
    args = parser.parse_args()
    course_num = args.course
    assignment_type = args.type
    assignment_name = args.name
    download_dir = args.download_dir
    classlist_dir = args.classlists_dir
    feedback = args.feedback
    headless = not args.gui

    return (course_num, assignment_type, assignment_name, download_dir, classlist_dir, feedback, headless)

def scrape_submissions(course, assignment, download_dir, headless):
    # Scraper Logic            
    scraper = SubmissionScraper(course, assignment, download_dir, headless)
    scraper.login(os.getenv("EMAIL"), os.getenv("PASS"))
    scraper.get_submissions()
    scraper.quit()

def scrape_feedback(course, assignment, download_dir, headless):
    # Scraper Logic
    scraper = SubmissionScraper(course, assignment, download_dir, headless)
    scraper.login(os.getenv("EMAIL"), os.getenv("PASS"))
    scraper.get_feedback_file()
    scraper.quit()

def scrape_classlist(course, download_dir, headless):
    # Scraper Logic            
    scraper = ClasslistScraper(course, download_dir, headless)
    scraper.login(os.getenv("EMAIL"), os.getenv("PASS"))
    scraper.get_classlist()
    scraper.quit()

def scrape_quiz(course, quiz_name, download_dir, headless):
    # Scraper Logic            
    scraper = QuizScraper(course, quiz_name, download_dir, headless)
    scraper.login(os.getenv("EMAIL"), os.getenv("PASS"))
    scraper.get_quiz()
    scraper.quit()

def scrape_grades(course, download_dir, headless):
    # Scraper Logic            
    scraper = GradeScraper(course, download_dir, headless)
    scraper.login(os.getenv("EMAIL"), os.getenv("PASS"))
    scraper.get_grades()
    scraper.quit()


def unzip(directory):
    # Get the newest file in the directory
    list_of_files = [os.path.join(directory, f) for f in os.listdir(directory)]
    list_of_files = [f for f in list_of_files if os.path.isfile(f)]  # Filter out directories
    if not list_of_files:
        raise FileNotFoundError("No files found in the directory.")
    
    zip_file = max(list_of_files, key=os.path.getctime)  # Get the most recently created/modified file
    
    # Unzip if it's a zip file
    if zipfile.is_zipfile(zip_file):
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(directory)
        os.remove(zip_file)
    else:
        print("The file is not a valid zip archive.")

def create_user_dirs(download_dir, user_dict):
    # Create username directories
    for _, user in user_dict.items():
        user_dir = f"{download_dir}/{user['username']}"
        os.mkdir(user_dir)
        with open(f"{user_dir}/user", 'w') as f:
            print(f"{user['first_name']} {user['last_name']}", file=f)

def parse_assignments_to_user_dirs(download_dir, user_dict):
    # Parse assignments into username directories
    for file_name in os.listdir(download_dir):
       file_path = os.path.join(download_dir, file_name)
       if os.path.isfile(file_path):
           for _, user in user_dict.items():
               full_name = f"{user['first_name']} {user['last_name']}"
               if full_name in file_name:
                   dest_dir = os.path.join(download_dir, user['username'])
                   shutil.move(file_path, os.path.join(dest_dir, file_name.split("- ")[3]))


if __name__ == "__main__":
    # Check if the environment variables are set
    if not os.getenv('EMAIL') or not os.getenv('PASS'):
        print("Error: EMAIL or PASS environment variable for D2L login is not set.")
        sys.exit()

    # Parse args
    (course_num, assignment_type, assignment, download_dir, classlist_dir, feedback, headless) = parse_args()


    # Hard code course IDs until we find a way to 
    #  dynamically parse them
    # Nested shadow root is a bitch
    # hrs spent: 2
    with open('course_ids.json') as file:
        COURSES = json.load(file)

    course_id = COURSES[course_num]

    # Run scraping function
    if assignment_type == "assignment":
        if feedback:
            scrape_feedback(course_id, assignment, download_dir, headless)
        else:
            scrape_submissions(course_id, assignment, download_dir, headless)
    elif assignment_type == "classlist":
        scrape_classlist(course_id, download_dir, headless)
    elif assignment_type == "quiz":
        scrape_quiz(course_id, assignment, download_dir, headless)
    elif assignment_type == "grades":
        scrape_grades(course, download_dir, headless)

    # Unzip D2L payload
    unzip(download_dir)
    
    # Get rid of index.html; damn you D2L
    os.remove(f'{download_dir}/index.html')

    # Parse classlist
    csv_path = f"{classlist_dir}/csci-{course_num.split('-')[0]}.csv"
    df = pandas.read_csv(csv_path, header=None, names=['username', 'last_name', 'first_name'])
    user_dict = df.to_dict(orient='index')

    # Create directories for each user
    create_user_dirs(download_dir, user_dict)
    
    # Parse the assignments into their respective user directory
    parse_assignments_to_user_dirs(download_dir, user_dict)
