# scripts/get_appointments.py
# Run `python get_appointments.py --begin_date <date> --end_date <date>` from the root directory of the project

import os
import logging
import argparse
import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from navigate_connector import NavigateAPI


# Define the directory for logging relative to the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(script_dir, os.pardir, 'logs')
log_file_path = os.path.join(log_dir, 'appointments.log')
full_log_path = os.path.abspath(log_file_path)

# Ensure the directory exists
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Check if the log file exists, and if not, create it
if not os.path.isfile(full_log_path):
    open(full_log_path, 'a').close()

# Set up logging to write to a file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(full_log_path)]
)

def extract_appointment_data(appointments):
    # Prepare a list to hold extracted data
    extracted_data = []

    for appointment in appointments:
        # Extract required fields
        appointment_id = appointment.get('id')
        location = appointment.get('location')
        organizer_primary_id = appointment.get('organizer', {}).get('primary_id')
        appointment_type = appointment.get('type')
        start_time = appointment.get('start_time')
        scheduled_student_services = appointment.get('scheduled_student_services')
        is_no_show = appointment.get('is_no_show')
        is_cancelled = appointment.get('is_cancelled')

        # Extract attendee IDs; ensure it's a list even if one or none
        attendees = appointment.get('attendees', [])
        attendees_primary_ids = [attendee.get('primary_id') for attendee in attendees if 'primary_id' in attendee]

        # Append to the list
        extracted_data.append({
            'appointment_id': appointment_id,
            'location': location,
            'organizer_primary_id': organizer_primary_id,
            'appointment_type': appointment_type,
            'start_time': start_time,
            'scheduled_student_services': scheduled_student_services,
            'is_no_show': is_no_show,
            'is_cancelled': is_cancelled,
            'attendees_primary_ids': ','.join(attendees_primary_ids)  # Join the IDs into a single string
        })

    return extracted_data

def export_to_csv(data, start_date, end_date, save_dir='data/appointments'):

    # Convert dates from mm/dd/yyyy to mm_dd_yyyy format for filename
    safe_start_date = start_date.replace('/', '_')
    safe_end_date = end_date.replace('/', '_')

    # Convert data to a DataFrame
    df = pd.DataFrame(data)

    # Check if the directory exists, if not, create it
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Define the full file path
    filename = f"apmts_{safe_start_date}_{safe_end_date}.csv"
    full_file_path = os.path.join(save_dir, filename)

    # Export to CSV
    df.to_csv(full_file_path, index=False)
    logging.info(f"Data exported to {full_file_path}")

def get_and_export_appointments_for_date(connector, start_date, end_date):
    try:
        logging.info(f"Starting API call for appointments from {start_date} to {end_date}")
        
        # Download appointments for the given date range
        response = connector.get_appointments(begin_date=start_date, end_date=end_date)
        
        if response:
            logging.info(f"API call successful for appointments from {start_date} to {end_date}")

            # Extract data
            extracted_data = extract_appointment_data(response)

            if extracted_data:
                # Export to CSV
                export_to_csv(extracted_data, start_date, end_date)
            else:
                logging.info(f"No appointments found for the date range from {start_date} to {end_date}. No CSV file created.")
        else:
            logging.info(f"API returned an empty list for the date range from {start_date} to {end_date}. No CSV file created.")

    except Exception as e:
        logging.error(f"Error during API call for the date range from {start_date} to {end_date}: {e}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Download appointments data from Navigate")
    parser.add_argument("--begin_date", required=True, help="Begin date in mm/dd/yyyy format")
    parser.add_argument("--end_date", required=True, help="End date in mm/dd/yyyy format")
    args = parser.parse_args()

    # Mark the start of the script run
    print("Script running. See logs at /logs/appointments.log for details.")

    # Convert string dates to datetime objects
    start_date = datetime.strptime(args.begin_date, "%m/%d/%Y")
    end_date = datetime.strptime(args.end_date, "%m/%d/%Y")

    # Create an instance of the NavigateAPI
    connector = NavigateAPI()

    # Define the maximum number of threads to use
    max_threads = 50

    # Use ThreadPoolExecutor to limit the number of concurrent threads
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = []
        # Loop over each day in the date range
        while start_date < end_date:
            # Define the range for each day
            day_end = start_date + timedelta(days=1)

            # Format dates into strings for the API call
            str_start_date = start_date.strftime("%m/%d/%Y")
            str_end_date = day_end.strftime("%m/%d/%Y")

            # Submit the function to the executor
            future = executor.submit(get_and_export_appointments_for_date, connector, str_start_date, str_end_date)
            futures.append(future)

            # Move to the next day
            start_date = day_end

        # Wait for all futures to complete
        for future in as_completed(futures):
            try:
                # Result is None for this script, but if you have a result, you can process it here
                result = future.result()
            except Exception as exc:
                # Log the exception if any occurred
                logging.error(f"Generated an exception: {exc}")

    logging.info("All data exported.")

if __name__ == "__main__":
    main()
