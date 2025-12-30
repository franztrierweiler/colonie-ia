import { useAuth } from '../context/AuthContext';
import AuthModal from '../components/AuthModal';
import './Home.css';

function Home() {
  const { isAuthenticated, user } = useAuth();

  return (
    <div className="home-page">
      {isAuthenticated ? (
        <div className="hero-section">
          <img src="/game-logo.jpg" alt="Colonie-IA" className="game-logo" />
          <h1 className="game-title">Colonie-IA</h1>
          <p className="game-subtitle">Conquête Galactique à l'ère Napoléonienne</p>
          <div className="authenticated-section">
            <p className="welcome-message">Bienvenue, Général {user?.pseudo} !</p>
            <div className="game-actions">
              <button className="btn-primary btn-large">Nouvelle Partie</button>
              <button className="btn-large">Rejoindre une Partie</button>
            </div>
          </div>
        </div>
      ) : (
        <AuthModal />
      )}
    </div>
  );
}

export default Home;
