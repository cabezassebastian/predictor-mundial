@echo off
title Predictor Mundial 2026 - Iniciando Servidor
color 0B
echo.
echo ===================================================
echo     INICIANDO INTERFAZ GRAFICA DEL MUNDIAL 2026    
echo ===================================================
echo.
echo El servidor local se esta encendiendo...
echo Tu navegador predeterminado se abrira automaticamente en unos segundos.
echo.
echo (Para apagar el programa, simplemente cierra esta ventana negra)
echo.
cd /d "C:\Users\user\Desktop\Mundial"
python -m streamlit run app_streamlit.py --server.address 127.0.0.1 --server.enableCORS false --server.enableXsrfProtection false
pause
