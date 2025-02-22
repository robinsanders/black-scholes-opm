from flask import Flask, render_template, request
import numpy as np
from scipy.stats import norm
from typing import Optional
from dataclasses import dataclass
from datetime import datetime

app = Flask(__name__)

@dataclass
class OptionResult:
    bs_price: float
    edge: float
    symbol: str
    expiry_date: str
    recommendation: str
    option_type: str  # Added to distinguish between call and put

def black_scholes_call(S: float, K: float, sigma: float, r: float, t: float) -> float:
    """
    Calculate Black-Scholes price for a call option
    
    Parameters:
    S (float): Spot price
    K (float): Strike price
    sigma (float): Volatility
    r (float): Risk-free rate
    t (float): Time to expiry in years
    """
    try:
        d1 = (np.log(S/K) + (r + sigma**2/2)*t) / (sigma*np.sqrt(t))
        d2 = d1 - sigma*np.sqrt(t)
        
        call_price = S*norm.cdf(d1) - K*np.exp(-r*t)*norm.cdf(d2)
        return call_price
    except Exception as e:
        app.logger.error(f"Error in Black-Scholes calculation: {e}")
        raise ValueError("Invalid input parameters for Black-Scholes calculation")

def black_scholes_put(S: float, K: float, sigma: float, r: float, t: float) -> float:
    """
    Calculate Black-Scholes price for a put option
    
    Parameters:
    S (float): Spot price
    K (float): Strike price
    sigma (float): Volatility
    r (float): Risk-free rate
    t (float): Time to expiry in years
    """
    try:
        d1 = (np.log(S/K) + (r + sigma**2/2)*t) / (sigma*np.sqrt(t))
        d2 = d1 - sigma*np.sqrt(t)
        
        put_price = K*np.exp(-r*t)*norm.cdf(-d2) - S*norm.cdf(-d1)
        return put_price
    except Exception as e:
        app.logger.error(f"Error in Black-Scholes calculation: {e}")
        raise ValueError("Invalid input parameters for Black-Scholes calculation")

def get_trading_recommendation(edge: float) -> str:
    """Determine trading recommendation based on edge"""
    if edge < -0.10:  # More than 10 cents undervalued
        return "Strong Buy"
    elif edge < 0:
        return "Consider Buy"
    elif edge > 0.10:  # More than 10 cents overvalued
        return "Strong Sell"
    elif edge > 0:
        return "Consider Sell"
    return "Neutral"

@app.route('/', methods=['GET', 'POST'])
def index():
    result: Optional[OptionResult] = None
    error_message: Optional[str] = None
    
    if request.method == 'POST':
        try:
            # Input validation
            required_fields = ['spot_price', 'strike_price', 'volatility', 
                             'risk_free_rate', 'time_to_expiry', 'market_price',
                             'option_type']  # Added option_type
            
            if not all(field in request.form for field in required_fields):
                raise ValueError("All fields are required")
            
            # Parse and validate inputs
            S = float(request.form['spot_price'])
            K = float(request.form['strike_price'])
            sigma = float(request.form['volatility'])/100
            r = float(request.form['risk_free_rate'])/100
            t = float(request.form['time_to_expiry'])/365
            market_price = float(request.form['market_price'])
            option_type = request.form['option_type'].lower()
            
            # Validate numerical inputs
            if any(x <= 0 for x in [S, K, sigma, t]):
                raise ValueError("Prices, volatility, and time must be positive")
            
            # Calculate BS price based on option type
            if option_type == 'call':
                bs_price = black_scholes_call(S, K, sigma, r, t)
            elif option_type == 'put':
                bs_price = black_scholes_put(S, K, sigma, r, t)
            else:
                raise ValueError("Invalid option type. Must be 'call' or 'put'")
            
            edge = market_price - bs_price
            
            result = OptionResult(
                bs_price=round(bs_price, 2),
                edge=round(edge, 2),
                symbol=request.form['symbol'].upper(),
                expiry_date=request.form['expiry_date'],
                recommendation=get_trading_recommendation(edge),
                option_type=option_type.capitalize()
            )
            
        except ValueError as e:
            error_message = str(e)
        except Exception as e:
            error_message = "An unexpected error occurred"
            app.logger.error(f"Calculation error: {e}")
    
    return render_template('index.html', result=result, error=error_message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
