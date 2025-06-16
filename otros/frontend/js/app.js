const WS_URL = 'ws://localhost:8000/ws';
const PREFIX_LEN = 5;
let ws;
let currentUser;
let currentConvId;

function connect() {
  ws = new WebSocket(WS_URL);
  ws.onopen = () => console.log('WebSocket conectado');
  ws.onmessage = ({ data }) => handleResponse(data);
  ws.onerror = e => console.error('WS Error:', e);
}

function sendTx(service, payload) {
  return new Promise((resolve, reject) => {
    const body = service + payload;
    const prefix = String(body.length).padStart(PREFIX_LEN, '0');
    ws.send(prefix + body);
    ws.addEventListener('message', function handler(evt) {
      const msg = evt.data;
      ws.removeEventListener('message', handler);
      resolve(msg);
    });
  });
}

function parseMsg(msg) {
  const length = parseInt(msg.slice(0, PREFIX_LEN));
  const serv = msg.slice(PREFIX_LEN, PREFIX_LEN+5);
  const rest = msg.slice(PREFIX_LEN+5);
  return { serv, rest };
}

async function login(email, pass) {
  const resp = await sendTx('USLOG', `${email};${pass}`);
  const { serv, rest } = parseMsg(resp);
  if (rest.startsWith('OK')) {
    const [id, name] = rest.split(':')[1].split(';');
    currentUser = { id, name };
    showProfile();
  } else alert('Error: ' + rest);
}

async function register(name, email, pass) {
  const resp = await sendTx('USREG', `${name};${email};${pass}`);
  const { rest } = parseMsg(resp);
  if (rest.startsWith('OK')) alert('Registrado con ID ' + rest.split(':')[1]);
  else alert('Error: ' + rest);
}

async function loadProfile() {
  const resp = await sendTx('USGET', currentUser.id);
  const { rest } = parseMsg(resp);
  if (rest.startsWith('OK')) {
    const data = rest.split(':')[1].split(';');
    document.getElementById('profile-info').innerText =
      `ID: ${data[0]}\nUsuario: ${data[1]}\nEmail: ${data[2]}\nReputación: ${data[3]}`;
  }
}

async function loadPosts() {
  const resp = await sendTx('PBLST', 'oferta;');
  const { rest } = parseMsg(resp);
  if (rest.startsWith('OK')) {
    const list = rest.slice(3).split('|');
    const container = document.getElementById('posts-list');
    container.innerHTML = '';
    list.forEach(item => {
      if (!item) return;
      const parts = item.split(';');
      const card = document.createElement('div'); card.className = 'card';
      card.innerHTML = `<strong>${parts[2]}</strong><br>${parts[3]}`;
      container.appendChild(card);
    });
  }
}

// Eventos de formularios
window.onload = () => {
  connect();
  document.getElementById('login-form').onsubmit = e => {
    e.preventDefault();
    login(
      e.target['login-email'].value,
      e.target['login-pass'].value
    );
  };
  document.getElementById('register-form').onsubmit = e => {
    e.preventDefault();
    register(
      e.target['reg-name'].value,
      e.target['reg-email'].value,
      e.target['reg-pass'].value
    );
  };
  document.getElementById('logout-btn').onclick = () => location.reload();
};

// Navegación básica entre secciones
function showProfile() {
  ['auth'].forEach(i => document.getElementById(i).classList.add('hidden'));
  ['profile','posts','chat','notifications'].forEach(i => document.getElementById(i).classList.remove('hidden'));
  loadProfile();
  loadPosts();
}