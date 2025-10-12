# 🛩️ Aerial Simulator in Python

A Python-based Aerial Simulator with a **Tkinter GUI** to calculate mission success probabilities based on aircraft stats, mission type, weather, and distance. The simulator also displays aircraft images and detailed statistics.

---

## 🚀 Features

- Select **Country**, **Aircraft**, **Mission**, **Weather**, and **Distance**.
- Calculates **mission success probability**.
- Special calculations for **BVR Combat** and **Strategic Reconnaissance**.
- Auto-updates **compatible aircraft** for each mission.
- Displays **aircraft images** and **statistics** in real-time.
- User-friendly GUI for easy navigation.

---

## 🎬 Demo

![Simulator Demo](img/demo.gif)  
*Example of the simulator interface showing selection of aircraft, mission, weather, and probability calculation.*

---

## 🛠️ Prerequisites

- **Python 3.10+**
- Python libraries:
  - `tkinter` (usually included)
  - `pandas`
  - `Pillow`  

Install required libraries:

```bash
pip install pandas pillow


aerial-simulator/
│
├─ img/                  # Aircraft images (e.g., f22.png, f35a.png) + demo.gif
├─ simulator.py          # Main Python file
├─ README.md             # This file


python simulator.py

📄 License

This project is licensed under the MIT License
