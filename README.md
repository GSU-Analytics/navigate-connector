```markdown
# Navigate Connector

`navigate-connector` is a Python package for interacting with the Navigate API and SFTP service. It provides methods for retrieving student data, appointments, notes, alerts, and more from the Navigate system using API requests and an SFTP client.

## 🚀 Installation

### Install from GitHub
To install the latest version from GitHub:

```bash
pip install git+https://github.com/GSU-Analytics/navigate-connector.git
```

## 📂 Project Structure

```
navigate-connector/
│── navigate_connector/
│   ├── __init__.py              # Package initializer
│   ├── navigate_api.py          # API client for Navigate
│   ├── navigate_sftp.py         # SFTP client for Navigate
│── examples/
│   ├── get_appointments.py      # Example script for fetching appointments
│── tests/
│   ├── test_navigate_api.py     # Unit tests for API client
│   ├── test_navigate_sftp.py    # Unit tests for SFTP client
│── docs/
│   ├── index.md                 # Documentation
│── setup.py                     # Setup script for packaging
│── pyproject.toml               # Project metadata and dependencies
│── README.md                    # Project readme
│── LICENSE                      # License file
│── .gitignore                    # Files to ignore in Git
```

---

## 📖 Usage

### API Connector

The `NavigateAPI` class provides methods for retrieving data via the Navigate API.

#### Example: Fetch Alerts
```python
from navigate_connector import NavigateAPI

api = NavigateAPI()
alerts = api.get_alerts()
print(alerts)
```

#### Example: Fetch Appointments
```python
appointments = api.get_appointments(begin_date="01/01/2023", end_date="01/07/2023")
print(appointments)
```

---

### SFTP Connector

The `NavigateSFTP` class allows you to interact with the Navigate SFTP service.

#### Example: List Files in an SFTP Directory
```python
from navigate_connector import NavigateSFTP

sftp = NavigateSFTP(host="example.com", username="user", private_key_path="~/.ssh/id_rsa")
sftp.connect()
files = sftp.list_files()
print(files)
sftp.close()
```

#### Example: Download a File
```python
sftp.download_file("remote/path/file.csv", "local/path/file.csv")
```

#### Example: Upload a File
```python
sftp.upload_file("local/path/file.csv", "remote/path/file.csv")
```

---

## 🔍 Available Methods in `NavigateAPI`

| Method                        | Description |
|--------------------------------|-------------|
| `load_credentials()`          | Loads Navigate API credentials from the system keyring or prompts the user. |
| `update_credentials()`        | Prompts the user to update API credentials. |
| `get_alerts(**kwargs)`        | Retrieves alerts from the Navigate API. |
| `get_users(**kwargs)`         | Fetches user data based on query parameters. |
| `get_user_by_id(user_id)`     | Retrieves details for a single user. |
| `get_notes(**kwargs)`         | Fetches notes recorded in Navigate. |
| `get_reminders(**kwargs)`     | Retrieves reminders from Navigate. |
| `get_visits(**kwargs)`        | Retrieves visit/check-in records. |
| `get_attendance(**kwargs)`    | Fetches attendance data. |
| `get_assignments(**kwargs)`   | Retrieves assignment records. |
| `get_assignment_feedback(**kwargs)` | Fetches feedback on assignments. |
| `get_appointments(**kwargs)`  | Retrieves appointment records based on filters. |
| `get_endpoint(endpoint, **kwargs)` | Fetches data from any Navigate API endpoint dynamically. |

For more details on parameters, see the [Navigate API Documentation](https://gsu.campus.eab.com/api/v3/docs) or the project source code.

---

## 👨‍💻 Contributing to the Project

We welcome contributions! To get started:

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/GSU-Analytics/navigate-connector.git
cd navigate-connector
```

### 2️⃣ Set Up the Virtual Environment with Conda or Venv

Choose one of the following methods to set up a virtual environment for development:

### 🏗 Setting Up the Development Environment with Venv
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### 🏗 Setting Up the Development Environment with Conda

To set up a development environment using Conda, follow these steps:

1. **Create the environment**  
   Run the following command to create a Conda environment with all necessary dependencies:

   ```bash
   conda env create -f environment.yml
   ```

2. **Activate the environment**  
   ```bash
   conda activate navigate-connector
   ```

### 3️⃣ Install Dependencies
```bash
pip install -e .
```

### 4️⃣ Run Tests
Before submitting any changes, ensure all tests pass:

```bash
python -m unittest discover tests
```

### 5️⃣ Submit a Pull Request (PR)
1. Create a new feature branch:
   ```bash
   git checkout -b feature-branch
   ```
2. Make your changes and commit them:
   ```bash
   git commit -m "Add new feature"
   ```
3. Push your branch to GitHub:
   ```bash
   git push origin feature-branch
   ```
4. Open a pull request on [GitHub](https://github.com/GSU-Analytics/navigate-connector).

---

## 📚 Learn More

- **Navigate API Documentation:** [https://gsu.campus.eab.com/api/v3/docs](https://gsu.campus.eab.com/api/v3/docs)
- **GitHub Repository:** [https://github.com/GSU-Analytics/navigate-connector](https://github.com/GSU-Analytics/navigate-connector)
- **Set Up API Credentials:** [Keyring Documentation](https://pypi.org/project/keyring/)
- **SFTP Basics:** [Paramiko Documentation](http://docs.paramiko.org/en/stable/)