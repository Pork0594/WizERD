import process from 'node:process';
import ELK from 'elkjs/lib/elk.bundled.js';

const elk = new ELK();

const readStdin = async () =>
  new Promise((resolve, reject) => {
    const chunks = [];
    process.stdin.on('data', (chunk) => chunks.push(chunk));
    process.stdin.on('error', (error) => reject(error));
    process.stdin.on('end', () => {
      try {
        resolve(JSON.parse(Buffer.concat(chunks).toString('utf-8')));
      } catch (error) {
        reject(error);
      }
    });
  });

const run = async () => {
    const payload = await readStdin();
    const layout = await elk.layout(payload);
    process.stdout.write(JSON.stringify(layout));
};

run().catch((error) => {
  console.error(error instanceof Error ? error.stack : error);
  process.exitCode = 1;
});
