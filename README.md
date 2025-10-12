# 🛩️ Aerial Simulator in Python

![Python Version](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A Python-based **Aerial Simulator** with a **Tkinter GUI** to calculate mission success probabilities based on aircraft stats, mission type, weather, and distance. The simulator also displays aircraft images and detailed statistics.

---

## 🚀 Features

- Select **Country**, **Aircraft**, **Mission**, **Weather**, and **Distance**
- Calculates **mission success probability**
- Special calculations for **BVR Combat** and **Strategic Reconnaissance**
- Auto-updates **compatible aircraft** for each mission
- Displays **aircraft images** and **statistics** in real-time
- User-friendly GUI for easy navigation

---

## 🎮 Usage Instructions

1. **Select the country** of the aircraft
2. **Choose a mission**
3. **Select an aircraft** compatible with that mission
4. Pick **weather** and **distance**
5. Click **"Calculate Probability"**
6. View **mission result**, **aircraft image**, and **statistics**

---

## ⚠️ Notes

- Missing aircraft images in `img/` will display **"Image not found"**
- Mission types **Reconnaissance** and **BVR Combat** use special calculations factoring **stealth, radar, RCS, range, speed, and maneuverability**
- 
---

## 🤝 Contributing

1. Fork the repository
2. Create a branch: `git checkout -b feature/new-feature`
3. Commit your changes: `git commit -m 'Add new feature'`
4. Push to the branch: `git push origin feature/new-feature`
5. Open a Pull Request

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
```

---

!([img.](https://images.steamusercontent.com/ugc/919166841047493933/D2DCF4AAD98BCFCB84A00A082E299B5C698C2A25/?imw=5000&imh=5000&ima=fit&impolicy=Letterbox&imcolor=%23000000&letterbox=false))
