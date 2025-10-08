import streamlit as st
import pandas as pd
import re
from datetime import datetime, date
import io
import os

# Page configuration
st.set_page_config(
    page_title="SSNIT Records Management System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.search-container {
    background-color: #f0f2f6;
    padding: 2rem;
    border-radius: 10px;
    margin-bottom: 2rem;
}
.result-container {
    background-color: #ffffff;
    padding: 1.5rem;
    border-radius: 10px;
    border: 1px solid #e0e0e0;
    margin-bottom: 1rem;
}
.success-box {
    background-color: #e8f5e8;
    padding: 1rem;
    border-radius: 5px;
    border-left: 4px solid #44ff44;
}
.error-box {
    background-color: #ffe8e8;
    padding: 1rem;
    border-radius: 5px;
    border-left: 4px solid #ff4444;
}
.latest-record {
    background-color: #e8f4fd;
    padding: 1rem;
    border-radius: 5px;
    border-left: 4px solid #1f77b4;
    margin-bottom: 1rem;
}
.withdrawal-card {
    background-color: #fff3cd;
    padding: 1rem;
    border-radius: 5px;
    border-left: 4px solid #ffc107;
    margin-bottom: 1rem;
}
.retiree-card {
    background-color: #d1ecf1;
    padding: 1rem;
    border-radius: 5px;
    border-left: 4px solid #17a2b8;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load the SSNIT data - supports any CSV file in the directory"""
    try:
        # Get all CSV files in the current directory
        csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if not csv_files:
            st.error("No CSV files found in the current directory")
            return pd.DataFrame(), ""
        
        # If there's a Combined.csv, use it, otherwise use the first CSV file
        if 'Combined.csv' in csv_files:
            file_to_use = 'Combined.csv'
        else:
            file_to_use = csv_files[0]
        
        df = pd.read_csv(file_to_use)
        st.success(f"Data loaded successfully from: {file_to_use}")
        
        # Clean the Social Security column
        if 'Social Security #' in df.columns:
            df['Social Security #'] = df['Social Security #'].astype(str).str.strip()
        
        # Handle different date column names
        date_columns = ['Date_of_Birth', 'combined', 'DOB', 'Birth_Date']
        for col in date_columns:
            if col in df.columns:
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    df['birth_date'] = df[col]  # Standardize to 'birth_date'
                    break
                except:
                    continue
        
        # Convert Year to numeric for proper sorting
        if 'Year' in df.columns:
            df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        
        # Handle Month column - keep original values but create a numeric version for sorting
        if 'Month' in df.columns:
            # Keep original month values
            df['Month_original'] = df['Month'].astype(str)
            
            # Create numeric version for sorting
            month_map = {
                'jan': 1, 'january': 1,
                'feb': 2, 'february': 2,
                'mar': 3, 'march': 3,
                'apr': 4, 'april': 4,
                'may': 5, 
                'jun': 6, 'june': 6,
                'jul': 7, 'july': 7,
                'aug': 8, 'august': 8,
                'sep': 9, 'september': 9,
                'oct': 10, 'october': 10,
                'nov': 11, 'november': 11,
                'dec': 12, 'december': 12
            }
            
            # Create numeric month column for sorting
            df['Month_numeric'] = df['Month'].astype(str).str.lower().str.strip().map(month_map)
            df['Month_numeric'] = pd.to_numeric(df['Month_numeric'], errors='coerce')
        
        # Sort the entire dataframe chronologically (oldest first)
        if 'Year' in df.columns and 'Month_numeric' in df.columns:
            df = df.sort_values(['Year', 'Month_numeric'], ascending=[True, True])
        
        # Clean withdrawals column for filtering
        if 'Withdrawals' in df.columns:
            df['Withdrawals'] = pd.to_numeric(df['Withdrawals'], errors='coerce').fillna(0)
        
        return df, file_to_use
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame(), ""

def validate_unit_holder_id(unit_holder_id):
    """Validate Unit Holder ID format"""
    if not unit_holder_id:
        return False, "Please enter a Unit Holder ID"
    
    unit_holder_clean = str(unit_holder_id).strip()
    
    # Basic validation - adjust these rules based on your Unit Holder ID format
    if len(unit_holder_clean) < 3:
        return False, f"Unit Holder ID seems too short (currently {len(unit_holder_clean)} characters)"
    
    return True, unit_holder_clean

def calculate_age(birth_date):
    """Calculate age from birth date"""
    if pd.isna(birth_date):
        return "N/A"
    
    try:
        if isinstance(birth_date, str):
            birth_date = pd.to_datetime(birth_date)
        
        today = date.today()
        birth_date = birth_date.date()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except:
        return "N/A"

def search_by_unit_holder_id(df, unit_holder_id):
    """Search for records by Unit Holder ID and return the most recent one"""
    if 'Unit Holder ID' not in df.columns:
        return pd.DataFrame(), pd.DataFrame()
    
    # Convert both to string for comparison to handle mixed data types
    df_copy = df.copy()
    df_copy['Unit Holder ID'] = df_copy['Unit Holder ID'].astype(str).str.strip()
    unit_holder_id = str(unit_holder_id).strip()
    
    # Get all records for this Unit Holder ID
    all_results = df_copy[df_copy['Unit Holder ID'] == unit_holder_id].copy()
    
    if len(all_results) == 0:
        return pd.DataFrame(), pd.DataFrame()
    
    # Sort chronologically (oldest first)
    if 'Year' in all_results.columns and 'Month_numeric' in all_results.columns:
        all_results = all_results.sort_values(['Year', 'Month_numeric'], ascending=[True, True])
    
    # Get the most recent record (last row after sorting)
    latest_record = all_results.iloc[[-1]]
    
    return latest_record, all_results

def get_withdrawal_records(df):
    """Get all records with withdrawals (not equal to 0)"""
    if 'Withdrawals' not in df.columns:
        return pd.DataFrame()
    
    withdrawal_records = df[df['Withdrawals'] != 0].copy()
    
    # Add age calculation for additional info
    if 'birth_date' in withdrawal_records.columns:
        withdrawal_records['Age'] = withdrawal_records['birth_date'].apply(calculate_age)
    
    # Sort chronologically (oldest first)
    if 'Year' in withdrawal_records.columns and 'Month_numeric' in withdrawal_records.columns:
        withdrawal_records = withdrawal_records.sort_values(['Year', 'Month_numeric'], ascending=[True, True])
    
    return withdrawal_records

def get_retiree_records(df):
    """Get all records where person is 60 years or older"""
    if 'birth_date' not in df.columns:
        return pd.DataFrame()
    
    # Calculate ages and filter for 60+
    df_with_age = df.copy()
    df_with_age['Age'] = df_with_age['birth_date'].apply(calculate_age)
    
    # Filter for valid numeric ages first, then check >= 60
    numeric_ages = df_with_age[df_with_age['Age'] != "N/A"].copy()
    retiree_records = numeric_ages[numeric_ages['Age'] >= 60].copy()
    
    # Sort chronologically (oldest first)
    if 'Year' in retiree_records.columns and 'Month_numeric' in retiree_records.columns:
        retiree_records = retiree_records.sort_values(['Year', 'Month_numeric'], ascending=[True, True])
    
    return retiree_records

def display_record(record, all_records):
    """Display a single record with information about multiple records"""
    # Show info about multiple records if they exist
    if len(all_records) > 1:
        st.markdown('<div class="latest-record">', unsafe_allow_html=True)
        st.info(f"📊 **Multiple records found ({len(all_records)} total)** - Showing the most recent record from {record['Year'].iloc[0] if 'Year' in record.columns else 'N/A'}")
        
        # Show years available
        if 'Year' in all_records.columns:
            years = sorted(all_records['Year'].dropna().unique())
            st.write(f"**Available years:** {', '.join(map(str, years))}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="result-container">', unsafe_allow_html=True)
    
    # Personal Information
    st.subheader("Personal Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Name:** {record['Contributor Name'].iloc[0] if 'Contributor Name' in record.columns else 'N/A'}")
        st.write(f"**Unit Holder ID:** {record['Unit Holder ID'].iloc[0] if 'Unit Holder ID' in record.columns else 'N/A'}")
        st.write(f"**SSNIT Number:** {record['Social Security #'].iloc[0] if 'Social Security #' in record.columns else 'N/A'}")
        
        # Handle birth date
        birth_date = record['birth_date'].iloc[0] if 'birth_date' in record.columns else None
        age = calculate_age(birth_date)
        st.write(f"**Date of Birth:** {birth_date if not pd.isna(birth_date) else 'N/A'}")
        st.write(f"**Age:** {age}")
    
    with col2:
        st.write(f"**Address:** {record['Address'].iloc[0] if 'Address' in record.columns and not pd.isna(record['Address'].iloc[0]) else 'N/A'}")
        st.write(f"**Year:** {record['Year'].iloc[0] if 'Year' in record.columns else 'N/A'}")
        st.write(f"**Month:** {record['Month_original'].iloc[0] if 'Month_original' in record.columns and not pd.isna(record['Month_original'].iloc[0]) else 'N/A'}")
    
    # Employment Information
    st.subheader("Employment Information")
    col3, col4 = st.columns(2)
    
    with col3:
        st.write(f"**Employer Code:** {record['Employer Code'].iloc[0] if 'Employer Code' in record.columns and not pd.isna(record['Employer Code'].iloc[0]) else 'N/A'}")
        st.write(f"**Scheme Code:** {record['Scheme Code'].iloc[0] if 'Scheme Code' in record.columns and not pd.isna(record['Scheme Code'].iloc[0]) else 'N/A'}")
    
    # Financial Information
    st.subheader("Financial Information")
    col5, col6, col7 = st.columns(3)
    
    with col5:
        st.write(f"**Begin Balance:** {record['Begin Bal'].iloc[0] if 'Begin Bal' in record.columns and not pd.isna(record['Begin Bal'].iloc[0]) else 'N/A'}")
        st.write(f"**End Balance:** {record['End Bal'].iloc[0] if 'End Bal' in record.columns and not pd.isna(record['End Bal'].iloc[0]) else 'N/A'}")
    
    with col6:
        st.write(f"**Withdrawals:** {record['Withdrawals'].iloc[0] if 'Withdrawals' in record.columns and not pd.isna(record['Withdrawals'].iloc[0]) else 'N/A'}")
        st.write(f"**Contribution:** {record['Contribution'].iloc[0] if 'Contribution' in record.columns and not pd.isna(record['Contribution'].iloc[0]) else 'N/A'}")
    
    with col7:
        st.write(f"**App Contribute:** {record['App Contribute'].iloc[0] if 'App Contribute' in record.columns and not pd.isna(record['App Contribute'].iloc[0]) else 'N/A'}")
        st.write(f"**Misc Contri.:** {record['Misc Contri.'].iloc[0] if 'Misc Contri.' in record.columns and not pd.isna(record['Misc Contri.'].iloc[0]) else 'N/A'}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_withdrawal_summary(withdrawal_records):
    """Display summary of withdrawal records"""
    if len(withdrawal_records) == 0:
        st.info("No withdrawal records found.")
        return
    
    st.markdown('<div class="withdrawal-card">', unsafe_allow_html=True)
    st.subheader("💰 Withdrawal Records Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Records", len(withdrawal_records))
    with col2:
        total_withdrawals = withdrawal_records['Withdrawals'].sum()
        st.metric("Total Withdrawals", f"₵{total_withdrawals:,.2f}")
    with col3:
        positive_withdrawals = withdrawal_records[withdrawal_records['Withdrawals'] > 0]['Withdrawals'].sum()
        st.metric("Positive Withdrawals", f"₵{positive_withdrawals:,.2f}")
    with col4:
        negative_withdrawals = withdrawal_records[withdrawal_records['Withdrawals'] < 0]['Withdrawals'].sum()
        st.metric("Negative Adjustments", f"₵{negative_withdrawals:,.2f}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_retiree_summary(retiree_records):
    """Display summary of retiree records"""
    if len(retiree_records) == 0:
        st.info("No retiree records found (age 60+).")
        return
    
    st.markdown('<div class="retiree-card">', unsafe_allow_html=True)
    st.subheader("👥 Retiree Records Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Retirees", len(retiree_records))
    with col2:
        avg_age = retiree_records['Age'].mean()
        st.metric("Average Age", f"{avg_age:.1f} years")
    with col3:
        oldest_age = retiree_records['Age'].max()
        st.metric("Oldest Person", f"{oldest_age} years")
    with col4:
        age_60_65 = len(retiree_records[(retiree_records['Age'] >= 60) & (retiree_records['Age'] <= 65)])
        st.metric("Ages 60-65", age_60_65)
    
    st.markdown('</div>', unsafe_allow_html=True)

def records_lookup_tab(df, filename):
    """Handle the Records Lookup functionality"""
    st.subheader("🔍 Search by Unit Holder ID")
    
    # Search Container
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        unit_holder_input = st.text_input(
            "Enter Unit Holder ID:",
            placeholder="e.g., 12345678",
            help="Enter the Unit Holder ID to search for records",
            key="records_search"
        )
    
    with col2:
        st.write("")
        st.write("")
        search_button = st.button("Search", type="primary", key="records_search_btn")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Perform search
    if search_button or unit_holder_input:
        if unit_holder_input:
            is_valid, result = validate_unit_holder_id(unit_holder_input)
            
            if not is_valid:
                st.markdown(f'<div class="error-box">ERROR: {result}</div>', unsafe_allow_html=True)
            else:
                unit_holder_clean = result
                
                with st.spinner("Searching..."):
                    latest_record, all_records = search_by_unit_holder_id(df, unit_holder_clean)
                
                if len(latest_record) == 0:
                    st.markdown(f'<div class="error-box">No record found for Unit Holder ID: {unit_holder_clean}</div>', unsafe_allow_html=True)
                    st.info("Please check the Unit Holder ID and try again.")
                else:
                    st.markdown(f'<div class="success-box">Record found for Unit Holder ID: {unit_holder_clean}</div>', unsafe_allow_html=True)
                    display_record(latest_record, all_records)
                    
                    # Export options
                    st.subheader("Export Options")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Export latest record
                        export_latest = latest_record.copy()
                        # Ensure we maintain original column order and use original month values
                        export_latest = export_latest[df.columns]
                        if 'Month_original' in export_latest.columns:
                            export_latest['Month'] = export_latest['Month_original']
                        csv_data_latest = export_latest.to_csv(index=False)
                        st.download_button(
                            label="📄 Download Latest Record",
                            data=csv_data_latest,
                            file_name=f"UnitHolder_{unit_holder_clean}_latest_record.csv",
                            mime="text/csv"
                        )
                    
                    with col2:
                        # Export all records for this person
                        if len(all_records) > 1:
                            export_all = all_records.copy()
                            # Ensure we maintain original column order and use original month values
                            export_all = export_all[df.columns]
                            if 'Month_original' in export_all.columns:
                                export_all['Month'] = export_all['Month_original']
                            csv_data_all = export_all.to_csv(index=False)
                            st.download_button(
                                label=f"📋 Download All Records ({len(all_records)})",
                                data=csv_data_all,
                                file_name=f"UnitHolder_{unit_holder_clean}_all_records.csv",
                                mime="text/csv"
                            )

def withdrawals_tab(df, filename):
    """Handle the Withdrawals functionality"""
    st.subheader("💰 Withdrawal Records")
    
    withdrawal_records = get_withdrawal_records(df)
    
    if len(withdrawal_records) == 0:
        st.warning("No withdrawal records found in the database.")
        return
    
    # Display summary
    display_withdrawal_summary(withdrawal_records)
    
    # Search and filter options
    st.subheader("Search & Filter")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        unit_holder_search = st.text_input("Search by Unit Holder ID:", key="withdrawal_unit_holder_search")
    
    with col2:
        min_amount = st.number_input("Minimum Amount:", value=None, key="withdrawal_min_amount")
    
    with col3:
        withdrawal_type = st.selectbox("Withdrawal Type:", 
                                     ["All", "Positive Only", "Negative Only"], 
                                     key="withdrawal_type")
    
    # Apply filters
    filtered_records = withdrawal_records.copy()
    
    if unit_holder_search:
        filtered_records = filtered_records[
            filtered_records['Unit Holder ID'].astype(str).str.contains(unit_holder_search, case=False, na=False)
        ]
    
    if min_amount is not None:
        filtered_records = filtered_records[abs(filtered_records['Withdrawals']) >= min_amount]
    
    if withdrawal_type == "Positive Only":
        filtered_records = filtered_records[filtered_records['Withdrawals'] > 0]
    elif withdrawal_type == "Negative Only":
        filtered_records = filtered_records[filtered_records['Withdrawals'] < 0]
    
    # Display results
    st.subheader(f"Results ({len(filtered_records)} records)")
    
    if len(filtered_records) > 0:
        # Select columns to display
        display_columns = ['Contributor Name', 'Unit Holder ID', 'Withdrawals', 'Year', 'Month_original']
        if 'Age' in filtered_records.columns:
            display_columns.append('Age')
        
        # Filter to existing columns and rename Month_original to Month for display
        display_df = filtered_records.copy()
        if 'Month_original' in display_df.columns:
            display_df['Month'] = display_df['Month_original']
        display_columns = [col.replace('Month_original', 'Month') for col in display_columns]
        
        st.dataframe(
            display_df[display_columns],
            use_container_width=True,
            hide_index=True
        )
        
        # Export option - maintain original column order and sorting
        st.subheader("Export Results")
        export_data = filtered_records.copy()
        export_data = export_data[df.columns]  # Maintain original column order
        if 'Month_original' in export_data.columns:
            export_data['Month'] = export_data['Month_original']
        
        csv_data = export_data.to_csv(index=False)
        st.download_button(
            label=f"📊 Download Withdrawal Records ({len(filtered_records)} records)",
            data=csv_data,
            file_name="withdrawal_records.csv",
            mime="text/csv"
        )
    else:
        st.info("No records match your search criteria.")

def retirees_tab(df, filename):
    """Handle the Retirees functionality"""
    st.subheader("👥 Retiree Records (Age 60+)")
    
    retiree_records = get_retiree_records(df)
    
    if len(retiree_records) == 0:
        st.warning("No retiree records found (people aged 60 or above).")
        return
    
    # Display summary
    display_retiree_summary(retiree_records)
    
    # Search and filter options
    st.subheader("Search & Filter")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        unit_holder_search = st.text_input("Search by Unit Holder ID:", key="retiree_unit_holder_search")
    
    with col2:
        min_age = st.number_input("Minimum Age:", value=60, min_value=60, max_value=100, key="retiree_min_age")
    
    with col3:
        max_age = st.number_input("Maximum Age:", value=100, min_value=60, max_value=120, key="retiree_max_age")
    
    # Apply filters
    filtered_records = retiree_records.copy()
    
    if unit_holder_search:
        filtered_records = filtered_records[
            filtered_records['Unit Holder ID'].astype(str).str.contains(unit_holder_search, case=False, na=False)
        ]
    
    filtered_records = filtered_records[
        (filtered_records['Age'] >= min_age) & 
        (filtered_records['Age'] <= max_age)
    ]
    
    # Display results
    st.subheader(f"Results ({len(filtered_records)} records)")
    
    if len(filtered_records) > 0:
        # Select columns to display
        display_columns = ['Contributor Name', 'Unit Holder ID', 'Age', 'birth_date', 'Year', 'Month_original']
        
        # Filter to existing columns and rename Month_original to Month for display
        display_df = filtered_records.copy()
        if 'Month_original' in display_df.columns:
            display_df['Month'] = display_df['Month_original']
        display_columns = [col.replace('Month_original', 'Month') for col in display_columns]
        
        st.dataframe(
            display_df[display_columns],
            use_container_width=True,
            hide_index=True
        )
        
        # Export option - maintain original column order and sorting
        st.subheader("Export Results")
        export_data = filtered_records.copy()
        export_data = export_data[df.columns]  # Maintain original column order
        if 'Month_original' in export_data.columns:
            export_data['Month'] = export_data['Month_original']
        
        csv_data = export_data.to_csv(index=False)
        st.download_button(
            label=f"👥 Download Retiree Records ({len(filtered_records)} records)",
            data=csv_data,
            file_name="retiree_records.csv",
            mime="text/csv"
        )
    else:
        st.info("No records match your search criteria.")

def main():
    # Header
    st.markdown('<h1 class="main-header">SSNIT Records Management System</h1>', unsafe_allow_html=True)
    
    # Load data
    df, filename = load_data()
    
    if df.empty:
        st.warning("No data available. Please ensure you have a CSV file in this directory.")
        st.stop()
    
    # Sidebar with information
    with st.sidebar:
        st.header("Database Info")
        st.info(f"**File:** {filename}")
        st.info(f"**Total Records:** {len(df):,}")
        
        if 'Year' in df.columns:
            years = sorted(df['Year'].dropna().unique())
            st.info(f"**Years Available:** {', '.join(map(str, years))}")
        
        # Quick stats
        st.header("Quick Stats")
        
        # Withdrawal stats
        if 'Withdrawals' in df.columns:
            withdrawal_count = len(df[df['Withdrawals'] != 0])
            st.metric("Withdrawal Records", withdrawal_count)
        
        # Retiree stats
        if 'birth_date' in df.columns:
            df_temp = df.copy()
            df_temp['Age'] = df_temp['birth_date'].apply(calculate_age)
            # Filter for numeric ages only, then check >= 60
            numeric_ages = df_temp[df_temp['Age'] != "N/A"]
            retiree_count = len(numeric_ages[numeric_ages['Age'] >= 60])
            st.metric("Retirees (60+)", retiree_count)
        
        st.header("How to Use")
        st.markdown("""
        **Records Lookup:** Search individual records by Unit Holder ID
        
        **Withdrawals:** View all records with withdrawal activity
        
        **Retirees:** View all people aged 60 and above
        """)
        
        # Refresh button
        if st.button("Refresh Data"):
            st.cache_data.clear()
            st.rerun()
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["🔍 Records Lookup", "💰 Withdrawals", "👥 Retirees"])
    
    with tab1:
        records_lookup_tab(df, filename)
    
    with tab2:
        withdrawals_tab(df, filename)
    
    with tab3:
        retirees_tab(df, filename)
    
    # Footer
    st.markdown("---")
    st.markdown(f"**SSNIT Records Management System** | Current Data: {filename}")

if __name__ == "__main__":
    main()

