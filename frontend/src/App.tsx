import { Routes, Route } from 'react-router-dom';
import Home from './pages/Home.tsx';
import NewDossier from './pages/NewDossier.tsx';
import Review from './pages/Review.tsx';

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-xl font-semibold text-gray-900">
            Dossier de Compétences - Analyseur CV
          </h1>
        </div>
      </nav>
      
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/new" element={<NewDossier />} />
          <Route path="/review" element={<Review />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
