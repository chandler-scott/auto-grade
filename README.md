# Auto Grading Tool
A command-line interface tool using Selenium to scrape D2L.

## Setup
1. Create virtual environment
  ```
  python -m venv .venv --prompt auto-grade
  ```
2. Activate .venv
  ```
  source ./.venv/bin/activate
  ```
3. Install dependencies
  ```
  python3 -m pip install -r requirements.txt
  ```
4. Set Environmental Variables for Login
  ```
  export EMAIL=[EMAIL]
  export PASS=[PASS]
  ```

## Using the Tool

- Get classlist
  ```
  python3 app.py -c [course-number] -t [classlist] -d [download-dir] 
  ```

- Get grades (*NOTE: requires a classlist .csv in classlists/*)
  ```
  python3 app.py -c [course-number] -t [grades] -d [download-dir] 
  ```

- Get assignment submissions (*NOTE: requires a classlist .csv in classlists/*)
  ```
  python3 app.py -c [course-number] -t [assignment] -n [name] -d [download-dir] 
  ```
