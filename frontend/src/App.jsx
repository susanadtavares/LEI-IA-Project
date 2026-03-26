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
      greedy: 'Sofrega',
      astar: 'A*',
    }
    return map[value] ?? value
  }

  return (
    <div className="app-shell">
      <header className="hero">
        <p className="kicker">LEI IA 2026</p>
        <h1>Navegador Inteligente de Cidades</h1>
        <p className="lead">
          Planeia rotas entre cidades portuguesas com algoritmos de procura, OCR de matriculas e
          apoio de LLM local.
        </p>
      </header>

      {error && <div className="alert">{error}</div>}

      <section className="grid-two">
        <article className="panel">
          <h2>1) Login por Matricula</h2>
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
          <p className="plate-value">Veiculo: <strong>{plate || 'nao autenticado'}</strong></p>
        </article>

        <article className="panel">
          <h2>2) Configuracao da Rota</h2>
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
                <option value="greedy">Sofrega</option>
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
            <strong>{labelAlgorithm(routeResult.algorithm)}</strong> | Distancia total:{' '}
            <strong>{routeResult.cost} km</strong>
          </p>
          <p className="path">{routeResult.path?.join(' -> ') || 'Sem caminho'}</p>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>No</th>
                  <th>g(n)</th>
                  <th>h(n)</th>
                  <th>f(n)</th>
                </tr>
              </thead>
              <tbody>
                {routeResult.iterations.map((it, idx) => (
                  <tr key={`${it.node}-${idx}`}>
                    <td>{idx + 1}</td>
                    <td>{it.node}</td>
                    <td>{it.g ?? '-'}</td>
                    <td>{it.h ?? '-'}</td>
                    <td>{it.f ?? '-'}</td>
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
              Gerar Atractoes da Rota
            </button>
          </div>
        </section>
      )}

      {compareResults.length > 0 && (
        <section className="panel">
          <h2>Comparacao de Algoritmos</h2>
          <div className="cards">
            {compareResults.map((result) => (
              <article key={result.algorithm} className="result-card">
                <h3>{labelAlgorithm(result.algorithm)}</h3>
                <p>
                  Distancia: <strong>{result.cost} km</strong>
                </p>
                <p>Iteracoes: {result.iterations.length}</p>
                <p className="path-small">{result.path?.join(' -> ') || 'Sem caminho'}</p>
              </article>
            ))}
          </div>
        </section>
      )}

      {attractions.length > 0 && (
        <section className="panel">
          <h2>Atractoes Turisticas</h2>
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
