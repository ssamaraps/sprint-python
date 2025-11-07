<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<title>Assistente Virtual HC</title>
<style>
body { font-family: Arial; margin: 20px; background: #f9f9f9; }
.container { max-width: 900px; margin: auto; background: #fff; padding: 20px; box-shadow: 0 0 10px #ccc; }
input, button, textarea { margin: 5px 0; padding: 8px; font-size: 14px; }
button { cursor: pointer; margin-right: 5px; }
table { border-collapse: collapse; width: 100%; margin-top: 10px; }
table, th, td { border: 1px solid #ccc; }
th, td { padding: 8px; text-align: left; }
.obs-container { margin-top: 20px; border-top: 1px solid #ccc; padding-top: 10px; }
.note { border: 1px solid #ddd; padding: 8px; margin: 5px 0; background: #f8f8f8; }
.lembrete { color: green; font-weight: bold; margin: 5px 0; }
.card-title { font-weight: bold; }
.btn-secondary { background: #eee; border: 1px solid #ccc; padding: 4px 8px; cursor: pointer; }
.toast {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: #4CAF50;
  color: white;
  padding: 12px 18px;
  border-radius: 8px;
  opacity: 0.95;
  z-index: 9999;
  animation: fadeIn 0.3s ease;
  box-shadow: 0 0 10px rgba(0,0,0,0.2);
}
@keyframes fadeIn {
  from {opacity: 0; transform: translateY(20px);}
  to {opacity: 1; transform: translateY(0);}
}
.msg-consulta-dia { background: #fffae5; border: 1px solid #f0c36d; padding: 10px; margin: 10px 0; font-weight: bold; color: #a46a00; }
.alerta-fixo {
  position: fixed;
  bottom: 80px;
  right: 20px;
  background: #ff5555;
  color: white;
  padding: 14px 20px;
  border-radius: 10px;
  font-weight: bold;
  box-shadow: 0 0 10px rgba(0,0,0,0.3);
  z-index: 9999;
}
</style>
</head>
<body>
<div class="container">
<h1>Assistente Virtual HC - Paciente</h1>
<label>Digite seu CPF:</label>
<input type="text" id="cpfInput" placeholder="Digite apenas números">
<button onclick="buscarConsultas()">Buscar Consultas</button>

<div id="mensagensDia"></div>
<div id="consultasContainer"></div>
<div id="observacoesContainer" class="obs-container"></div>
<div id="lembretesContainer"></div>
</div>

<script>
// =========================
// URL da API no Render
// =========================
const API_URL = "https://sprint-python-7.onrender.com";

let lembretes = [];
let notificacoesDisparadas = {};
let alertaFixo = null;

// =========================
// Funções auxiliares
// =========================
function formatarDataLocal(dataStr) {
  const [datePart, timePart] = dataStr.split(" ");
  const [year, month, day] = datePart.split("-");
  const [hour, min, sec] = timePart.split(":");
  const dateObj = new Date(year, month - 1, day, hour, min, sec);
  return dateObj.toLocaleString();
}

function escapeHtml(text) {
  return text.replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
}

function mostrarToast(msg, cor="#4CAF50") {
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.style.background = cor;
  toast.innerText = msg;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}

// =========================
// Consultas
// =========================
async function buscarConsultas() {
  const cpf = document.getElementById("cpfInput").value.trim();
  if (!cpf) return alert("Digite o CPF!");

  const res = await fetch(`${API_URL}/consultas/${cpf}`);
  const consultas = await res.json();

  const mensagensDia = document.getElementById("mensagensDia");
  mensagensDia.innerHTML = "";

  let html = "<h2>Próximas Consultas</h2>";
  if (consultas.length === 0) html += "<p>📭 Nenhuma consulta encontrada.</p>";
  else {
    html += `<table>
      <tr><th>ID</th><th>Data/Hora</th><th>Médico</th><th>Status</th><th>Ações</th></tr>`;
    const agora = new Date();

    consultas.forEach(c => {
      const dataObj = new Date(c.data.replace(" ", "T"));
      const isHoje = dataObj.toDateString() === agora.toDateString();

      if (isHoje) {
        mensagensDia.innerHTML += `<div class="msg-consulta-dia">
          Hoje você tem consulta às ${dataObj.toLocaleTimeString()} com ${c.medico}.
        </div>`;
      }

      const podeAlterar = dataObj > agora;
      html += `<tr>
        <td>${c.id}</td>
        <td class="card-title">${formatarDataLocal(c.data)}</td>
        <td>${c.medico}</td>
        <td>${c.status}</td>
        <td>
          <button ${podeAlterar ? "" : "disabled"} onclick="confirmarConsulta('${cpf}', ${c.id})">Confirmar</button>
          <button ${podeAlterar ? "" : "disabled"} onclick="cancelarConsulta('${cpf}', ${c.id})">Cancelar</button>
          <button onclick="mostrarObservacoes('${cpf}', ${c.id})">Observações</button>
          <button onclick="adicionarLembrete('${cpf}', ${c.id}, '${c.data}')">Adicionar Lembrete</button>
          <button onclick="entrarNaConsulta(${c.id})">Entrar na Consulta</button>
        </td>
      </tr>`;
    });
    html += `</table>`;
  }

  document.getElementById("consultasContainer").innerHTML = html;
}

// =========================
// Confirmar / Cancelar
// =========================
async function confirmarConsulta(cpf, id) {
  await fetch(`${API_URL}/consultas/confirmar`, {
    method: "POST",
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({cpf, id_consulta: id})
  });
  mostrarToast("✅ Consulta confirmada com sucesso!");
  buscarConsultas();
}

async function cancelarConsulta(cpf, id) {
  await fetch(`${API_URL}/consultas/cancelar`, {
    method: "POST",
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({cpf, id_consulta: id})
  });
  mostrarToast("❌ Consulta cancelada.", "#d9534f");
  buscarConsultas();
}

// =========================
// Observações (mantidas)
// =========================

// =========================
// Lembretes + Alerta fixo
// =========================
function adicionarLembrete(cpf, id_consulta, dataStr) {
  const [datePart, timePart] = dataStr.split(" ");
  const [year, month, day] = datePart.split("-");
  const [hour, min, sec] = timePart.split(":");
  const consultaDate = new Date(year, month - 1, day, hour, min, sec);

  const index = lembretes.findIndex(l => l.id_consulta === id_consulta);
  if (index >= 0) lembretes[index].consultaDate = consultaDate;
  else lembretes.push({ id_consulta, consultaDate, cpf });

  notificacoesDisparadas[id_consulta] = false;
  mostrarToast("🔔 Lembrete adicionado!");
  atualizarLembretes();
}

function atualizarLembretes() {
  const container = document.getElementById("lembretesContainer");
  container.innerHTML = "";
  const agora = new Date();

  lembretes.forEach(l => {
    const diff = l.consultaDate - agora;
    if (diff <= 0) {
      if (alertaFixo && alertaFixo.id_consulta === l.id_consulta) {
        alertaFixo.remove();
        alertaFixo = null;
      }
      return;
    }

    const minFaltando = Math.floor(diff / 60000);
    const segFaltando = Math.floor((diff % 60000) / 1000);
    let alerta = "";

    if (diff <= 10 * 60 * 1000) {
      alerta = ` — ⏰ <b>Faltam menos de 10 minutos!</b>`;
      if (!alertaFixo || alertaFixo.id_consulta !== l.id_consulta) {
        alertaFixo = document.createElement("div");
        alertaFixo.className = "alerta-fixo";
        alertaFixo.id_consulta = l.id_consulta;
        alertaFixo.innerText = `🚨 Falta menos de 10 minutos para sua consulta #${l.id_consulta}!`;
        document.body.appendChild(alertaFixo);
      }
    }

    container.innerHTML += `
      <div class="lembrete">
        Consulta #${l.id_consulta} — ${l.consultaDate.toLocaleDateString()} ${l.consultaDate.toLocaleTimeString()}
        — Tempo restante: ${minFaltando}m ${segFaltando}s${alerta}
      </div>`;

    if (diff <= 10 * 60 * 1000 && !notificacoesDisparadas[l.id_consulta]) {
      dispararNotificacao("Consulta em breve!", `Faltam menos de 10 minutos para sua consulta #${l.id_consulta}`);
      notificacoesDisparadas[l.id_consulta] = true;
    }
  });
}

function dispararNotificacao(title, body) {
  if (!("Notification" in window)) return;
  if (Notification.permission === "granted") {
    new Notification(title, { body });
  } else if (Notification.permission !== "denied") {
    Notification.requestPermission().then(p => {
      if (p === "granted") new Notification(title, { body });
    });
  }
}

function entrarNaConsulta(id_consulta) {
  const win = window.open("", "_blank");
  win.document.write(`<h2>Consulta #${id_consulta}</h2><p>Simulação de chamada online</p>`);
}

setInterval(atualizarLembretes, 1000);
</script>
</body>
</html>
