@echo off
echo ====================================
echo  FS25 Farming Dashboard - Uruchamianie
echo ====================================
echo.
pip install -r requirements.txt
echo.
echo Uruchamianie serwera na http://localhost:9988
echo Nacisnij Ctrl+C aby zatrzymac.
echo.
python main.py
pause
