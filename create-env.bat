set PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312;%PATH%
python -m venv sandag
call sandag\Scripts\activate
pip install -r requirements.txt
pip list
deactivate
pause
