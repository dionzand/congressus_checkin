import requests
import streamlit as st
import pandas as pd
import os
import streamlit_authenticator as stauth

# Constants
API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.congressus.nl/v30"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

authenticator = stauth.Authenticate(
    st.secrets['credentials'].to_dict(),
    st.secrets['cookie']['name'],
    st.secrets['cookie']['key'],
    st.secrets['cookie']['expiry_days']
)


def get_participants():
    participants = []
    page = 1
    while True:
        params = {"status": "approved"}
        url = f"{BASE_URL}/events/{st.session_state["event_id"]}/participations?page={page}"
        response = requests.get(url, params=params, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            participants.extend(data.get("data", []))  # Extract participants list from "data" key
            if not data.get("has_next", False):
                break  # Stop if there's no next page
            page += 1
        else:
            st.error(f"Error bij het zoeken van deelnemer: {response.text}")
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
    url = f"{BASE_URL}/events/{st.session_state["event_id"]}/participations/{participant_id}/set-presence"
    payload = {"status_presence": "present"}
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 204:
        st.success(f"Deelnemer {participant_id} geregistreerd als aanwezig!")
    else:
        st.error(f"Kan aanwezigheid niet registreren voor: {response.text}")


def get_member_status(member_id):
    url = f"{BASE_URL}/members/{member_id}/statuses"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json().get("data", "")
        member_statuses = [p["name"] for p in data if not p["archived"]]
    else:
        member_statuses = ""
    return "".join(member_statuses)


st.title("Congressus aanwezigheid")

# Render the login widget
try:
    authenticator.login()
except Exception as e:
    st.error(e)

# Process login results
if st.session_state["authentication_status"]:
    if "event_id" not in st.session_state:
        event_id = st.text_input("Event ID")
        if st.button("Zoek event"):
            st.session_state["event_id"] = event_id

    if "event_id" in st.session_state:
        participants = get_participants()
        if participants:
            addressees = list_addressees(participants)
            df = pd.DataFrame(addressees, columns=["ID", "Addressee"])

            search_name = st.selectbox("Selecteer een deelnemer:", df["Addressee"].tolist())
            participant = find_participant_by_addressee(participants, search_name)
            if participant:
                member_status = get_member_status(participant["member_id"])
                st.write(f"Lidmaatschap status: {member_status}")
                if st.button("Zet deze deelnemer op aanwezig"):
                    set_presence(participant["id"])

            st.subheader("Deelnemers")
            st.dataframe(df)

elif st.session_state["authentication_status"] == False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] == None:
    st.warning('Please enter your username and password')
