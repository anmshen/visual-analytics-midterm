from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

data = pd.read_csv("placementdata.csv")
app.data = data

# more stuff here 

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)