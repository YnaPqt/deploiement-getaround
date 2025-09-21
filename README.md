
![2bd4cdf9-37f2-497f-9096-c2793296a75f-1568844229943](https://github.com/user-attachments/assets/9e841707-2257-46fc-94b4-229d9a349016)

# GetAround 
GetAround is a car-sharing platform that allows individuals to rent cars from private owners for periods ranging from a few hours to several days. The company has experienced rapid growth, counting over 5 million users and approximately 20,000 cars worldwide as of 2019.

As part of this project, participants are expected to conduct data analysis and build machine learning services to support GetAround’s business decisions.

# 📌 Context

Getaround, often referred to as the “Airbnb for cars,” allows users to rent a vehicle for a few hours or several days.
However, late car returns create friction for subsequent customers.
Therefore, Getaround aims to:

Assess a safety buffer between two rentals to reduce conflicts.

Propose a rental price optimization using Data Science.

# 🎯 Business Objectives

Study the impact of delays on customer satisfaction and cancellations.

Simulate a minimum gap between two bookings.

Provide recommendations to the product team.

Predict an optimal daily rental price.

# 🛠️ Technical Objectives

Perform an exploratory data analysis (EDA).

Train a regression model to predict prices.

Develop a REST API with FastAPI.

Create an interactive dashboard with Streamlit.

Deploy the entire solution with Docker on Hugging Face Spaces.

# 📊 Exploratory Analysis
File: get_around_delay_analysis.xlsx

Analysis of delays (early returns, on-time, late).

Impact of delays on the next booking.

Check-in type (mobile/manual), average delay duration.

Determination of delay thresholds.

# 🤖 Machine Learning Model Selection

Type: Regression model and decision trees.

Target variable: rental_price_per_day.

Features: car_type, engine_power, fuel, mileage, connect, etc.

Integration with a FastAPI endpoint.

# 🧱 Project Architecture

The project is structured around the following components:

Analysis: Jupyter Notebook for data analysis.

Dashboard: Web interface developed with Streamlit for interactive exploration of results.

API: Built with FastAPI for production inference.

Deployment: Containerization of the API with Docker for maximum portability and reliability.


# Tools / Services
- [API FastAPI](https://yona-p-getaround-api.hf.space) : Service for predicting the rental price 
  
- [API Documents](https://yona-p-getaround-api.hf.space/docs)	: API documentation for test endpoint /predict 
  
- [Dashboard Streamlit](https://yona-p-getaround-dashboard.hf.space) : Analyse EDA + Prédiction prix d'une location
