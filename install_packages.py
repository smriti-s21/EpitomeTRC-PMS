import sys
import subprocess
import os

def install_packages():
    print("Installing required packages...")
    try:
        # Use pip to install pandas and openpyxl
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pandas', 'openpyxl'])
        print("Successfully installed pandas and openpyxl!")
        return True
    except Exception as e:
        print(f"Error installing packages: {str(e)}")
        return False

if __name__ == "__main__":
    success = install_packages()
    if success:
        print("Installation successful. You can now run the application.")
    else:
        print("Installation failed. Please try to install manually using:")
        print("pip install pandas openpyxl")