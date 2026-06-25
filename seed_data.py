import os
import django
import pandas as pd
from datetime import datetime
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.utils import timezone
from doctors.models import Remake


def clean_string(value, default=''):
    if pd.isna(value):
        return default
    text = str(value).strip()
    return text if text else default


def optional_string(value):
    if pd.isna(value):
        return None
    text = str(value).strip()
    return text if text else None


def clean_int(value, default=0):
    if pd.isna(value):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def clean_bool(value):
    if pd.isna(value):
        return False
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    return text in ('true', '1', 'yes', 'y', 't')


def parse_month_to_date(month_value):
    month_string = clean_string(month_value, '202501')
    if len(month_string) == 6 and month_string.isdigit():
        year = int(month_string[:4])
        month = int(month_string[4:])
        try:
            return timezone.make_aware(datetime(year, month, 1), timezone.get_current_timezone())
        except Exception:
            return timezone.now()
    return timezone.now()


def seed_from_excel():
    desktop_path = Path.home() / 'Desktop'
    excel_file_path = desktop_path / 'Remake Analysis - TTM.xlsx'

    if not excel_file_path.exists():
        print(f'File not found at {excel_file_path}')
        return

    print('Reading Excel...')
    try:
        df = pd.read_excel(excel_file_path, sheet_name='DATA')
    except Exception as error:
        print(f'ERROR reading Excel file: {error}')
        return

    print(f'Processing {len(df)} rows from DATA sheet...')

    

    remakes_to_create = []
    successful_imports = 0
    failed_imports = 0
    batch_size = 5000
    max_rows_to_import = None  # Set to a number for testing, or None for all rows

    if max_rows_to_import is not None:
        df = df.head(max_rows_to_import)
        print(f'Limiting import to first {max_rows_to_import} rows for testing.')

    for index, row in df.iterrows():
        month_value = clean_string(row.get('Month', '202501'))
        case_number = clean_string(row.get('CaseNumber', ''))
        doctor_name = clean_string(row.get('DoctorName', 'Unknown'))
        department = clean_string(row.get('Department', 'General'))
        production_lab = clean_string(row.get('ProductionLab', 'Unknown'))

        if not case_number or not doctor_name:
            print(f'Skipping row {index + 2}: missing case number or doctor name')
            failed_imports += 1
            continue

        date_entered = parse_month_to_date(month_value)

        remake_record = Remake(
            month=month_value,
            case_number=case_number,
            doctor_name=doctor_name,
            department=department,
            production_lab=production_lab,
            mill_used=optional_string(row.get('MillUsed')),
            milling_technician=optional_string(row.get('MillingTechnician')),
            design_location=optional_string(row.get('DesignLocation')),
            units=clean_int(row.get('Units', 0)),
            product_id=optional_string(row.get('ProductID')),
            invoice_description=optional_string(row.get('InvoiceDescription')),
            original_case_number=optional_string(row.get('OriginalCaseNumber')),
            original_month=optional_string(row.get('OriginalMonth')),
            original_production_lab=optional_string(row.get('OriginalProductionLab')),
            remake_reason=optional_string(row.get('RemakeReason')),
            charge_doctor=clean_bool(row.get('ChargeDoctor', False)),
            remake_units=clean_int(row.get('RemakeUnits', 0)),
            adjustment_units=clean_int(row.get('AdjustmentUnits', 0)),
            lab_discount=float(row.get('LabDiscount', 0.0) or 0.0),
            lab_discount_units=clean_int(row.get('LabDiscountUnits', 0)),
            date_entered=date_entered,
        )

        remakes_to_create.append(remake_record)
        successful_imports += 1

        if len(remakes_to_create) >= batch_size:
            Remake.objects.bulk_create(remakes_to_create)
            print(f'Saved {len(remakes_to_create)} records...')
            remakes_to_create = []

    if remakes_to_create:
        Remake.objects.bulk_create(remakes_to_create)
        print(f'Saved remaining {len(remakes_to_create)} records...')

    print('Done!')
    print(f'Successfully imported: {successful_imports}')
    print(f'Failed rows: {failed_imports}')


if __name__ == '__main__':
    seed_from_excel()
