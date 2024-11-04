import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import pandas as pd

# Supabase project details
# Use secrets from Streamlit Cloud
supabase_url = st.secrets["supabase"]["url"]
supabase_key = st.secrets["supabase"]["key"]

# Initialize Supabase client
supabase: Client = create_client(supabase_url, supabase_key)

# Sidebar navigation
page = st.sidebar.selectbox("Navigation", ["Submit Sighting", "Monthly Stats"])

# Page 1: Form for submitting sighting
if page == "Submit Sighting":
    st.title("Crescent Moon Sighting Submission")
    
    # Form fields
    date_of_sighting = st.date_input("Date of Sighting")
    time_of_sighting = st.time_input("Time of Sighting (HH:MM:SS)", datetime.now().time())  # Allow exact time input
    name = st.text_input("Name")
    email = st.text_input("Email")
    # Sighting location with single-choice options
    sighting_location = st.selectbox(
        "Sighting Location", 
        ["Signal Hill", "Three Anchor Bay", "Gordons Bay", "Bakoven", "Stellenbosch", "Grabouw", "Other"]
    )
    # sighting_location = st.text_input("Sighting Location")
    # weather_conditions = st.text_area("Weather Conditions")
    # Weather conditions with multiple-choice options
    # weather_conditions = st.multiselect(
    #     "Weather Conditions", 
    #     ["Cloudy", "Hazy", "Red Horizon", "Clear", "Misty", "Other"]
    # )

        # Weather conditions with checkboxes
    st.write("Weather Conditions (select all that apply):")
    cloudy = st.checkbox("Cloudy")
    hazy = st.checkbox("Hazy")
    red_horizon = st.checkbox("Red Horizon")
    clear = st.checkbox("Clear")
    misty = st.checkbox("Misty")
    other_weather = st.checkbox("Other")
    
    # Collect selected weather conditions
    weather_conditions = []
    if cloudy: weather_conditions.append("Cloudy")
    if hazy: weather_conditions.append("Hazy")
    if red_horizon: weather_conditions.append("Red Horizon")
    if clear: weather_conditions.append("Clear")
    if misty: weather_conditions.append("Misty")
    if other_weather: weather_conditions.append("Other")

    crescent_sighted = st.selectbox("Crescent Sighted", ["Yes", "No"])
    num_members = st.number_input("Number of Members", min_value=0, step=1)
    num_non_members = st.number_input("Number of Non-members", min_value=0, step=1)
    additional_info = st.text_area("Any Additional Information?")
    
    # Submit button
    if st.button("Submit Sighting"):
        # Get the current date and time for submission
        submit_date_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        
        # Prepare data for insertion
        new_sighting = {
            "date_of_sighting": date_of_sighting.strftime("%Y-%m-%d"),
            "time_of_sighting": time_of_sighting.strftime("%H:%M:%S"),
            "name": name,
            "email": email,
            "sighting_location": sighting_location,
            "weather_conditions": ", ".join(weather_conditions),
            "crescent_sighted": crescent_sighted,
            "num_members": num_members,
            "num_non_members": num_non_members,
            "additional_info": additional_info,
            "submit_date_time": submit_date_time  # Add current date and time here
        }
        
        # Insert data into Supabase
        try:
            response = supabase.table("sightings").insert(new_sighting).execute()
            if response.data:
                st.success("Sighting successfully submitted!")
            else:
                st.error("Failed to submit sighting. Please try again.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

        # Display last 10 entries
    st.subheader("Last 10 Entries")
    try:
        response = supabase.table("sightings").select("*").order("submit_date_time", desc=True).limit(10).execute()
        if response.data:
            entries_data = response.data
            entries_df = pd.DataFrame(entries_data)

            # Display the last 10 entries
            if not entries_df.empty:
                st.table(entries_df[["date_of_sighting", "time_of_sighting", "sighting_location", "weather_conditions", "crescent_sighted", "num_members", "num_non_members", "additional_info"]])
            else:
                st.info("No entries found.")
        else:
            st.error("Failed to retrieve last entries.")
    except Exception as e:
        st.error(f"An error occurred while retrieving last entries: {e}")

# Page 2: Display monthly stats
elif page == "Monthly Stats":
    st.title("Monthly Crescent Sighting Statistics")
    
    # Select a month and year
    selected_year = st.selectbox("Select Year", range(2024, datetime.now().year + 1))
    selected_month = st.selectbox("Select Month", range(1, 13))
    
    # Fetch and filter sightings for the selected month and year
    try:
        response = supabase.table("sightings").select("*").execute()
        if response.data:
            sightings_data = response.data
            sightings_df = pd.DataFrame(sightings_data)
            
            # Filter data for the selected month and year
            sightings_df["date_of_sighting"] = pd.to_datetime(sightings_df["date_of_sighting"])
            monthly_data = sightings_df[(sightings_df["date_of_sighting"].dt.year == selected_year) &
                                        (sightings_df["date_of_sighting"].dt.month == selected_month)]
            
            # Display monthly stats if data exists for the selected month
            if not monthly_data.empty:
                display_data = monthly_data[["sighting_location", "weather_conditions", "crescent_sighted",
                                             "num_members", "num_non_members","additional_info"]]
                st.write(f"Statistics for {datetime(selected_year, selected_month, 1).strftime('%B %Y')}")
                st.table(display_data)
            else:
                st.info("No sightings data available for the selected month.")
        else:
            st.error("Failed to retrieve data. Please try again.")
    except Exception as e:
        st.error(f"An error occurred while retrieving data: {e}")
