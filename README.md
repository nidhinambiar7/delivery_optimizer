# delivery_optimizer

![Python](https://img.shields.io/badge/python-v3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Flask](https://img.shields.io/badge/flask-2.0+-red.svg)

An intelligent delivery route optimization system that minimizes travel distance while prioritizing time-sensitive deliveries. Built with Flask and OpenRouteService API for real-world routing accuracy using actual road networks rather than straight-line distances.

## 🚀 Features

* **Smart Route Optimization** - Uses real road distances via OpenRouteService API
* **Priority-Based Delivery** - Automatically prioritizes perishable items for early delivery
* **Interactive Visualization** - Generate detailed route maps with Folium
* **Multiple Algorithm Strategies**:
  * Exhaustive search for small delivery sets
  * Intelligent nearest-neighbor with priority penalties
  * 2-Opt local search optimization for route refinement
* **Scalable Architecture** - Handles varying delivery volumes efficiently

## 📋 Requirements

* Python 3.7 or higher
* OpenRouteService API key ([free tier available](https://openrouteservice.org/))
* Modern web browser for map visualization

## 🛠 Installation

1. **Clone the repository:**
```bash
git clone https://github.com/nidhinambiar7/delivery_optimizer.git
cd delivery_optimizer
```

2. **Create and activate a virtual environment (recommended):**
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
Create a `.env` file in the project root:
```ini
ORS_API_KEY=your_openrouteservice_api_key_here
```

## 🚀 Usage

1. **Start the Flask development server:**
```bash
python app.py
```

2. **Access the application:**
Open your browser and navigate to `http://127.0.0.1:5000`

3. **Input your delivery locations:**
   * Set your starting point (depot/warehouse)
   * Add delivery addresses
   * Mark perishable items for priority handling

4. **Get optimized route:**
   * View the calculated optimal route
   * See total distance and estimated time
   * Download interactive map for driver use

## 📊 Optimization Example

**Input Scenario:**
* **Starting Point:** HSR Layout, Bangalore
* **Perishable Deliveries:** Electronic City, Silk Board, Whitefield
* **Standard Deliveries:** Marathahalli, Central Bangalore

**Optimized Output:**
* Route prioritizes perishable deliveries in first half
* Total distance: ~43.09 km
* Estimated time savings: 15-20% vs. unoptimized route
* Interactive map with turn-by-turn directions

## ⚙️ Technologies Used

* **Backend:** Python, Flask
* **Routing API:** OpenRouteService
* **Visualization:** Folium (interactive maps)
* **Frontend:** HTML5, CSS3, JavaScript
* **Environment:** Python virtual environment

## 📁 Project Structure

```
delivery_optimizer/
├── app.py                 # Main Flask application
├── templates/
│   ├── base.html         # Base template
│   └── index.html        # Main interface
├── static/
│   └── css/
│       └── main.css      # Styling
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (not committed)
├── .gitignore           # Git ignore rules
├── README.md            # This file
└── LICENSE              # MIT License
```

## 🔧 Configuration

### API Setup
1. Visit [OpenRouteService](https://openrouteservice.org/)
2. Create a free account
3. Generate an API key
4. Add the key to your `.env` file

### Rate Limits
* Free tier: 2,000 requests/day
* Each route optimization uses 1 request per location pair
* Consider upgrading for high-volume usage

## 🐛 Troubleshooting

**Common Issues:**

* **API Key Error:** Ensure your OpenRouteService API key is valid and properly set in `.env`
* **Route Not Found:** Check that all addresses are valid and accessible by road
* **Slow Performance:** Large delivery sets (>10 locations) may take longer to optimize

**Performance Tips:**
* Use specific addresses rather than general area names
* Batch similar deliveries in the same geographic area
* Consider breaking large delivery sets into smaller optimized groups

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

* [OpenRouteService](https://openrouteservice.org/) - For providing the routing API
* [Folium](https://python-visualization.github.io/folium/) - For interactive map visualization
* [Flask](https://flask.palletsprojects.com/) - For the web framework
* The open-source community for continuous inspiration and support

## 📞 Support

For issues, questions, or feature requests, please:
* Open an issue on [GitHub Issues](https://github.com/nidhinambiar7/delivery_optimizer/issues)
* Check existing issues before creating new ones
* Provide detailed information for bug reports

---

**Built with ❤️ for efficient delivery logistics**
