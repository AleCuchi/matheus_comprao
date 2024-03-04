echo teste
git reset --hard HEAD
git pull
call .\.venv\Scripts\activate
python ./busca_compras.py

pause