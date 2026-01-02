import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Layout from './components/Layout';
import Home from './pages/Home';
import Profile from './pages/Profile';
import OAuthCallback from './pages/OAuthCallback';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import GameList from './pages/GameList';
import CreateGame from './pages/CreateGame';
import GameLobby from './pages/GameLobby';
import GameView from './pages/GameView';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Home />} />
            <Route
              path="profile"
              element={
                <ProtectedRoute>
                  <Profile />
                </ProtectedRoute>
              }
            />
            <Route
              path="games"
              element={
                <ProtectedRoute>
                  <GameList />
                </ProtectedRoute>
              }
            />
            <Route
              path="games/new"
              element={
                <ProtectedRoute>
                  <CreateGame />
                </ProtectedRoute>
              }
            />
            <Route
              path="games/:gameId/lobby"
              element={
                <ProtectedRoute>
                  <GameLobby />
                </ProtectedRoute>
              }
            />
          </Route>
          {/* GameView has its own header, outside Layout */}
          <Route
            path="games/:gameId/play"
            element={
              <ProtectedRoute>
                <GameView />
              </ProtectedRoute>
            }
          />
          <Route path="/oauth/callback" element={<OAuthCallback />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
