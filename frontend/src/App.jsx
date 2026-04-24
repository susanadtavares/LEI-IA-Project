import { useEffect, useMemo, useState } from 'react'
import {
  detectPlateFromImage,
  fetchAttractions,
  fetchCities,
  fetchModels,
  runCompare,
  runRoute,
  validatePlate,
} from './api'
import './App.css'

const ITERATION_COLUMN_MAP = {
  ucs: [
    { key: 'node', label: 'Nó' },
    { key: 'g', label: 'g(n)' },
    { key: 'path', label: 'Caminho' },
  ],
  dls: [
    { key: 'node', label: 'Nó' },
    { key: 'depth', label: 'Prof' },
    { key: 'g', label: 'g(n)' },
    { key: 'path', label: 'Caminho' },
  ],
  greedy: [
    { key: 'node', label: 'Nó' },
    { key: 'h', label: 'h(n)' },
    { key: 'g', label: 'g(n)' },
    { key: 'path', label: 'Caminho' },
  ],
  astar: [
    { key: 'node', label: 'Nó' },
    { key: 'f', label: 'f(n)' },
    { key: 'g', label: 'g(n)' },
    { key: 'h', label: 'h(n)' },
    { key: 'path', label: 'Caminho' },
  ],
}

function App() {
  const [cities, setCities] = useState([])
  const [models, setModels] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [plateInput, setPlateInput] = useState('')
  const [plate, setPlate] = useState('')
  const [imageFile, setImageFile] = useState(null)

  const [start, setStart] = useState('')
  const [goal, setGoal] = useState('')
  const [algorithm, setAlgorithm] = useState('ucs')
  const [depthLimit, setDepthLimit] = useState(4)
  const [routeResult, setRouteResult] = useState(null)
  const [compareResults, setCompareResults] = useState([])

  const [selectedModel, setSelectedModel] = useState('llama3.2')
  const [attractions, setAttractions] = useState([])

  useEffect(() => {
    async function bootstrap() {
      try {
        setLoading(true)
        setError('')
        const [cityList, modelList] = await Promise.all([fetchCities(), fetchModels()])
        setCities(cityList)
        setModels(modelList)
        if (cityList.length > 1) {
          setStart(cityList[0])
          setGoal(cityList[1])
        }
        if (modelList.length > 0) {
          setSelectedModel(modelList[0])
        }
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    bootstrap()
  }, [])

  const canRun = useMemo(() => {
    return plate && start && goal && start !== goal
  }, [plate, start, goal])

  async function handlePlateManual(event) {
    event.preventDefault()
    try {
      setLoading(true)
      setError('')
      const data = await validatePlate(plateInput)
      setPlate(data.plate)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function handlePlateOcr(event) {
    event.preventDefault()
    if (!imageFile) {
      setError('Seleciona uma imagem primeiro')
      return
    }
    try {
      setLoading(true)
      setError('')
      const data = await detectPlateFromImage(imageFile)
      setPlate(data.plate)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleRunRoute(event) {
    event.preventDefault()
    try {
      setLoading(true)
      setError('')
      const payload = {
        start,
        goal,
        algorithm,
        depth_limit: algorithm === 'dls' ? Number(depthLimit) : null,
      }
      const result = await runRoute(payload)
      setRouteResult(result)
      setCompareResults([])
      setAttractions([])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleCompare(event) {
    event.preventDefault()
    try {
      setLoading(true)
      setError('')
      const result = await runCompare({
        start,
        goal,
        depth_limit: Number(depthLimit),
      })
      setCompareResults(result.results ?? [])
      setRouteResult(null)
      setAttractions([])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleAttractions(event) {
    event.preventDefault()
    const path = routeResult?.path ?? []
    if (!path.length) {
      setError('Executa uma rota antes de pedir atrações')
      return
    }
    try {
      setLoading(true)
      setError('')
      const answers = await Promise.all(
        path.map((city) => fetchAttractions({ city, model: selectedModel }))
      )
      setAttractions(answers)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  function labelAlgorithm(value) {
    const map = {
      ucs: 'Custo Uniforme',
      dls: 'Profundidade Limitada',
      greedy: 'Sôfrega',
      astar: 'A*',
    }
    return map[value] ?? value
  }

  function getIterationColumns(algorithm) {
    return ITERATION_COLUMN_MAP[algorithm] ?? ITERATION_COLUMN_MAP.ucs
  }

  function getIterationValue(iteration, key) {
    if (key === 'path') {
      return Array.isArray(iteration.path) ? iteration.path.join(' -> ') : '-'
    }
    return iteration[key] ?? '-'
  }

  function serializeCompareToCsv(results) {
    const header = [
      'algorithm',
      'distance_km',
      'iterations',
      'execution_ms',
      'expanded_nodes',
      'path_nodes',
      'found',
      'path',
    ]

    const rows = results.map((result) => [
      result.algorithm,
      result.cost,
      result.iterations?.length ?? 0,
      result.metrics?.execution_ms ?? '',
      result.metrics?.expanded_nodes ?? '',
      result.metrics?.path_nodes ?? '',
      result.metrics?.found ?? false,
      (result.path ?? []).join(' -> '),
    ])

    return [header, ...rows]
      .map((row) => row.map((value) => `"${String(value).replace(/"/g, '""')}"`).join(','))
      .join('\n')
  }

  function downloadFile(content, mimeType, filename) {
    const blob = new Blob([content], { type: mimeType })
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = filename
    document.body.appendChild(anchor)
    anchor.click()
    anchor.remove()
    URL.revokeObjectURL(url)
  }

  function exportCompare(format) {
    if (!compareResults.length) {
      setError('Não há comparação para exportar')
      return
    }

    if (format === 'json') {
      downloadFile(
        JSON.stringify(compareResults, null, 2),
        'application/json;charset=utf-8',
        'comparacao-rotas.json'
      )
      return
    }

    const csv = serializeCompareToCsv(compareResults)
    downloadFile(csv, 'text/csv;charset=utf-8', 'comparacao-rotas.csv')
  }

  return (
    <div className="app-shell">
      <header className="hero">
        <p className="kicker">LEI IA 2026</p>
        <h1>Navegador Inteligente de Cidades</h1>
        <p className="lead">
          Planeia rotas entre cidades portuguesas com algoritmos de procura, OCR de matrículas e
          apoio de LLM local.
        </p>
      </header>

      {error && <div className="alert">{error}</div>}

      <section className="grid-two">
        <article className="panel">
          <h2>1) Login por Matrícula</h2>
          <p className="muted">Valida manualmente ou reconhece com OCR.</p>
          <form onSubmit={handlePlateManual} className="form-row">
            <input
              value={plateInput}
              onChange={(e) => setPlateInput(e.target.value)}
              placeholder="AA-00-BB"
            />
            <button type="submit" disabled={loading}>
              Validar
            </button>
          </form>
          <form onSubmit={handlePlateOcr} className="form-row">
            <input type="file" accept="image/*" onChange={(e) => setImageFile(e.target.files?.[0] ?? null)} />
            <button type="submit" disabled={loading}>
              Ler OCR
            </button>
          </form>
          <p className="plate-value">Veículo: <strong>{plate || 'não autenticado'}</strong></p>
        </article>

        <article className="panel">
          <h2>2) Configuração da Rota</h2>
          <p className="muted">Escolhe origem, destino e algoritmo.</p>
          <form className="route-form" onSubmit={handleRunRoute}>
            <label>
              Origem
              <select value={start} onChange={(e) => setStart(e.target.value)}>
                {cities.map((city) => (
                  <option key={city} value={city}>
                    {city}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Destino
              <select value={goal} onChange={(e) => setGoal(e.target.value)}>
                {cities.map((city) => (
                  <option key={city} value={city}>
                    {city}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Algoritmo
              <select value={algorithm} onChange={(e) => setAlgorithm(e.target.value)}>
                <option value="ucs">Custo Uniforme</option>
                <option value="dls">Profundidade Limitada</option>
                <option value="greedy">Sôfrega</option>
                <option value="astar">A*</option>
              </select>
            </label>
            <label>
              Limite DLS
              <input
                type="number"
                min="1"
                value={depthLimit}
                onChange={(e) => setDepthLimit(e.target.value)}
              />
            </label>
            <div className="actions">
              <button type="submit" disabled={!canRun || loading}>
                Executar Rota
              </button>
              <button type="button" onClick={handleCompare} disabled={!canRun || loading}>
                Comparar 4 Algoritmos
              </button>
            </div>
          </form>
        </article>
      </section>

      {routeResult && (
        <section className="panel">
          <h2>Resultado de Rota</h2>
          <p>
            <strong>{labelAlgorithm(routeResult.algorithm)}</strong> | Distância total:{' '}
            <strong>{routeResult.cost} km</strong>
          </p>
          <p className="path">{routeResult.path?.join(' -> ') || 'Sem caminho'}</p>

          <div className="metrics-grid">
            <div className="metric-item">
              <span>Tempo</span>
              <strong>{routeResult.metrics?.execution_ms ?? '-'} ms</strong>
            </div>
            <div className="metric-item">
              <span>Nós expandidos</span>
              <strong>{routeResult.metrics?.expanded_nodes ?? '-'}</strong>
            </div>
            <div className="metric-item">
              <span>Nós no caminho</span>
              <strong>{routeResult.metrics?.path_nodes ?? '-'}</strong>
            </div>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  {getIterationColumns(routeResult.algorithm).map((column) => (
                    <th key={column.key}>{column.label}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {routeResult.iterations.map((it, idx) => (
                  <tr key={`${it.node}-${idx}`}>
                    <td>{idx + 1}</td>
                    {getIterationColumns(routeResult.algorithm).map((column) => (
                      <td key={`${column.key}-${idx}`}>{getIterationValue(it, column.key)}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="llm-box">
            <label>
              Modelo LLM
              <select value={selectedModel} onChange={(e) => setSelectedModel(e.target.value)}>
                {(models.length ? models : ['llama3.2']).map((m) => (
                  <option value={m} key={m}>
                    {m}
                  </option>
                ))}
              </select>
            </label>
            <button onClick={handleAttractions} disabled={loading}>
              Gerar Atrações da Rota
            </button>
          </div>
        </section>
      )}

      {compareResults.length > 0 && (
        <section className="panel">
          <h2>Comparação de Algoritmos</h2>
          <div className="toolbar">
            <button type="button" onClick={() => exportCompare('json')}>
              Exportar JSON
            </button>
            <button type="button" onClick={() => exportCompare('csv')}>
              Exportar CSV
            </button>
          </div>
          <div className="cards">
            {compareResults.map((result) => (
              <article key={result.algorithm} className="result-card">
                <h3>{labelAlgorithm(result.algorithm)}</h3>
                <p>
                  Distância: <strong>{result.cost} km</strong>
                </p>
                <p>Iterações: {result.iterations.length}</p>
                <p>Tempo: {result.metrics?.execution_ms ?? '-'} ms</p>
                <p>Nós expandidos: {result.metrics?.expanded_nodes ?? '-'}</p>
                <p className="path-small">{result.path?.join(' -> ') || 'Sem caminho'}</p>
              </article>
            ))}
          </div>
        </section>
      )}

      {attractions.length > 0 && (
        <section className="panel">
          <h2>Atrações Turísticas</h2>
          <div className="cards">
            {attractions.map((item) => (
              <article key={item.city} className="result-card">
                <h3>{item.city}</h3>
                <pre>{item.content}</pre>
              </article>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}

export default App
