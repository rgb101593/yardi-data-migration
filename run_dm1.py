# run_dm1.py - MAIN ENTRY POINT
from src.orchestration import execute_dm1_phase

if __name__ == "__main__":
    print("Starting Yardi DM1 Migration...")
    execute_dm1_phase()
    print("Process completed! Check /data/reports for results")