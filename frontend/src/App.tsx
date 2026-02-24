import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Transactions from './pages/Transactions'
import Rules from './pages/Rules'
import Categories from './pages/Categories'
import Alerts from './pages/Alerts'
import Import from './pages/Import'
import Navigation from './components/Navigation'
import Income from './pages/Income'

function App() {
  return (
    <Router>
      <div className="min-h-screen dark">
        <Navigation />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/transactions" element={<Transactions />} />
            <Route path="/rules" element={<Rules />} />
            <Route path="/categories" element={<Categories />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/import" element={<Import />} />
            <Route path="/income" element={<Income />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App