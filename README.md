# **SSNIT Records Management System**

A **user-friendly web application** built with **Streamlit** and **Pandas** to efficiently search, analyze, and manage SSNIT (Social Security and National Insurance Trust) contributor records.  

This tool is designed for **HR professionals, administrators, or data analysts** who need quick access to individual records and aggregated insights from large datasets.

---

## 🌟 **Key Features**

### 🧭 **Tabbed Interface**
A clean, organized interface with three distinct sections for different tasks:

- 🔍 **Records Lookup** – Search for an individual contributor by their unique **Unit Holder ID** to view their most recent record and personal details.  
- 💰 **Withdrawals** – View and filter all records that have withdrawal activity, with summary statistics and export capabilities.  
- 👥 **Retirees** – Automatically identify and display records for all contributors aged 60 and above, with options to filter by age range.  

---

### ⚙️ **Intelligent Data Loading**
Automatically detects and loads any CSV file in its directory, prioritizing a file named `Combined.csv` if it exists.

### 🧹 **Robust Data Cleaning**
Automatically cleans and standardizes key data columns (SSNIT numbers, dates of birth, month/year formats) to ensure consistency and accurate sorting.

### 📅 **Chronological Record Handling**
When multiple records exist for a single individual, the system intelligently sorts them chronologically and displays the most recent one, while also providing an option to download all historical data.

### 👵 **Dynamic Age Calculation**
Automatically calculates the current age of each contributor based on their date of birth — crucial for identifying retirees.

### 🔍 **Advanced Filtering**
Each tab provides powerful search and filter options, allowing users to narrow data by ID, withdrawal amount, or age.

### 💾 **Data Export**
Download filtered results or individual records as a CSV file for offline analysis or reporting.

### 📱 **Responsive Design**
Built with Streamlit, ensuring the interface is fully responsive and works seamlessly on both desktop and mobile devices.

---

## 🛠️ **Technical Stack**

| Component | Description |
|------------|-------------|
| **Language** | Python |
| **Framework** | Streamlit (web app interface) |
| **Data Manipulation** | Pandas (for data loading, cleaning, and analysis) |

---

## 🚀 **How to Run the Application Locally**

Follow these steps to get the application running on your computer:

### **1️⃣ Prerequisites**
- Python 3.8 or higher  
- pip (Python package installer)

---

### **2️⃣ Clone the Repository**
```bash
git clone https://github.com/AndyBa275/ssnit-records-management-system.git
cd ssnit-records-management-system
```

---

### **3️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```

If you don’t have a `requirements.txt` file, you can install directly:
```bash
pip install streamlit pandas
```

---

### **4️⃣ Prepare Your Data**

A sample file (`sample_data/Combined.csv`) is included for testing.  
It contains:
- Multiple records for one individual  
- Several retirees (age 60+)  
- Records with withdrawal activity  

To use your own data:
1. Place your SSNIT records (CSV format) in the project’s root folder.  
2. Ensure your file includes these columns:  
   - `Unit Holder ID`  
   - `Contributor Name`  
   - `Social Security #`  
   - `Date_of_Birth`  
   - `Withdrawals`  
   - `Year`  
   - `Month`  
3. The app automatically detects and loads your file. If `Combined.csv` exists, it will use that file first.

---

### **5️⃣ Launch the Application**
```bash
streamlit run app.py
```
The application will automatically open in your web browser.

---

## 💡 **Potential Enhancements**

This project can be extended with the following future features:

- 🗄️ **Database Integration** – Connect to PostgreSQL or SQLite for scalable data management.  
- 🔐 **User Authentication** – Add secure login for authorized users.  
- 📊 **Data Visualization** – Add charts to show trends (e.g., contributions or retiree age distribution).  
- 📝 **Data Entry & Editing** – Allow admins to add/edit records directly via the app.  
- ☁️ **Deployment** – Deploy to Streamlit Cloud, Render, or Heroku for public access.

---

## 👤 **Author**

**Andy Baiden**  
📧 [abaiden514@gmail.com](mailto:abaiden514@gmail.com)  
💼 [GitHub Profile](https://github.com/AndyBa275)

---

## 📜 **License**
This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.
