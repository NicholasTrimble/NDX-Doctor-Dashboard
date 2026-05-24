import pandas as pd
from pathlib import Path

def inspect_excel_file():
    """
    Utility script to inspect your Excel file and show column names.
    Run this to see what columns are available in your Excel file.
    """

    # Path to your desktop
    desktop_path = Path.home() / "Desktop"
    excel_file_path = desktop_path / "Remake Analysis - TTM.xlsx"

    if not excel_file_path.exists():
        print(f"ERROR: Excel file not found at {excel_file_path}")
        print("Please make sure 'Remake Analysis - TTM.xlsx' is on your desktop.")
        return

    print(f"Reading Excel file from: {excel_file_path}")
    print("=" * 60)

    try:
        # First, let's see what sheets are available
        excel_file = pd.ExcelFile(excel_file_path)
        available_sheets = excel_file.sheet_names
        print(f"Available sheets in Excel file: {available_sheets}")
        print()

        # Ask user which sheet to inspect
        if len(available_sheets) > 1:
            print("Multiple sheets found. Inspecting the first sheet by default.")
            print("You can change this in seed_data.py by modifying sheet_name parameter.")
            print()

        # Read the first sheet (or you can specify a different one)
        sheet_name = available_sheets[0]  # First sheet
        print(f"Inspecting sheet: '{sheet_name}'")
        print("=" * 40)

        excel_data = pd.read_excel(excel_file_path, sheet_name=sheet_name)

        print(f"Found {len(excel_data)} rows of data")
        print(f"Found {len(excel_data.columns)} columns")
        print("\nCOLUMN NAMES:")
        print("=" * 30)

        for i, col in enumerate(excel_data.columns, 1):
            print("2d")

        print("\n" + "=" * 60)
        print("SAMPLE DATA (first 10 rows):")
        print("=" * 30)
        # Show more rows to better understand the data structure
        print(excel_data.head(10))

        print("\n" + "=" * 60)
        print("DATA TYPES:")
        print("=" * 12)
        print(excel_data.dtypes)

        print("\n" + "=" * 60)
        print("INSTRUCTIONS:")
        print("=" * 12)
        print("1. Copy the column names above")
        print("2. Open seed_data.py")
        print("3. Find the 'EXCEL COLUMN MAPPING' section")
        print("4. Replace the example column names with your actual column names")
        print("5. If data is on a different sheet, change sheet_name in seed_data.py")
        print("6. Run: python seed_data.py")

        # Check if this looks like actual case data or summary data
        if len(excel_data.columns) <= 2 and 'Unnamed' in str(excel_data.columns[0]):
            print("\n" + "!" * 60)
            print("WARNING: This sheet appears to be a summary or filter sheet,")
            print("not raw case data. You may need to:")
            print("1. Choose a different sheet (see available sheets above)")
            print("2. Or export your raw data to a new sheet")
            print("!" * 60)

    except Exception as e:
        print(f"ERROR reading Excel file: {e}")

if __name__ == '__main__':
    inspect_excel_file()