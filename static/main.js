(() => {
  const loginEl = document.getElementById('login');
  const chatEl = document.getElementById('chat');
  const joinBtn = document.getElementById('joinBtn');
  const usernameInput = document.getElementById('username');
  const loginError = document.getElementById('loginError');
  const usersList = document.getElementById('users');
  const messagesEl = document.getElementById('messages');
  const sendForm = document.getElementById('sendForm');
  const messageInput = document.getElementById('messageInput');

  let ws = null;
  let username = null;

  function addMessage(text, cls = '') {
    const div = document.createElement('div');
    div.className = 'message ' + cls;
    div.innerText = text;
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function updateUsers(users) {
    usersList.innerHTML = '';
    users.forEach(u => {
      const li = document.createElement('li');
      li.innerText = u;
      usersList.appendChild(li);
    });
  }

  joinBtn.addEventListener('click', () => {
    const name = usernameInput.value.trim();
    if (!name) {
      loginError.innerText = '请输入用户名';
      return;
    }
    username = name;
    connectWS(name);
  });

  function connectWS(name) {
    ws = new WebSocket((location.protocol === 'https:' ? 'wss' : 'ws') + '://' + location.host + '/ws/' + encodeURIComponent(name));

    ws.addEventListener('open', () => {
      loginEl.classList.add('hidden');
      chatEl.classList.remove('hidden');
      loginError.innerText = '';
      addMessage('已连接到服务器', 'system');
    });

    ws.addEventListener('message', (ev) => {
      try {
        const data = JSON.parse(ev.data);
        if (data.type === 'error') {
          loginError.innerText = data.msg || '连接错误';
          ws.close();
        } else if (data.type === 'system') {
          addMessage(data.msg, 'system');
        } else if (data.type === 'users') {
          updateUsers(data.users || []);
        } else if (data.type === 'chat') {
          addMessage(`${data.user}: ${data.msg}`, 'chat');
        } else {
          // other types
          addMessage(JSON.stringify(data));
        }
      } catch (e) {
        // non-JSON or fallback
        addMessage(ev.data);
      }
    });

    ws.addEventListener('close', () => {
      addMessage('已断开连接', 'system');
      chatEl.classList.add('hidden');
      loginEl.classList.remove('hidden');
    });

    ws.addEventListener('error', () => {
      addMessage('连接发生错误', 'system');
    });
  }

  sendForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const msg = messageInput.value.trim();
    if (!msg || !ws || ws.readyState !== WebSocket.OPEN) return;
    ws.send(JSON.stringify({ msg }));
    messageInput.value = '';
  });
})();