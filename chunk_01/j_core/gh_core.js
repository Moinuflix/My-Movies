
const CONFIRM_PIN = "24592";
const TMDB_API_KEY = "051ccf72e026820cb53b8b8531b6a2ba";
const GH_REPO = "Moinuflix/My-Movies";
const GH_BRANCH = "main";
const WORKER_BASE = "https://gdrive-stream.moinudeentv.workers.dev/?id=";
const USER_AGENT = "|User-Agent=Kodi-MoinuTV-PrivatePlayer/1.0";

function getStoredToken() { return localStorage.getItem("moinuflix_gh_token") || ""; }
function configureGithubToken() {
  const c = getStoredToken();
  const input = prompt("Enter your GitHub Token (ghp_...):", c);
  if(input !== null) { localStorage.setItem("moinuflix_gh_token", input.trim()); showLaserToast("GitHub Token Saved!"); }
}
function showLaserToast(msg, isError = false) {
  const t = document.getElementById("laser-toast");
  if(!t) return;
  t.style.borderColor = isError ? "var(--laser-red)" : "var(--laser-cyan)";
  t.textContent = (isError ? "❌ " : "⚡ ") + msg;
  t.style.display = "block";
  setTimeout(() => { t.style.display = "none"; }, 3500);
}
function extractGDriveId(url) {
  if(!url) return "";
  const clean = url.trim();
  const pMatch = clean.match(/[?&]id=([a-zA-Z0-9_-]+)/);
  if(pMatch) return pMatch[1];
  const fMatch = clean.match(/\/file\/d\/([a-zA-Z0-9_-]+)/);
  if(fMatch) return fMatch[1];
  const foldMatch = clean.match(/\/folders\/([a-zA-Z0-9_-]+)/);
  if(foldMatch) return foldMatch[1];
  return clean;
}
function cleanAndRoundSize(raw) {
  if(!raw) return "10GB";
  const m = String(raw).match(/([\d\.]+)\s*(gb|mb)?/i);
  if(!m) return "10GB";
  let num = parseFloat(m[1]);
  if((m[2] || "gb").toLowerCase() === "mb") num /= 1024;
  return Math.max(1, Math.min(50, Math.round(num))) + "GB";
}
async function fetchChunk(chunkPath) {
  try {
    const res = await fetch("https://raw.githubusercontent.com/" + GH_REPO + "/" + GH_BRANCH + "/" + chunkPath + "?t=" + Date.now());
    return res.ok ? await res.json() : [];
  } catch(e) { return []; }
}
async function commitFileDirect(chunkPath, arrayData, message, token) {
  const url = "https://api.github.com/repos/" + GH_REPO + "/contents/" + chunkPath;
  let sha = undefined;
  try {
    const getRes = await fetch(url + "?t=" + Date.now(), { headers: { "Authorization": "Bearer " + token } });
    if(getRes.ok) sha = (await getRes.json()).sha;
  } catch(e) {}
  const jsonStr = JSON.stringify(arrayData, null, 2);
  const binary = Array.from(new TextEncoder().encode(jsonStr)).map(b => String.fromCharCode(b)).join("");
  const res = await fetch(url, {
    method: "PUT",
    headers: { "Authorization": "Bearer " + token, "Content-Type": "application/json" },
    body: JSON.stringify({ message: message, content: btoa(binary), branch: GH_BRANCH, sha: sha })
  });
  if(!res.ok) throw new Error("Commit failed");
}
