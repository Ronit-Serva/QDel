/* The browser and CLI use the same Python source, bundled in engine.zip. */
let python;
let chain = Promise.resolve();
async function handle({id, action, config, minutes}) {
  try {
    if (!python) {
      postMessage({type: 'loading', message: 'Loading Python runtime…'});
      importScripts('https://cdn.jsdelivr.net/pyodide/v0.27.7/full/pyodide.js');
      python = await loadPyodide({indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.27.7/full/'});
      const response = await fetch('engine.zip');
      if (!response.ok) throw new Error('Unable to fetch simulation engine');
      python.unpackArchive(await response.arrayBuffer(), 'zip');
      await python.runPythonAsync('import json\nfrom simulation import Config, Simulation');
    }
    let result;
    if (action === 'reset') {
      python.globals.set('config_json', JSON.stringify(config));
      result = await python.runPythonAsync('sim = Simulation(Config(**json.loads(config_json)))\njson.dumps(sim.snapshot())');
    } else {
      python.globals.set('step_minutes', minutes);
      result = await python.runPythonAsync('json.dumps(sim.advance(step_minutes))');
    }
    postMessage({id, type:'state', state:JSON.parse(result)});
  } catch (error) {
    postMessage({id, type:'error', message: String(error.message || error)});
  }
}
onmessage = ({data}) => { chain = chain.then(() => handle(data)); };
