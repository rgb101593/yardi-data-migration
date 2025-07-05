import sys
from src.orchestration import execute_dm3_phase

def main():
    print("="*70)
    print("YARDI PRODUCTION MIGRATION - DM3 GO-LIVE")
    print("="*70)
    print("WARNING: This operation will modify PRODUCTION systems!")
    print("         Ensure you have proper authorization and backups!\n")
    
    # Safety confirmation
    confirmation = input("Type 'PROD' to confirm production migration: ")
    if confirmation != "PROD":
        print("\nProduction migration aborted!")
        sys.exit(0)
    
    # Second confirmation
    print("\nThis is your final warning. This operation:")
    print("- Will overwrite production data")
    print("- Cannot be undone without restoring backups")
    print("- May cause system downtime\n")
    
    final_confirmation = input("Type 'CONFIRM' to proceed: ")
    if final_confirmation != "CONFIRM":
        print("\nProduction migration cancelled!")
        sys.exit(0)
    
    # Execute migration
    execute_dm3_phase()

if __name__ == "__main__":
    main()