import requests
import streamlit as st
import pandas as pd
import os

# Constants
API_KEY = os.getenv("API_KEY")
EVENT_ID = "108406"
BASE_URL = "https://api.congressus.nl/v30"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

# Authentication
PASSWORD = os.getenv("PASSWORD")
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False


def authenticate():
    password_input = st.text_input("Enter Password:", type="password")
    if st.button("Login"):
        if password_input == PASSWORD:
            st.session_state["authenticated"] = True
        else:
            st.error("Incorrect password. Try again.")


if not st.session_state["authenticated"]:
    authenticate()
    st.stop()


def get_participants():
    participants = []
    page = 1
    while True:
        url = f"{BASE_URL}/events/{EVENT_ID}/participations?page={page}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            participants.extend(data.get("data", []))  # Extract participants list from "data" key
            if not data.get("has_next", False):
                break  # Stop if there's no next page
            page += 1
        else:
            st.error(f"Error fetching participants: {response.text}")
            break
    return participants


def list_addressees(participants):
    return [(p.get("id"), p.get("addressee", "Unknown")) for p in participants]


def find_participant_by_addressee(participants, search_name):
    for p in participants:
        if p.get("addressee", "").lower() == search_name.lower():
            return p
    return None


def set_presence(participant_id):
    url = f"{BASE_URL}/events/{EVENT_ID}/participations/{participant_id}/set-presence"
    payload = {"status_presence": "present"}
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 204:
        st.success(f"Successfully marked participant {participant_id} as present.")
    else:
        st.error(f"Error setting presence: {response.text}")


st.title("Congressus Event Participation Manager")

participants = get_participants()
if participants:
    addressees = list_addressees(participants)
    df = pd.DataFrame(addressees, columns=["ID", "Addressee"])
    st.subheader("Participants")
    st.dataframe(df)

    search_name = st.selectbox("Select addressee to mark as present:", df["Addressee"].tolist())
    if st.button("Set Presence"):
        participant = find_participant_by_addressee(participants, search_name)
        if participant:
            set_presence(participant["id"])
        else:
            st.warning("Participant not found.")
