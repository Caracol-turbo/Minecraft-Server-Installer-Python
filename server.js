import express from 'express';
import cors from 'cors';
import { exec, spawn } from 'child_process';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

const SERVERS_DIR = path.join(__dirname, 'servers');
const activeProcesses = new Map(); // serverName -> { process, logs: [] }

// Helper para ejecutar comandos python de la libreria
function runPythonBridge(action, args = []) {
  return new Promise((resolve, reject) => {
    const bridgePath = path.join(__dirname, 'lib', 'cli_bridge.py');
    const cmdArgs = [bridgePath, action, ...args];
    exec(`python3 ${cmdArgs.map(a => `"${a}"`).join(' ')}`, (error, stdout, stderr) => {
      if (error) {
        try {
          const jsonErr = JSON.parse(stdout);
          return resolve(jsonErr);
        } catch (e) {
          return reject(stderr || stdout || error.message);
        }
      }
      try {
        const result = JSON.parse(stdout);
        resolve(result);
      } catch (e) {
        resolve({ raw: stdout });
      }
    });
  });
}

// Ensure servers directory exists
async function ensureServersDir() {
  try {
    await fs.mkdir(SERVERS_DIR, { recursive: true });
  } catch (err) {
    console.error('Error creating servers directory:', err);
  }
}
ensureServersDir();

// GET /api/servers - Listar servidores
app.get('/api/servers', async (req, res) => {
  try {
    await ensureServersDir();
    const entries = await fs.readdir(SERVERS_DIR, { withFileTypes: true });
    const servers = [];

    for (const entry of entries) {
      if (entry.isDirectory()) {
        const serverPath = path.join(SERVERS_DIR, entry.name);
        const hasJar = await fs.access(path.join(serverPath, 'server.jar')).then(() => true)
          .catch(() => fs.access(path.join(serverPath, 'installer.jar')).then(() => true))
          .catch(() => fs.access(path.join(serverPath, 'run.sh')).then(() => true))
          .catch(() => false);
        const hasProps = await fs.access(path.join(serverPath, 'server.properties')).then(() => true).catch(() => false);
        const hasStart = await fs.access(path.join(serverPath, 'start.sh')).then(() => true).catch(() => false);


        servers.push({
          name: entry.name,
          hasJar,
          hasProps,
          hasStart,
          isRunning: activeProcesses.has(entry.name)
        });
      }
    }
    res.json(servers);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET /api/versions/:software - Obtener versiones
app.get('/api/versions/:software', async (req, res) => {
  const { software } = req.params;
  const version = req.query.version || '';
  try {
    if (software === 'vanilla') {
      const data = await runPythonBridge('get_vanilla_versions');
      res.json(data);
    } else if (software === 'paper') {
      if (version) {
        const builds = await runPythonBridge('get_paper_builds', [version]);
        res.json(builds);
      } else {
        const versions = await runPythonBridge('get_paper_versions');
        res.json(versions);
      }
    } else if (software === 'purpur') {
      if (version) {
        const builds = await runPythonBridge('get_purpur_builds', [version]);
        res.json(builds);
      } else {
        const versions = await runPythonBridge('get_purpur_versions');
        res.json(versions);
      }
    } else if (software === 'fabric') {
      const data = await runPythonBridge('get_fabric_versions');
      res.json(data);
    } else if (software === 'forge') {
      if (version) {
        const builds = await runPythonBridge('get_forge_builds', [version]);
        res.json(builds);
      } else {
        const versions = await runPythonBridge('get_forge_versions');
        res.json(versions);
      }
    } else if (software === 'neoforge') {
      const versions = await runPythonBridge('get_neoforge_versions');
      res.json(versions);
    } else {
      res.status(400).json({ error: 'Software no soportado' });
    }
  } catch (err) {
    res.status(500).json({ error: String(err) });
  }
});

// POST /api/servers/create - Crear nuevo servidor
app.post('/api/servers/create', async (req, res) => {
  const { serverName, software, version, extra, ram } = req.body;
  if (!serverName || !software || !version) {
    return res.status(400).json({ error: 'Faltan parámetros requeridos' });
  }

  try {
    const result = await runPythonBridge('create_server', [
      serverName,
      software,
      version,
      extra || '',
      ram || '2G'
    ]);
    res.json(result);
  } catch (err) {
    res.status(500).json({ success: false, error: String(err) });
  }
});

// GET /api/servers/:name/properties - Leer server.properties
app.get('/api/servers/:name/properties', async (req, res) => {
  const propsPath = path.join(SERVERS_DIR, req.params.name, 'server.properties');
  try {
    const content = await fs.readFile(propsPath, 'utf-8');
    res.json({ content });
  } catch (err) {
    res.status(404).json({ error: 'server.properties no encontrado' });
  }
});

// POST /api/servers/:name/properties - Guardar server.properties
app.post('/api/servers/:name/properties', async (req, res) => {
  const propsPath = path.join(SERVERS_DIR, req.params.name, 'server.properties');
  const { content } = req.body;
  try {
    await fs.writeFile(propsPath, content, 'utf-8');
    res.json({ success: true, message: 'server.properties guardado con éxito' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST /api/servers/:name/start - Arrancar servidor
app.post('/api/servers/:name/start', async (req, res) => {
  const name = req.params.name;
  const srvDir = path.join(SERVERS_DIR, name);
  const startSh = path.join(srvDir, 'start.sh');

  if (activeProcesses.has(name)) {
    return res.json({ message: 'El servidor ya se encuentra en ejecución', isRunning: true });
  }

  try {
    await fs.access(startSh);
  } catch (err) {
    return res.status(400).json({ error: 'No existe start.sh en el directorio del servidor' });
  }

  const child = spawn('./start.sh', [], { cwd: srvDir, shell: true });
  const logs = [];

  child.stdout.on('data', (data) => {
    const msg = data.toString();
    logs.push(msg);
    if (logs.length > 500) logs.shift();
  });

  child.stderr.on('data', (data) => {
    const msg = data.toString();
    logs.push(`[STDERR] ${msg}`);
    if (logs.length > 500) logs.shift();
  });

  child.on('close', (code) => {
    logs.push(`\n[PROCESO FINALIZADO CON CÓDIGO ${code}]`);
    activeProcesses.delete(name);
  });

  activeProcesses.set(name, { process: child, logs });
  res.json({ success: true, message: `Servidor ${name} iniciado.` });
});

// POST /api/servers/:name/stop - Detener servidor
app.post('/api/servers/:name/stop', async (req, res) => {
  const name = req.params.name;
  if (!activeProcesses.has(name)) {
    return res.status(400).json({ error: 'El servidor no está en ejecución' });
  }

  const item = activeProcesses.get(name);
  try {
    item.process.kill('SIGTERM');
    activeProcesses.delete(name);
    res.json({ success: true, message: `Servidor ${name} detenido.` });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET /api/servers/:name/logs - Obtener logs
app.get('/api/servers/:name/logs', (req, res) => {
  const name = req.params.name;
  if (!activeProcesses.has(name)) {
    return res.json({ logs: ['Servidor no en ejecución.'], isRunning: false });
  }
  const item = activeProcesses.get(name);
  res.json({ logs: item.logs, isRunning: true });
});

// --- API PLAYIT.GG ---
app.get('/api/playit/status', async (req, res) => {
  try {
    const status = await runPythonBridge('playit_status');
    res.json(status);
  } catch (err) {
    res.status(500).json({ error: String(err) });
  }
});

app.post('/api/playit/start', async (req, res) => {
  const { secretKey } = req.body || {};
  try {
    const result = await runPythonBridge('playit_start', secretKey ? [secretKey] : []);
    res.json(result);
  } catch (err) {
    res.status(500).json({ error: String(err) });
  }
});

app.post('/api/playit/stop', async (req, res) => {
  try {
    const result = await runPythonBridge('playit_stop');
    res.json(result);
  } catch (err) {
    res.status(500).json({ error: String(err) });
  }
});

app.post('/api/playit/secret', async (req, res) => {
  const { secretKey } = req.body || {};
  try {
    const result = await runPythonBridge('playit_save_secret', [secretKey || '']);
    res.json(result);
  } catch (err) {
    res.status(500).json({ error: String(err) });
  }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Minecraft Server Installer Web Dashboard corriendo en http://localhost:${PORT}`);
});
