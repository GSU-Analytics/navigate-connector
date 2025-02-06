import requests
import pandas as pd
from requests.auth import HTTPBasicAuth
import keyring
import getpass

class NavigateAPI:
    def __init__(self, service_name='NavigateService'):
        self.service_name = service_name
        self.base_url = 'https://gsu.campus.eab.com/api'
        self.username, self.api_key = self.load_credentials()

    def load_credentials(self):
        """
        Loads credentials for the Navigate service from the system's keyring. 
        If credentials are not found, prompts the user to enter them, and then stores them in the keyring.

        The method checks the system's keyring for stored username and API key associated with the Navigate service.
        If not found, the user is prompted to input these details, which are then saved for future use.

        Returns:
            tuple: A tuple containing the username and API key for the Navigate service.
                   The format is (username, api_key).

        Side Effects:
            - If credentials are not found in the keyring, prompts the user to enter their username and API key.
            - Stores new credentials in the system's keyring.

        Examples:
            >>> connector = NavigateAPI()
            Navigate service credentials not found.
            Enter Navigate username: my_username
            Enter Navigate API key: [Hidden]
            Credentials stored successfully.
            >>> connector.username
            'my_username'
            >>> connector.api_key
            'my_api_key'
        """

        # Check if credentials exist in the keyring
        username = keyring.get_password(self.service_name, 'username')
        api_key = keyring.get_password(self.service_name, 'api_key')

        # Prompt for credentials if not found
        if username is None or api_key is None:
            print("Navigate service credentials not found.")
            username = input("Enter Navigate username: ")
            api_key = getpass.getpass("Enter Navigate API key: ")

            # Store the new credentials in the keyring
            keyring.set_password(self.service_name, 'username', username)
            keyring.set_password(self.service_name, 'api_key', api_key)
            print("Credentials stored successfully.")

        return username, api_key
    
    def update_credentials(self):
        """
        Prompts the user to enter new credentials for the Navigate service and stores them in the system's keyring.

        This method is used to update the username and API key for the Navigate service. 
        It prompts the user to input new credentials, which are then saved in the keyring, 
        replacing any existing ones.

        Returns:
            tuple: A tuple containing the new username and API key for the Navigate service.
                   The format is (username, api_key).

        Side Effects:
            - Prompts the user to enter their new username and API key.
            - Updates the stored credentials in the system's keyring.

        Examples:
            >>> connector = NavigateAPI()
            >>> connector.update_credentials()
            Enter new Navigate username: new_username
            Enter new Navigate API key: [Hidden]
            Credentials updated successfully.
            ('new_username', 'new_api_key')

        Note:
            The API key input will be hidden during entry for security reasons.
        """
                
        # Prompt the user for new credentials
        username = input("Enter new Navigate username: ")
        api_key = getpass.getpass("Enter new Navigate API key: ")  # getpass hides the input for security

        # Store the new credentials in the keyring
        keyring.set_password(self.service_name, 'username', username)
        keyring.set_password(self.service_name, 'api_key', api_key)
        print("Credentials updated successfully.")

        return username, api_key

    def get_alerts(self, **kwargs):
        """
        Fetches alert data from the Navigate API based on provided query parameters.

        This method sends a GET request to the Navigate API to retrieve alert data. 
        The user can specify various query parameters to filter the alerts. 
        If no parameters are provided, all alerts are returned. 
        The data is paginated, and pagination parameters can also be passed.

        Args:
            **kwargs: Arbitrary keyword arguments. Allowed parameters include:
                - student_primary_user_id (str): Returns records where the user external_id 
                  for the associated student matches the input. This is the PIDM for GSU users.
                - issued_by_primary_user_id (str): Returns records where the user external_id 
                  for the associated creator matches the input. This is the PIDM for GSU users.
                - alert_reason_external_id (str): Returns records associated with the alert 
                  reason where the external_id matches the input.
                - created_after (str): Returns all alerts created on or after this date.
                - created_before (str): Returns all alerts created on or before this date.
                - page (int): Page number for paginated results. Default is 1.
                - per_page (int): Number of elements to return per page. Default is 100.

        Returns:
            dict: A dictionary containing the JSON response data with alert records.

        Raises:
            RequestException: If an error occurs during the API request.

        Examples:
            >>> connector = NavigateAPI()
            >>> # Fetch first page of alerts
            >>> connector.get_alerts()
            >>> # Fetch alerts for a specific student
            >>> connector.get_alerts(student_primary_user_id='11111')
            >>> # Fetch alerts created after a specific date
            >>> connector.get_alerts(created_after='2022-01-31')
            >>> # Fetch alerts within a specific date range
            >>> connector.get_alerts(created_after='2022-01-01', created_before='2022-04-01')
            >>> # Fetch a specific page of results
            >>> connector.get_alerts(page=2, per_page=50)

        Note:
            The method automatically handles authentication using the stored credentials.
            Ensure that credentials are loaded and valid before making API calls.
        """

        # Ensure the credentials are loaded
        if not self.username or not self.api_key:
            print("Credentials are not loaded. Please load or update credentials.")
            return None

        # Making the API call
        try:
            response = requests.get(
                f'{self.base_url}/v3/alerts',
                params=kwargs,
                auth=HTTPBasicAuth(self.username, self.api_key)
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None
        
    def save_alerts_to_dataframe(self, alerts_response):
        """
        Converts the alerts data from the API response to a pandas DataFrame.

        This method takes the response from the Navigate API containing alerts data and 
        converts it into a pandas DataFrame for easier analysis and manipulation. 
        The method handles nested lists in the 'alert_reasons' and 'enrollments' fields 
        by converting them into comma-separated strings.

        Args:
            alerts_response (dict): The JSON response object from the Navigate API 
                                    which contains the alerts data.

        Returns:
            DataFrame: A pandas DataFrame containing the alerts data. Each row represents 
                       an alert, and columns include 'id', 'comments', 'group', 'issued_for', 
                       'issued_by', 'alert_reasons', and 'enrollments'.
            Note: The 'issued_for' and 'issued_by' fields contain user IDs, which can be found
                  with a `get_user_by_id` call

        Raises:
            ValueError: If the alerts_response is invalid or empty.

        Examples:
            >>> connector = NavigateAPI()
            >>> alerts_response = connector.get_alerts(created_after='2022-01-01')
            >>> alerts_df = connector.save_alerts_to_dataframe(alerts_response)
            >>> print(alerts_df.head())

            # Example output (truncated for brevity):
            #        id                         comments  ...      alert_reasons  enrollments
            # 0  123456  This student has missed several classes  ...  123456, 123457  123456, 123458

        Note:
            If the alerts_response does not contain valid data, an empty DataFrame is returned.
            The DataFrame's structure and content depend on the API response format.
        """

        if not alerts_response or 'data' not in alerts_response or 'alerts' not in alerts_response['data']:
            print("Invalid or empty response data.")
            return pd.DataFrame()  # Return an empty DataFrame

        # Extracting alerts data
        alerts_data = alerts_response['data']['alerts']

        # Creating a DataFrame
        df = pd.DataFrame(alerts_data)

        # Extracting nested lists into separate columns if needed
        df = df.assign(
            alert_reasons=df['alert_reasons'].apply(lambda x: ', '.join(map(str, x))),
            enrollments=df['enrollments'].apply(lambda x: ', '.join(map(str, x)))
        )

        return df

    def get_users(self, **kwargs):
        """
        Fetches user data from the Navigate API based on provided query parameters.

        This method sends a GET request to the Navigate API to retrieve user data. 
        The user can specify various query parameters to filter the user records. 
        If no parameters are provided, all user records are returned. 
        The data is paginated, and pagination parameters can also be passed.

        Args:
            **kwargs: Arbitrary keyword arguments. Allowed parameters include:
                - primary_user_id (str): Returns all records where the primary_user_id of 
                  the user matches the given input. This is the PIDM for GSU users.
                - page (int): Page number for paginated results. Default is 1.
                - per_page (int): The number of elements to be returned from the request, 
                  for paginated results. Default is 100.

        Returns:
            dict: A dictionary containing the JSON response data with user records.

        Raises:
            RequestException: If an error occurs during the API request.

        Examples:
            >>> connector = NavigateAPI()
            >>> # Fetch all user records
            >>> connector.get_users()
            >>> # Fetch user records for a specific primary user ID
            >>> connector.get_users(primary_user_id='A11111')
            >>> # Fetch a specific page of user records
            >>> connector.get_users(page=2, per_page=50)

        Note:
            The method automatically handles authentication using the stored credentials.
            Ensure that credentials are loaded and valid before making API calls.
        """

        # Ensure the credentials are loaded
        if not self.username or not self.api_key:
            print("Credentials are not loaded. Please load or update credentials.")
            return None

        # Making the API call
        try:
            response = requests.get(
                f'{self.base_url}/v3/users',
                params=kwargs,
                auth=HTTPBasicAuth(self.username, self.api_key)
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def get_user_by_id(self, user_id):
        """
        Fetches data for a single user record from the Navigate API.

        Args:
            user_id (int): The database level unique identifier of the user.

        Returns:
            dict: A dictionary containing the JSON response data with the user record.

        Raises:
            RequestException: If an error occurs during the API request.

        Examples:
            >>> connector = NavigateAPI()
            >>> user_data = connector.get_user_by_id(123456)
            >>> print(user_data)

        Note:
            The method automatically handles authentication using the stored credentials.
            Ensure that credentials are loaded and valid before making API calls.
        """

        # Ensure the credentials are loaded
        if not self.username or not self.api_key:
            print("Credentials are not loaded. Please load or update credentials.")
            return None

        # Making the API call
        try:
            response = requests.get(
                f'{self.base_url}/v3/users/{user_id}',
                auth=HTTPBasicAuth(self.username, self.api_key)
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None
        
    def get_notes(self, **kwargs):
        """
        Fetches note data from the Navigate API based on provided query parameters.

        This method sends a GET request to the Navigate API to retrieve note data. 
        The user can specify various query parameters to filter the note records. 
        If no parameters are provided, all note records are returned. 
        The data is paginated, and pagination parameters can also be passed.

        Args:
            **kwargs: Arbitrary keyword arguments. Allowed parameters include:
                - primary_user_id (str): Returns all records where the primary_user_id of 
                  the associated student matches the given input. This is the PIDM for GSU users.
                - created_by (str): Returns all records where the primary_user_id of 
                  the note creator matches the given input. This is the PIDM for GSU users.
                - page (int): Page number for paginated results. Default is 1.
                - per_page (int): The number of elements to be returned from the request, 
                  for paginated results. Default is 100.

        Returns:
            dict: A dictionary containing the JSON response data with note records.

        Raises:
            RequestException: If an error occurs during the API request.

        Examples:
            >>> connector = NavigateAPI()
            >>> # Fetch all note records
            >>> connector.get_notes()
            >>> # Fetch note records for a specific primary user ID
            >>> connector.get_notes(primary_user_id='A11111')
            >>> # Fetch note records created by a specific user
            >>> connector.get_notes(created_by='B22222')
            >>> # Fetch a specific page of note records
            >>> connector.get_notes(page=2, per_page=50)

        Note:
            The method automatically handles authentication using the stored credentials.
            Ensure that credentials are loaded and valid before making API calls.
        """

        # Ensure the credentials are loaded
        if not self.username or not self.api_key:
            print("Credentials are not loaded. Please load or update credentials.")
            return None

        # Making the API call
        try:
            response = requests.get(
                f'{self.base_url}/v3/notes',
                params=kwargs,
                auth=HTTPBasicAuth(self.username, self.api_key)
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None
        
    def get_reminders(self, **kwargs):
        """
        Fetches reminder data from the Navigate API based on provided query parameters.

        This method sends a GET request to the Navigate API to retrieve reminder data. 
        The user can specify various query parameters to filter the reminder records. 
        If no parameters are provided, all reminder records are returned. 
        The data is paginated, and pagination parameters can also be passed.

        Args:
            **kwargs: Arbitrary keyword arguments. Allowed parameters include:
                - primary_user_id (str): Returns all records where the primary_user_id of 
                  the associated student matches the given input.
                - staff_primary_user_id (str): Returns all records where the primary_user_id 
                  of the staff user associated with the reminder matches the given input.
                - page (int): Page number for paginated results. Default is 1.
                - per_page (int): The number of elements to be returned from the request, 
                  for paginated results. Default is 100.

        Returns:
            dict: A dictionary containing the JSON response data with reminder records.

        Raises:
            RequestException: If an error occurs during the API request.

        Examples:
            >>> connector = NavigateAPI()
            >>> # Fetch all reminder records
            >>> connector.get_reminders()
            >>> # Fetch reminder records for a specific primary user ID
            >>> connector.get_reminders(primary_user_id='A11111')
            >>> # Fetch reminder records associated with a specific staff user
            >>> connector.get_reminders(staff_primary_user_id='B22222')
            >>> # Fetch a specific page of reminder records
            >>> connector.get_reminders(page=2, per_page=50)

        Note:
            The method automatically handles authentication using the stored credentials.
            Ensure that credentials are loaded and valid before making API calls.
        """

        # Ensure the credentials are loaded
        if not self.username or not self.api_key:
            print("Credentials are not loaded. Please load or update credentials.")
            return None

        # Making the API call
        try:
            response = requests.get(
                f'{self.base_url}/v3/reminders',
                params=kwargs,
                auth=HTTPBasicAuth(self.username, self.api_key)
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def get_visits(self, **kwargs):
        """
        Fetches visit (checkin) data from the Navigate API based on provided query parameters.

        This method sends a GET request to the Navigate API to retrieve visit data. 
        The user can specify various query parameters to filter the visit records. 
        If no parameters are provided, all visit records are returned. 
        The data is paginated, and pagination parameters can also be passed.

        Args:
            **kwargs: Arbitrary keyword arguments. Allowed parameters include:
                - primary_user_id (str): Returns all records where the primary_user_id of 
                  the user associated with the visit matches the given input.
                - type (str): The type of visit, e.g., 'checkin'. If left empty, all types 
                  of visits will be included.
                - page (int): Page number for paginated results. Default is 1.
                - per_page (int): The number of elements to be returned from the request, 
                  for paginated results. Default is 100.

        Returns:
            dict: A dictionary containing the JSON response data with visit records.

        Raises:
            RequestException: If an error occurs during the API request.

        Examples:
            >>> connector = NavigateAPI()
            >>> # Fetch all visit records
            >>> connector.get_visits()
            >>> # Fetch visit records for a specific primary user ID
            >>> connector.get_visits(primary_user_id='A11111')
            >>> # Fetch visit records of a specific type
            >>> connector.get_visits(type='checkin')
            >>> # Fetch a specific page of visit records
            >>> connector.get_visits(page=2, per_page=50)

        Note:
            The method automatically handles authentication using the stored credentials.
            Ensure that credentials are loaded and valid before making API calls.
        """

        # Ensure the credentials are loaded
        if not self.username or not self.api_key:
            print("Credentials are not loaded. Please load or update credentials.")
            return None

        # Making the API call
        try:
            response = requests.get(
                f'{self.base_url}/v3/visits',
                params=kwargs,
                auth=HTTPBasicAuth(self.username, self.api_key)
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def get_attendance(self, **kwargs):
        """
        Fetches enrollment attendance data from the Navigate API based on provided query parameters.

        This method sends a GET request to the Navigate API to retrieve enrollment attendance data. 
        The user can specify various query parameters to filter the enrollment attendance records. 
        If no parameters are provided, all enrollment attendance records are returned. 
        The data is paginated, and pagination parameters can also be passed.

        Args:
            **kwargs: Arbitrary keyword arguments. Allowed parameters include:
                - primary_user_id (str): Returns all records where the primary_user_id of 
                  the student associated with the enrollment attendance matches the input.
                - term_external_id (str): The external ID for the term associated with the section.
                - section_external_id (str): The external ID for the section associated with the enrollment.
                - section_name (str): The section name for the section associated with the enrollment.
                - page (int): Page number for paginated results. Default is 1.
                - per_page (int): The number of elements to be returned from the request, 
                  for paginated results. Default is 100.

        Returns:
            dict: A dictionary containing the JSON response data with enrollment attendance records.

        Raises:
            RequestException: If an error occurs during the API request.

        Examples:
            >>> connector = NavigateAPI()
            >>> # Fetch all enrollment attendance records
            >>> connector.get_attendance()
            >>> # Fetch enrollment attendance records for a specific primary user ID
            >>> connector.get_attendance(primary_user_id='A11111')
            >>> # Fetch enrollment attendance records with specific term, section ID, and section name
            >>> connector.get_attendance(term_external_id='TERMID', section_external_id='SECTIONID', section_name='SECTIONNAME')
            >>> # Fetch a specific page of enrollment attendance records
            >>> connector.get_attendance(page=2, per_page=50)

        Note:
            The method automatically handles authentication using the stored credentials.
            Ensure that credentials are loaded and valid before making API calls.
        """

        # Ensure the credentials are loaded
        if not self.username or not self.api_key:
            print("Credentials are not loaded. Please load or update credentials.")
            return None

        # Making the API call
        try:
            response = requests.get(
                f'{self.base_url}/v3/enrollment_attendances',
                params=kwargs,
                auth=HTTPBasicAuth(self.username, self.api_key)
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None
        
    def get_assignments(self, **kwargs):
        """
        Fetches assignment data from the Navigate API based on provided query parameters.

        This method sends a GET request to the Navigate API to retrieve assignment data. 
        The user can specify various query parameters to filter the assignment records. 
        If no parameters are provided, all assignment records are returned. 
        The data is paginated, and pagination parameters can also be passed.

        Args:
            **kwargs: Arbitrary keyword arguments. Allowed parameters include:
                - external_id (str): Returns records where the external_id field matches the input.
                - section_external_id (str): Returns records where the section external_id 
                  field for the associated section matches the input.
                - page (int): Page number for paginated results. Default is 1.
                - per_page (int): The number of elements to be returned from the request, 
                  for paginated results. Default is 100.

        Returns:
            dict: A dictionary containing the JSON response data with assignment records.

        Raises:
            RequestException: If an error occurs during the API request.

        Examples:
            >>> connector = NavigateAPI()
            >>> # Fetch all assignment records
            >>> connector.get_assignments()
            >>> # Fetch assignment records with a specific external ID
            >>> connector.get_assignments(external_id='assignment1')
            >>> # Fetch assignment records for a specific section external ID
            >>> connector.get_assignments(section_external_id='section1')
            >>> # Fetch a specific page of assignment records
            >>> connector.get_assignments(page=2, per_page=50)

        Note:
            The method automatically handles authentication using the stored credentials.
            Ensure that credentials are loaded and valid before making API calls.
        """

        # Ensure the credentials are loaded
        if not self.username or not self.api_key:
            print("Credentials are not loaded. Please load or update credentials.")
            return None

        # Making the API call
        try:
            response = requests.get(
                f'{self.base_url}/v3/assignments',
                params=kwargs,
                auth=HTTPBasicAuth(self.username, self.api_key)
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None
        
    def get_assignment_feedback(self, **kwargs):
        """
        Fetches assignment feedback data from the Navigate API based on provided query parameters.

        This method sends a GET request to the Navigate API to retrieve enrollment assignment data. 
        The user can specify various query parameters to filter the enrollment assignment records. 
        If no parameters are provided, all enrollment assignment records are returned. 
        The data is paginated, and pagination parameters can also be passed.

        Args:
            **kwargs: Arbitrary keyword arguments. Allowed parameters include:
                - external_id (str): Returns all records where the external_id matches the given input.
                - assignment_external_id (str): Returns all records where the external_id of 
                  the associated assignment record matches the given input.
                - page (int): Page number for paginated results. Default is 1.
                - per_page (int): The number of elements to be returned from the request, 
                  for paginated results. Default is 100.

        Returns:
            dict: A dictionary containing the JSON response data with enrollment assignment records.

        Raises:
            RequestException: If an error occurs during the API request.

        Examples:
            >>> connector = NavigateAPI()
            >>> # Fetch all enrollment assignment records
            >>> connector.get_assignment_feedback()
            >>> # Fetch enrollment assignment records with a specific external ID
            >>> connector.get_assignment_feedback(external_id='A1S1')
            >>> # Fetch enrollment assignment records with a specific assignment external ID
            >>> connector.get_assignment_feedback(assignment_external_id='ASSIGNMENTID')
            >>> # Fetch a specific page of enrollment assignment records
            >>> connector.get_assignment_feedback(page=2, per_page=50)

        Note:
            The method automatically handles authentication using the stored credentials.
            Ensure that credentials are loaded and valid before making API calls.
        """

        # Ensure the credentials are loaded
        if not self.username or not self.api_key:
            print("Credentials are not loaded. Please load or update credentials.")
            return None

        # Making the API call
        try:
            response = requests.get(
                f'{self.base_url}/v3/enrollment_assignments',
                params=kwargs,
                auth=HTTPBasicAuth(self.username, self.api_key)
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None
        
    def get_appointments(self, **kwargs):
        """
        Fetches appointment data from the Navigate API based on provided query parameters.

        The method accepts any combination of the API's parameters as keyword arguments.

        Args:
            **kwargs: Arbitrary keyword arguments. Allowed parameters include:
                - begin_date (str): Begin date of the appointments in mm/dd/yyyy format.
                - end_date (str): End date of the appointments in mm/dd/yyyy format.
                - appointment_type (str, optional): Type of appointments ("advising", "tutoring", "general_event").
                - organizer_ids (str, optional): Comma-separated list of primary user ids of organizers.
                - attendee_ids (str, optional): Comma-separated list of primary user ids of attendees.
                - locations (str, optional): Comma-separated list of location names.
                - student_services (str, optional): Comma-separated list of student service names.

        Returns:
            list: A list containing the JSON response data with appointment records.

        Raises:
            RequestException: If an error occurs during the API request.
        """

        # Ensure the credentials are loaded
        if not self.username or not self.api_key:
            print("Credentials are not loaded. Please load or update credentials.")
            return None

        # Making the API call
        try:
            response = requests.get(
                f'{self.base_url}/appointments',
                params=kwargs,
                auth=HTTPBasicAuth(self.username, self.api_key)
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None
        
    def get_endpoint(self, endpoint, **kwargs):
        """
        Fetches data from the Navigate API from a specified endpoint based on provided query parameters.

        This method sends a GET request to the Navigate API to retrieve data from a specified endpoint. 
        The user can specify various query parameters to filter the records. 
        If no parameters are provided, all records for that endpoint are returned. 
        The data is paginated, and pagination parameters can also be passed.

        Args:
            endpoint (str): The API endpoint to fetch data from.
            **kwargs: Arbitrary keyword arguments for query parameters.
            See the Navigate API documentation for the specific endpoint for allowed parameters:
            https://gsu.campus.eab.com/api/v3/docs#!/Read_data_APIs/ShowAssignment

        Returns:
            dict: A dictionary containing the JSON response data from the specified endpoint.

        Raises:
            RequestException: If an error occurs during the API request.

        Examples:
            >>> connector = NavigateAPI()
            >>> # Fetch first page of alerts
            >>> connector.get_endpoint('alerts')
            >>> # Fetch user records for a specific primary user ID
            >>> connector.get_endpoint('users', primary_user_id='A11111')
            >>> # Fetch notes created by a specific user
            >>> connector.get_endpoint('notes', created_by='B22222')

        Note:
            The method automatically handles authentication using the stored credentials.
            Ensure that credentials are loaded and valid before making API calls.
        """

        # Ensure the credentials are loaded
        if not self.username or not self.api_key:
            print("Credentials are not loaded. Please load or update credentials.")
            return None

        # Making the API call
        try:
            response = requests.get(
                f'{self.base_url}/v3/{endpoint}',
                params=kwargs,
                auth=HTTPBasicAuth(self.username, self.api_key)
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None