import subprocess

def run_script(script_name):
    try:
        subprocess.run(['python3', script_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running {script_name}: {e}")

#demo coordinates (Brighton Ski Resort, specifically Wrens Hollow)
lat = 40.58727
lon = -111.58180

def main():
    run_script('api.py')
    run_script('7.py')
    run_script('combine.py')
    run_script('output.py')

if __name__ == '__main__':
    main()