# black-scholes-opm
A containerized web application that helps traders identify mispriced options using the Black-Scholes Option Pricing Model.

Features
	•	Calculates theoretical option prices using Black-Scholes
	•	Identifies trading edges by comparing market prices to theoretical values
	•	Provides clear buy/sell recommendations based on price differences
	•	Formats option details for easy Robinhood order placement
Tech Stack
	•	Python 3.12
	•	Flask 3.0.2
	•	NumPy/SciPy for calculations
	•	Docker for containerization
Quick Start
docker build -t options-calculator .
docker run -p 8080:8080 options-calculator

Access at http://localhost:8080

Directory
options-calculator/
│
├── templates/
│   └── index.html
│
├── app.py
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
