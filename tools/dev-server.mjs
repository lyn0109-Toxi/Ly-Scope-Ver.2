import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const preferredPort = Number(process.env.PORT || 4173);
const mimeTypes = new Map([
  ['.html', 'text/html; charset=utf-8'],
  ['.css', 'text/css; charset=utf-8'],
  ['.js', 'text/javascript; charset=utf-8'],
  ['.json', 'application/json; charset=utf-8'],
  ['.svg', 'image/svg+xml'],
]);

function resolveRequestPath(url) {
  const requestedPath = decodeURIComponent(new URL(url, 'http://localhost').pathname);
  const cleanPath = requestedPath === '/' ? '/index.html' : requestedPath;
  const filePath = path.resolve(root, `.${cleanPath}`);

  if (!filePath.startsWith(root)) {
    return null;
  }

  return filePath;
}

async function serveFile(request, response) {
  const filePath = resolveRequestPath(request.url);

  if (!filePath) {
    response.writeHead(403);
    response.end('Forbidden');
    return;
  }

  try {
    const fileStat = await stat(filePath);
    const finalPath = fileStat.isDirectory()
      ? path.join(filePath, 'index.html')
      : filePath;
    const body = await readFile(finalPath);
    const contentType =
      mimeTypes.get(path.extname(finalPath)) || 'application/octet-stream';

    response.writeHead(200, { 'Content-Type': contentType });
    response.end(body);
  } catch {
    response.writeHead(404);
    response.end('Not found');
  }
}

function listen(port) {
  const server = createServer(serveFile);

  server.on('error', (error) => {
    if (error.code === 'EADDRINUSE') {
      listen(port + 1);
      return;
    }

    throw error;
  });

  server.listen(port, '127.0.0.1', () => {
    console.log(`LY-Scope Ver.2 running at http://127.0.0.1:${port}`);
  });
}

listen(preferredPort);
