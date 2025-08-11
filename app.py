from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

app = Flask(__name__)

# Excel file to store patient data
excel_file = "patients.xlsx"

# Ensure static folder exists for charts
os.makedirs("static", exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        age = int(request.form["age"])
        disease = request.form["disease"]
        date = datetime.now().strftime("%Y-%m-%d")

        # Create a DataFrame for the new patient
        patient = pd.DataFrame([[name, age, disease, date]], 
                               columns=["Name", "Age", "Disease", "Date"])

        # Save to Excel
        if os.path.exists(excel_file):
            df = pd.read_excel(excel_file)
            df = pd.concat([df, patient], ignore_index=True)
        else:
            df = patient

        df.to_excel(excel_file, index=False)

        return render_template("success.html", name=name)

    return render_template("index.html")

@app.route("/analysis")
def analysis():
    if not os.path.exists(excel_file):
        return render_template("analysis.html", chart=None, message="No patient data yet.")

    df = pd.read_excel(excel_file)
    if df.empty:
        return render_template("analysis.html", chart=None, message="No patient data yet.")

    today = datetime.now().strftime("%Y-%m-%d")
    today_df = df[df["Date"] == today]

    if today_df.empty:
        return render_template("analysis.html", chart=None, message=f"No patient visits recorded for today ({today}).")

    disease_data = today_df["Disease"].value_counts()

    # Create pie chart
    plt.figure(figsize=(6,6))
    disease_data.plot(kind="pie", autopct='%1.1f%%', startangle=90, colormap='Set3')
    plt.title(f"Disease Distribution on {today}")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig("static/disease_chart.png")
    plt.close()

    return render_template("analysis.html", chart="static/disease_chart.png", message=None)

if __name__ == "__main__":
    app.run(debug=True)
