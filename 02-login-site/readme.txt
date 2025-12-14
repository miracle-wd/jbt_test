cd E:\jbt_ans\02-login-site\backend
uvicorn app:app --host 127.0.0.1 --port 8000

cd E:\jbt_ans\02-login-site\frontend
python -m http.server 5173
http://127.0.0.1:5173/