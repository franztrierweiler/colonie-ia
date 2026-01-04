import { useState, useEffect } from 'react';
import api from '../../services/api';
import type { CombatReportSummary, CombatReportFull } from '../../services/api';
import './CombatReportPanel.css';

interface CombatReportPanelProps {
  gameId: number;
  currentTurn: number;
  playerId: number;
}

function CombatReportPanel({ gameId, currentTurn, playerId }: CombatReportPanelProps) {
  const [reports, setReports] = useState<CombatReportSummary[]>([]);
  const [selectedReport, setSelectedReport] = useState<CombatReportFull | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadReports();
  }, [gameId, currentTurn]);

  const loadReports = async () => {
    try {
      const data = await api.getCombatReports(gameId, currentTurn - 1);
      setReports(data.reports);
    } catch (err) {
      console.error('Erreur chargement rapports combat:', err);
    }
  };

  const loadReportDetails = async (reportId: number) => {
    setIsLoading(true);
    try {
      const report = await api.getCombatReport(reportId);
      setSelectedReport(report);
    } catch (err) {
      console.error('Erreur chargement details rapport:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const getResultIcon = (report: CombatReportSummary) => {
    if (report.victor_id === playerId) return '🏆';
    if (report.victor_id === null) return '⚔️';
    return '💀';
  };

  const getResultClass = (report: CombatReportSummary) => {
    if (report.victor_id === playerId) return 'victory';
    if (report.victor_id === null) return 'draw';
    return 'defeat';
  };

  if (reports.length === 0) {
    return (
      <div className="combat-report-panel">
        <h4>Combats</h4>
        <p className="no-reports">Aucun combat ce tour</p>
      </div>
    );
  }

  return (
    <div className="combat-report-panel">
      <h4>Combats ({reports.length})</h4>

      <div className="combat-list">
        {reports.map((report) => (
          <div
            key={report.id}
            className={`combat-item ${getResultClass(report)} ${selectedReport?.id === report.id ? 'selected' : ''}`}
            onClick={() => loadReportDetails(report.id)}
          >
            <span className="combat-icon">{getResultIcon(report)}</span>
            <div className="combat-info">
              <span className="combat-planet">{report.planet_name}</span>
              <span className="combat-losses">
                {report.attacker_losses + report.defender_losses} vx perdus
              </span>
            </div>
            {report.planet_captured && <span className="captured-badge">Capture</span>}
          </div>
        ))}
      </div>

      {/* Details panel */}
      {selectedReport && (
        <div className="combat-details">
          <div className="details-header">
            <h5>{selectedReport.planet_name}</h5>
            <button className="close-btn" onClick={() => setSelectedReport(null)}>×</button>
          </div>

          {isLoading ? (
            <p>Chargement...</p>
          ) : (
            <>
              <div className="details-section">
                <h6>Forces engagees</h6>
                <div className="forces-grid">
                  <div className="forces-attacker">
                    <span className="label">Attaquants</span>
                    {Object.entries(selectedReport.attacker_forces).map(([playerId, ships]) => (
                      <div key={playerId} className="force-entry">
                        {Object.entries(ships).map(([type, count]) => (
                          <span key={type}>{count} {type}</span>
                        ))}
                      </div>
                    ))}
                  </div>
                  <div className="forces-defender">
                    <span className="label">Defenseurs</span>
                    {Object.entries(selectedReport.defender_forces).map(([type, count]) => (
                      <span key={type}>{count} {type}</span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="details-section">
                <h6>Pertes</h6>
                <div className="losses-summary">
                  <span>Attaquants: {selectedReport.attacker_losses} vx</span>
                  <span>Defenseurs: {selectedReport.defender_losses} vx</span>
                  {selectedReport.population_casualties > 0 && (
                    <span className="pop-casualties">
                      Population: -{selectedReport.population_casualties.toLocaleString()}
                    </span>
                  )}
                </div>
              </div>

              {selectedReport.metal_recovered > 0 && (
                <div className="details-section">
                  <h6>Debris</h6>
                  <span className="metal-recovered">
                    +{selectedReport.metal_recovered} metal recupere
                  </span>
                </div>
              )}

              <div className="details-section combat-log-section">
                <h6>Journal de combat</h6>
                <div className="combat-log">
                  {selectedReport.combat_log.slice(0, 10).map((entry, idx) => (
                    <div key={idx} className={`log-entry log-${entry.phase}`}>
                      {entry.message}
                    </div>
                  ))}
                  {selectedReport.combat_log.length > 10 && (
                    <div className="log-entry log-more">
                      ... et {selectedReport.combat_log.length - 10} autres
                    </div>
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default CombatReportPanel;
