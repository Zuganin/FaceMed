# Coursework 2024-2025 HSE
## Install
Clone the repository 
```bash
git clone https://github.com/Zuganin/FaceMed.git
cd FaceMed
```
2. Downland model "Yolo_train_best.pt" https://disk.yandex.ru/d/Snr4azlMXkMaqQ

3. Move file .pt to folder FaceMed (in manual or using bash) \\
```bash
mv ~/YOUR_PATH/Yolo_train_best.pt ~/YOUR_PATH/FaceMed/
```
4. Create vitrual environment and install requirements
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
5. Run main.py
```bash
python3 main.py
```
6. Run Telegram and search @FaceMedBot. It`s all.