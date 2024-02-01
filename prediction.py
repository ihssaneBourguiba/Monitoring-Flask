import requests
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from datetime import timedelta
from matplotlib.dates import DayLocator, DateFormatter

# Fonction pour récupérer les données météorologiques de l'API Open Meteo
def get_weather_data(api_url):
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Erreur {response.status_code}: Impossible de récupérer les données météorologiques.")
        print(response.text)  # Affichez la réponse pour obtenir plus de détails sur l'erreur
        return None


def predict_temperature_for_iot(latitude, longitude, start_date, end_date):
    # Utilize latitude and longitude to make temperature predictions
    api_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&past_days=10&hourly=temperature_2m"
    weather_data = get_weather_data(api_url)

    if weather_data:
        df = pd.DataFrame(weather_data['hourly'])
        df.set_index('time', inplace=True)
        df.index = pd.to_datetime(df.index)

        # Filter the DataFrame for the chosen period
        start_date = pd.Timestamp(start_date)  # Convert to Timestamp
        end_date = pd.Timestamp(end_date)  # Convert to Timestamp

        df_interval = df[(df.index >= start_date) & (df.index <= end_date)]

        # Split the data into training and test sets
        X_train, X_test, y_train, y_test = train_test_split(df_interval.index, df_interval['temperature_2m'], test_size=0.2, random_state=42)

        # Make predictions
        predictions = predict_temperature(X_train, y_train, X_test)

        # Visualize the data
        chart_filename = visualize_data(df_interval.index, df_interval['temperature_2m'], predictions)
        return chart_filename
    else:
        print("Unable to retrieve weather data.")

def predict_temperature(X_train, y_train, X_test):
    model = LinearRegression()

    X_train_numeric = (X_train - pd.Timestamp("2000-01-01")) // pd.Timedelta('1s')
    X_train_numeric = X_train_numeric.values.reshape(-1, 1)

    model.fit(X_train_numeric, y_train)

    X_test_numeric = (X_test - pd.Timestamp("2000-01-01")) // pd.Timedelta('1s')
    X_test_numeric = X_test_numeric.values.reshape(-1, 1)

    predictions = model.predict(X_test_numeric)
    return predictions

def visualize_data(dates, actual_temperature, predicted_temperature, filename='static/prediction_chart.png'):
    plt.figure(figsize=(10, 6))

    # Ensure the lengths are consistent
    len_data = min(len(dates), len(actual_temperature), len(predicted_temperature))
    dates = dates[:len_data]
    actual_temperature = actual_temperature[:len_data]
    predicted_temperature = predicted_temperature[:len_data]

    unique_dates = list(set(dates.date))
    unique_dates.sort()

    indices = [i for i, date in enumerate(dates.date) if date in unique_dates]

    plt.plot(dates[indices], actual_temperature[indices], label="Température réelle", marker='o')
    plt.plot(dates[indices], predicted_temperature[indices], label="Prédiction de température", marker='o')

    plt.title('Prédiction de température')
    plt.xlabel('Date')
    plt.ylabel('Température (°C)')
    plt.legend()
    plt.grid(True)

    locator = DayLocator()
    plt.gca().xaxis.set_major_locator(locator)

    plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))

    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the plot as an image file
    plt.savefig(filename)

    # Optionally, you can also clear the figure to release resources
    plt.clf()

    return filename
