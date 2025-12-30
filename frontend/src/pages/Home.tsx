import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import AuthModal from '../components/AuthModal';
import { PixelRocket, PixelUsers, PixelChart, PixelBook } from '../components/PixelIcons';
import './Home.css';

function Home() {
  const { isAuthenticated, user } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="home-page">
      {isAuthenticated ? (
        <div className="dashboard">
          <div className="dashboard-header">
            <h1 className="dashboard-title">Bienvenue, Général {user?.pseudo}</h1>
            <p className="dashboard-subtitle">Prêt à conquérir la galaxie ?</p>
          </div>

          <div className="dashboard-cards">
            <div className="dashboard-card card-primary">
              <div className="card-icon">
                <PixelRocket size={32} />
              </div>
              <h2 className="card-title">Nouvelle Partie</h2>
              <p className="card-description">
                Lancez une nouvelle conquête galactique et affrontez jusqu'à 7 adversaires.
              </p>
              <button className="btn-primary card-button" onClick={() => navigate('/games/new')}>
                Commencer
              </button>
            </div>

            <div className="dashboard-card">
              <div className="card-icon">
                <PixelUsers size={32} />
              </div>
              <h2 className="card-title">Rejoindre une Partie</h2>
              <p className="card-description">
                Rejoignez une partie en cours et combattez aux côtés d'autres généraux.
              </p>
              <button className="card-button" onClick={() => navigate('/games')}>
                Parcourir
              </button>
            </div>

            <div className="dashboard-card">
              <div className="card-icon">
                <PixelChart size={32} />
              </div>
              <h2 className="card-title">Statistiques</h2>
              <p className="card-description">
                Consultez vos victoires, défaites et performances au fil des parties.
              </p>
              <button className="card-button" disabled>
                Bientôt
              </button>
            </div>

            <div className="dashboard-card">
              <div className="card-icon">
                <PixelBook size={32} />
              </div>
              <h2 className="card-title">Tutoriel</h2>
              <p className="card-description">
                Apprenez les bases de la conquête spatiale napoléonienne.
              </p>
              <button className="card-button" disabled>
                Bientôt
              </button>
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
