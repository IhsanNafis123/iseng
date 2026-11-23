const vscode = require("vscode");

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
  console.log("GhostGPT Code ekstensi diaktifkan");

  context.subscriptions.push(
    vscode.commands.registerCommand("ghostgpt-code.setApiKey", setApiKey)
  );
  context.subscriptions.push(
    vscode.commands.registerCommand("ghostgpt-code.generateCode", generateCode)
  );
  context.subscriptions.push(
    vscode.commands.registerCommand("ghostgpt-code.chat", chat)
  );
}

function deactivate() {}

async function setApiKey() {
  const key = await vscode.window.showInputBox({
    prompt: "Masukkan GhostGPT API Key (SK-...)",
    password: true,
    placeHolder: "SK-xxxx",
  });
  if (key) {
    await vscode.workspace
      .getConfiguration("ghostgpt-code")
      .update("apiKey", key, vscode.ConfigurationTarget.Global);
    vscode.window.showInformationMessage("API Key GhostGPT tersimpan.");
  }
}

function getConfig() {
  const cfg = vscode.workspace.getConfiguration("ghostgpt-code");
  return {
    apiKey: cfg.get("apiKey", ""),
    baseUrl: cfg.get("baseUrl", "https://api.ghostgpt.io/v1"),
    model: cfg.get("model", "ghostgpt"),
    temperature: cfg.get("temperature", 0.7),
  };
}
async function generateCode() {
  const cfg = getConfig();
  if (!cfg.apiKey || cfg.apiKey === "SK-YOUR-KEY") {
    const set = await vscode.window.showWarningMessage(
      "API Key GhostGPT belum diatur. Setel sekarang?",
      "Setel API Key",
      "Batal"
    );
    if (set === "Setel API Key") {
      await setApiKey();
    }
    return;
  }

  const deskripsi = await vscode.window.showInputBox({
    prompt: "Deskripsi kode yang ingin Anda buat",
    placeHolder: "Contoh: buat website sederhana dengan HTML dan CSS",
  });
  if (!deskripsi) return;

  vscode.window.withProgress(
    {
      location: vscode.ProgressLocation.Notification,
      title: "GhostGPT Code",
      cancellable: false,
    },
    async (progress) => {
      progress.report({ message: "Menggenerate kode..." });
      try {
        const kode = await panggilGhostGPT(cfg, deskripsi, true);
        const fileUri = await simpanKeFile(cfg, deskripsi, kode);
        vscode.window.showInformationMessage(
          `Kode disimpan ke ${fileUri.fsPath}`
        );
        const buka = await vscode.window.showInformationMessage(
          "Buka file hasil generate di VS Code?",
          "Buka"
        );
        if (buka === "Buka") {
          const doc = await vscode.workspace.openTextDocument(fileUri);
          await vscode.window.showTextDocument(doc);
        }
      } catch (err) {
        vscode.window.showErrorMessage(`Gagal generate kode: ${err.message}`);
      }
    }
  );
}

async function chat() {
  const cfg = getConfig();
  if (!cfg.apiKey || cfg.apiKey === "SK-YOUR-KEY") {
    const set = await vscode.window.showWarningMessage(
      "API Key GhostGPT belum diatur. Setel sekarang?",
      "Setel API Key",
      "Batal"
    );
    if (set === "Setel API Key") {
      await setApiKey();
    }
    return;
  }

  const pesan = await vscode.window.showInputBox({
    prompt: "Ketik pesan untuk GhostGPT",
    placeHolder: "Tulis pertanyaan atau permintaan kode di sini...",
  });
  if (!pesan) return;

  vscode.window.withProgress(
    {
      location: vscode.ProgressLocation.Notification,
      title: "GhostGPT Chat",
      cancellable: false,
    },
    async (progress) => {
      progress.report({ message: "Mengirim pesan..." });
      try {
        const balasan = await panggilGhostGPT(cfg, pesan, false);
        const panel = vscode.window.createOutputChannel("GhostGPT Chat");
        panel.appendLine(`Anda: ${pesan}`);
        panel.appendLine(`GhostGPT: ${balasan}`);
        panel.appendLine("".padEnd(60, "-"));
        panel.show();
      } catch (err) {
        vscode.window.showErrorMessage(`Gagal chat: ${err.message}`);
      }
    }
  );
}

async function panggilGhostGPT(cfg, userText, kodeLengkap) {
  const systemPrompt =
    "Kamu adalah asisten coding yang ahli. Berikan jawaban dalam bahasa Indonesia. ";

  const prompt = kodeLengkap
    ? `${systemPrompt}\nBuat kode lengkap dan siap jalankan untuk: ${userText}\n
Berikan kode dalam satu blok markdown \`\`\`bahasa ... \`\`\`. Jangan ada penjelasan di luar blok kode. Tidak ada placeholder TODO.
`
    : `${systemPrompt}\nPengguna: ${userText}\nBalas dalam bahasa Indonesia.`;

  const body = {
    model: cfg.model,
    messages: [
      { role: "system", content: systemPrompt },
      { role: "user", content: prompt },
    ],
    temperature: cfg.temperature,
    stream: false,
  };

  const respons = await fetch(`${cfg.baseUrl}/chat/completions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${cfg.apiKey}`,
    },
    body: JSON.stringify(body),
  });

  if (!respons.ok) {
    const teksError = await respons.text();
    throw new Error(`HTTP ${respons.status}: ${teksError}`);
  }

  const data = await respons.json();
  const isi = data.choices && data.choices[0]
    ? data.choices[0].message.content
    : "";

  if (kodeLengkap) {
    return ekstraksiKode(isi) || isi;
  }
  return isi;
}

function ekstraksiKode(teks) {
  const cocok = teks.match(/```(\w+)?\n([\s\S]*?)```/);
  if (!cocok) return null;
  return cocok[2].trim();
}

async function simpanKeFile(cfg, deskripsi, kode) {
  const folder =
    vscode.workspace.workspaceFolders &&
    vscode.workspace.workspaceFolders.length > 0
      ? vscode.workspace.workspaceFolders[0].uri.fsPath
      : vscode.Uri.file(require("os").homedir()).fsPath;

  const fs = require("fs");
  const path = require("path");

  const dirCode = path.join(folder, "generated_code");
  if (!fs.existsSync(dirCode)) {
    fs.mkdirSync(dirCode, { recursive: true });
  }

  const aman = deskripsi
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "")
    .slice(0, 60) || "skrip";

  let namaFile = `${aman}.py`;
  if (kode.includes("<html") || kode.includes("<!DOCTYPE")) namaFile = `${aman}.html`;
  else if (kode.includes("function ") || kode.includes("const ") || kode.includes("let ")) namaFile = `${aman}.js`;
  else if (kode.includes("def ") || kode.includes("import ")) namaFile = `${aman}.py`;
  else if (kode.includes("public class") || kode.includes("System.out.println")) namaFile = `${aman}.java`;

  let counter = 1;
  let filePath = path.join(dirCode, namaFile);
  while (fs.existsSync(filePath)) {
    filePath = path.join(dirCode, `${aman}_${counter}.py`);
    counter++;
  }

  fs.writeFileSync(filePath, kode, "utf8");
  return vscode.Uri.file(filePath);
}

module.exports = { activate, deactivate };

