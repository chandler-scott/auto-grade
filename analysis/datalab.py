import re
import pandas as pd


class PuzzleData:
    def __init__(self, puzzle_name):
        self.puzzle_name = puzzle_name
        self.correctness_data = []
        self.rating_data = []
        self.errors_data = []
        self.perf_data = []
        self.ops_data = []


def extract_table_from_file(filename):
    with open(filename, 'r') as f:
        content = f.read()

    # Regular expression to capture the table
    table_pattern = re.search(r"Correctness Results\s+Perf Results\n(.*?)\nScore =", content, re.DOTALL)


    if not table_pattern:
        print("No table found in", filename)
        return None

    table_text = table_pattern[0].split("\n")[1:-1]  # Remove "Score =" line
    headers = table_text[0].split()  # Extract headers
    headers[0] = "CorrectnessPoints" # Manually set correctness vs performance points
    headers[3] = "PerformancePoints" # Manually set correctness vs performance points
    data_lines = table_text[1:]  # Extract data rows

    # Convert into a DataFrame
    data = [re.split(r'\s+', line.strip()) for line in data_lines if line.strip()]
    df = pd.DataFrame(data, columns=headers)

    # Convert numeric columns
    numeric_cols = ["CorrectnessPoints", "Rating", "Errors", "PerformancePoints", "Ops"]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric)

    return df

# Example usage
df = extract_table_from_file("/tmp/d2l-pull/gunjc1/out")

if df is not None:
    puzzle_list = []
    for puzzle in df["Puzzle"].values:
        puzzle_data = PuzzleData(puzzle)
        puzzle_data.correctness_data.append(df.loc[df["Puzzle"] == puzzle, "CorrectnessPoints"].values[0])
        puzzle_data.rating_data.append(df.loc[df["Puzzle"] == puzzle, "Rating"].values[0])
        puzzle_data.errors_data.append(df.loc[df["Puzzle"] == puzzle, "Errors"].values[0])
        puzzle_data.perf_data.append(df.loc[df["Puzzle"] == puzzle, "PerformancePoints"].values[0])
        puzzle_data.ops_data.append(df.loc[df["Puzzle"] == puzzle, "Ops"].values[0])

        print(f'{puzzle}')
        print(f'C: {puzzle_data.correctness_data}')
        print(f'R: {puzzle_data.rating_data}')
        print(f'E: {puzzle_data.errors_data}')
        print(f'P: {puzzle_data.perf_data}')
        print(f'O: {puzzle_data.ops_data}')
    
