import requests
import streamlit as st
import pandas as pd
import os

# Constants
API_KEY = os.getenv("API_KEY")
EVENT_ID = "108406"
BASE_URL = "https://api.congressus.nl/v30"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}


def get_participants():
    url = f"{BASE_URL}/events/{EVENT_ID}/participations"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching participants: {response.text}")
        return None


def list_addressees(participants):
    return [(p["id"], p["addressee"]) for p in participants]


def find_participant_by_addressee(participants, search_name):
    for p in participants:
        if p["addressee"].lower() == search_name.lower():
            return p
    return None


def set_presence(participant_id):
    url = f"{BASE_URL}/events/{EVENT_ID}/participations/{participant_id}/set-presence"
    payload = {"status_presence": "present"}
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
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
