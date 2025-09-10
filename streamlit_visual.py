import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Set page config with emoji in title
st.set_page_config(page_title="🚌💩 Bus Departure Calculator")

# Custom CSS for background color
page_bg = """
<style>
.stApp {
    background-color: #007E7E; /* Teal color */
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

st.title("🚌💩 Bus Departure Calculator (with Visualisation)")

st.write("Enter bus **arrival times** (HH:MM) and optional extra minutes (e.g., toilet break).")
st.write("The app will calculate departures spaced as close as possible to the chosen headway and display them on a visual timeline.")

# Side-by-side layout
col1, col2 = st.columns([1, 2])

with col1:
    headway = st.number_input("Headway (minutes):", min_value=1, value=8)

with col2:
    st.write("Enter one arrival per line. Format:")
    st.code("HH:MM +ExtraMinutes", language="text")
    st.write("Example:")
    st.code("10:04 +5\n10:14\n10:26 +3\n10:31")
    arrivals = st.text_area(
        "Arrival times with optional adjustments:",
        height=200,
        placeholder="10:04 +5\n10:14\n10:26 +3\n10:31"
    )

if arrivals:
    try:
        arrival_list = arrivals.splitlines()
        original_arrivals = []
        adjusted_arrivals = []

        for t in arrival_list:
            if not t.strip():
                continue
            parts = t.strip().split()
            time_str = parts[0]
            base_time = datetime.strptime(time_str, "%H:%M")
            extra = 0
            if len(parts) > 1 and parts[1].startswith("+"):
                try:
                    extra = int(parts[1][1:])
                except ValueError:
                    st.warning(f"⚠️ Invalid extra minutes in line: {t}")
            original_arrivals.append(base_time)
            adjusted_arrivals.append(base_time + timedelta(minutes=extra))

        if not adjusted_arrivals:
            st.error("No valid times entered.")
        else:
            # Calculate departures
            departures = []
            last_departure = None
            for arr in adjusted_arrivals:
                if last_departure is None:
                    dep = arr
                else:
                    dep = max(arr, last_departure + timedelta(minutes=headway))
                departures.append(dep)
                last_departure = dep

            # Results table
            df = pd.DataFrame({
                "Original Arrival": [a.strftime("%H:%M") for a in original_arrivals],
                "Adjusted Arrival": [a.strftime("%H:%M") for a in adjusted_arrivals],
                "Departure": [d.strftime("%H:%M") for d in departures]
            })

            st.success("✅ Calculated Departure Times:")
            st.dataframe(df, use_container_width=True)

            # ========================
            # Visualisation Section
            # ========================
            st.subheader("🚌 Route Visualisation")

            # Convert departure times to minutes relative to first departure
            dep_minutes = [(d - departures[0]).seconds // 60 for d in departures]

            fig, ax = plt.subplots(figsize=(8, 2))

            # Plot buses
            for i, t in enumerate(dep_minutes):
                ax.plot(t, 0, 'o', markersize=15, color='skyblue')
                ax.text(t, 0.25, departures[i].strftime('%H:%M'),
                        ha='center', fontsize=9, color="white")

            # Draw arrows between buses
            for i in range(len(dep_minutes)-1):
                ax.annotate("",
                            xy=(dep_minutes[i+1], 0),
                            xytext=(dep_minutes[i], 0),
                            arrowprops=dict(arrowstyle="->", lw=2, color="white"))

            ax.set_ylim(-0.5, 1)
            ax.set_yticks([])
            ax.set_xlabel("Minutes from first departure", color="white")
            ax.set_facecolor("#007E7E")  # teal background
            ax.spines[['top','left','right','bottom']].set_visible(False)
            ax.tick_params(colors="white")

            st.pyplot(fig)

    except ValueError:
        st.error("⚠️ Invalid format. Please use HH:MM or HH:MM +Minutes (e.g., 10:15 +5).")
