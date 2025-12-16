# Drug Dictionary Excel Import Tool

## Overview
This tool allows you to import drug data from Excel files into the Drug Dictionary database. The script is designed to work with Excel files that contain drug brand names and manufacturer information.

## Prerequisites
- Python 3.x installed
- Required Python packages:
  - pandas
  - openpyxl

## Installation
The required packages should already be installed from previous work. If needed, install them using:

```bash
pip install pandas openpyxl
```

## Supported Excel File Format
The script expects Excel files with the following column structure:
- **Brand Name** (required) - The brand name of the drug
- **Manufacturer** (required) - The manufacturer/company name

Example:
| Brand Name | Manufacturer |
|------------|--------------|
| Lipitor    | Pfizer       |
| Amoxil     | AstraZeneca  |
| Crocin     | GlaxoSmithKline |

## Usage

### Basic Usage
Navigate to the utils directory and run the script with the path to your Excel file:

```bash
cd e:\GITHUB\DrugDictionaryApp\utils
python import_drugs_from_excel.py path/to/your/excel/file.xlsx
```

### Example Commands
```bash
# Import Book2.xlsx
python import_drugs_from_excel.py ../Book2.xlsx

# Import from a different directory
python import_drugs_from_excel.py C:\data\medicines.xlsx
```

## Features
- Validates Excel file format and required columns
- Provides detailed progress reporting
- Shows import statistics (successful imports, errors, etc.)
- Handles database connections automatically
- Preserves existing database records
- Adds new records without duplicating existing ones

## Error Handling
The script includes error handling for:
- Missing files
- Incorrect file formats
- Missing required columns
- Database connection issues
- Individual row import errors

## Output
The script provides detailed output including:
- File information (number of rows, columns)
- Progress indicators (every 100 records)
- Final import summary with statistics
- Success/error indicators

## Best Practices
1. Always backup your database before importing new data
2. Verify your Excel file format before importing
3. Check the import summary to ensure all records were imported correctly
4. Test with a small sample file first if you're unsure about the format

## Troubleshooting
### Common Issues
1. **File not found error**: Check the file path is correct
2. **Missing columns error**: Ensure your Excel file has "Brand Name" and "Manufacturer" columns
3. **Database connection error**: Verify the database file exists in the expected location

### Getting Help
If you encounter issues, check:
1. The console output for specific error messages
2. That your Excel file follows the expected format
3. That you have proper file permissions

## Customization
You can modify the script to:
- Support additional columns
- Change the import frequency
- Add data validation
- Modify the progress reporting

## Version History
- v1.0: Initial release with basic import functionality

## Author
Generated for Drug Dictionary Application

## License
This tool is provided as part of the Drug Dictionary application and is intended for internal use only.