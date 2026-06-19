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
        
        // 处理不同消息类型
        if (data.type === 'error') {
          loginError.innerText = data.msg || data.detail || '连接错误';
          ws.close();
        } 
        else if (data.type === 'system') {
          addMessage(data.msg, 'system');
        } 
        else if (data.type === 'user_list') {
          updateUsers(data.users || []);
        } 
        else if (data.type === 'login') {
          addMessage(`[${data.username}] ${data.content}`, 'system');
          if (data.users) updateUsers(data.users);
        } 
        else if (data.type === 'logout') {
          addMessage(`[${data.username}] ${data.content}`, 'system');
          if (data.users) updateUsers(data.users);
        } 
        else if (data.type === 'message') {
          addMessage(`${data.username}: ${data.content}`, 'chat');
        }
        else if (data.type === 'private_message') {
          addMessage(`[私聊] ${data.username}: ${data.content}`, 'private');
        }
        else if (data.type === 'typing') {
          // 显示输入指示器
          addMessage(`${data.username} 正在输入...`, 'typing');
        }
        else if (data.type === 'pong') {
          // 心跳响应，不显示
          console.log('收到心跳响应');
        }
        else {
          // 其他消息类型
          addMessage(JSON.stringify(data));
        }
      } catch (e) {
        // 非 JSON 或其他错误
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
    
    // 发送消息，必须包含 type 字段
    ws.send(JSON.stringify({ 
      type: "message",
      content: msg 
    }));
    
    messageInput.value = '';
  });
})();
