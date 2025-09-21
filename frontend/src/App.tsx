import { Routes, Route } from 'react-router-dom';
import Home from './pages/Home.tsx';
import NewDossier from './pages/NewDossier.tsx';
import Review from './pages/Review.tsx';
import Compare from './pages/Compare.tsx';
import CompareResult from './pages/CompareResult.tsx';

function App() {
  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--bg)' }}>
      
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/new" element={<NewDossier />} />
          <Route path="/review" element={<Review />} />
          <Route path="/compare" element={<Compare />} />
          <Route path="/compare/result" element={<CompareResult />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
