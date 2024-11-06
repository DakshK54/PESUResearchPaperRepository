async function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    const response = await fetch('http://localhost:3000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });

    const data = await response.json();
    if (response.ok) {
        localStorage.setItem('token', data.token);
        loadPapers();
    } else {
        alert("Login failed!");
    }
}

async function loadPapers() {
    const response = await fetch('http://localhost:3000/api/papers', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    
    const papers = await response.json();
    const paperList = document.getElementById('papers');
    paperList.innerHTML = papers.map(paper => `<p>${paper.title}</p>`).join('');
}