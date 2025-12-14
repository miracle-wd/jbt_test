const API = "http://127.0.0.1:8000";

function show(x){ document.getElementById("out").textContent = JSON.stringify(x, null, 2); }

async function register(){
  const username = document.getElementById("r_user").value;
  const password = document.getElementById("r_pass").value;
  const res = await fetch(`${API}/register`, {
    method:"POST",
    headers:{ "Content-Type":"application/json" },
    body: JSON.stringify({username, password})
  });
  show({status: res.status, body: await res.json()});
}

async function login(){
  const username = document.getElementById("l_user").value;
  const password = document.getElementById("l_pass").value;
  const res = await fetch(`${API}/login`, {
    method:"POST",
    headers:{ "Content-Type":"application/json" },
    body: JSON.stringify({username, password})
  });
  show({status: res.status, body: await res.json()});
}
