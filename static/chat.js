const params = new URLSearchParams(location.search);

const username = params.get("user");

const ws = new WebSocket(
    `ws://${location.host}/ws/${username}`
);

const messages = document.getElementById("messages");

function addMessage(text){

    let div=document.createElement("div");

    div.innerHTML=text;

    messages.appendChild(div);

    saveHistory(text);
}

ws.onmessage = (event)=>{

    let data=JSON.parse(event.data);

    if(data.type==="chat"){

        addMessage(
          `<b>${data.user}</b>: ${data.msg}`
        );
    }

    if(data.type==="system"){

        addMessage(
           `[系统] ${data.msg}`
        );
    }

    if(data.type==="users"){

        document.getElementById("users").innerHTML=
            "在线用户："+data.users.join(",");
    }

    if(data.type==="error"){
        alert(data.msg);
    }
};

function sendMsg(){

    let msg=document.getElementById("msg").value;

    ws.send(
        JSON.stringify({
            msg:msg
        })
    );

    document.getElementById("msg").value="";
}