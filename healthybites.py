import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import csv

app_id = "eaafef93"
app_key = "e4917753bdd3ac24a1f2109d44a148af"

def calculate_health_score(nutrients):
    score = 100
    if nutrients.get("sugar", 0) > 15:
        score -= 30
    if nutrients.get("fat", 0) > 20:
        score -= 25
    if nutrients.get("fiber", 0) < 3:
        score -= 20
    if nutrients.get("protein", 0) < 5:
        score -= 15
    return max(score, 0)

st.set_page_config(page_title="Healthy Bites", layout="centered")
st.title("🥗 Healthy Bites")
st.subheader("Search for a food and get its nutritional breakdown")

query = st.text_input("Enter a food item:", "apple")
search_button = st.button("Search")

if search_button and query:
    url = f"https://trackapi.nutritionix.com/v2/natural/nutrients"
    headers = {
        "x-app-id": app_id,
        "x-app-key": app_key,
        "Content-Type": "application/json"
    }
    body = {"query": query}

    response = requests.post(url, headers=headers, json=body)

    if response.status_code == 200:
        data = response.json()
        food_data = data["foods"][0]

        nutrients = {
            "calories": food_data.get("nf_calories", 0),
            "sugar": food_data.get("nf_sugars", 0),
            "fat": food_data.get("nf_total_fat", 0),
            "fiber": food_data.get("nf_dietary_fiber", 0),
            "protein": food_data.get("nf_protein", 0)
        }

        df = pd.DataFrame.from_dict(nutrients, orient='index', columns=['Amount'])
        st.dataframe(df)

        score = calculate_health_score(nutrients)
        st.metric("Health Score", score)

        if score >= 75:
            st.success("This is a healthy choice! 🥦")
        elif score >= 50:
            st.info("Moderate choice. Could be better.")
        elif score >= 25:
            st.warning("High sugar/fat content. Be cautious.")
        else:
            st.error("This is not a healthy option. ❌")

        st.subheader("Nutrient Breakdown")
        fig, ax = plt.subplots()
        ax.bar(nutrients.keys(), nutrients.values())
        st.pyplot(fig)

        if st.checkbox("Show raw JSON response"):
            st.json(data)

        with st.form("feedback_form"):
            st.subheader("Rate this food")
            rating = st.slider("How would you rate this food?", 1, 10, 5)
            comments = st.text_area("Leave a comment:")
            submitted = st.form_submit_button("Submit Feedback")

            if submitted:
                st.success("Thanks for your feedback!")
                with open("feedback.csv", "a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([query, rating, comments])
    else:
        st.error("Could not fetch data. Please check your credentials or try another item.")
