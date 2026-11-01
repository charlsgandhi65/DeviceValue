import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Home from './pages/Home'
import Comparison from './pages/Comparison'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/comparison" element={<Comparison />} />
      </Routes>
    </BrowserRouter>
  )
}
