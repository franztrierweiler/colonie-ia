/**
 * BudgetBars - Spaceward Ho! style horizontal budget allocation bars
 * Shows savings, tech, and per-planet budget allocation
 */
import { useState, useEffect, useCallback } from 'react';
import api from '../../services/api';
import type { PlayerTechnology } from '../../services/api';
import './BudgetBars.css';

interface Planet {
  id: number;
  name: string;
  population: number;
  terraform_budget: number;
  mining_budget: number;
  ships_budget: number;
}

interface Economy {
  money: number;
  income: number;
  debt: number;
}

interface BudgetBarsProps {
  gameId: number;
  planets: Planet[];
  playerColor: string;
  economy?: Economy | null;
  onPlanetClick?: (planetId: number) => void;
  selectedPlanetId?: number | null;
}

function BudgetBars({ gameId, planets, playerColor, economy, onPlanetClick, selectedPlanetId }: BudgetBarsProps) {
  const [technology, setTechnology] = useState<PlayerTechnology | null>(null);

  const loadTechnology = useCallback(async () => {
    try {
      const data = await api.getTechnology(gameId);
      setTechnology(data);
    } catch (err) {
      console.error('Erreur chargement tech:', err);
    }
  }, [gameId]);

  useEffect(() => {
    loadTechnology();
  }, [loadTechnology]);

  // Calculate relative planet importance based on population (proxy for income)
  const totalPopulation = planets.reduce((sum, p) => sum + p.population, 0);

  // Calculate total tech budget percentage (average of all 6 domains, scaled)
  const techTotal = technology?.budget
    ? Math.round((technology.budget.range + technology.budget.speed +
        technology.budget.weapons + technology.budget.shields +
        technology.budget.mini + technology.budget.radical) / 6)
    : 0;

  // Calculate savings as ratio of money to income (how many turns of income saved)
  // Cap at 100% for display
  const savingsPercent = economy && economy.income > 0
    ? Math.min(100, Math.round((economy.money / economy.income) * 10))
    : 0;

  // Sort planets by population (most important first)
  const sortedPlanets = [...planets].sort((a, b) => b.population - a.population);

  return (
    <div className="budget-bars">
      <div className="budget-bars-header">
        <span className="budget-scale">0%</span>
        <span className="budget-scale-label">Budget</span>
        <span className="budget-scale">100%</span>
      </div>

      {/* Savings bar */}
      <div className="budget-row">
        <span className="budget-label savings-label">Épargne</span>
        <div className="budget-bar-container">
          <div
            className="budget-bar-fill savings-fill"
            style={{ width: `${savingsPercent}%` }}
          />
        </div>
        <span className="budget-percent">{savingsPercent}%</span>
      </div>

      {/* Tech bar */}
      <div className="budget-row">
        <span className="budget-label tech-label">Tech</span>
        <div className="budget-bar-container">
          <div
            className="budget-bar-fill tech-fill"
            style={{ width: `${techTotal}%` }}
          />
        </div>
        <span className="budget-percent">{techTotal}%</span>
      </div>

      {/* Planet bars */}
      {sortedPlanets.map((planet) => {
        const relativeImportance = totalPopulation > 0
          ? Math.round((planet.population / totalPopulation) * 100)
          : 0;
        const isSelected = selectedPlanetId === planet.id;

        return (
          <div
            key={planet.id}
            className={`budget-row planet-row ${isSelected ? 'selected' : ''}`}
            onClick={() => onPlanetClick?.(planet.id)}
          >
            <span
              className="budget-label planet-label"
              style={{ color: playerColor }}
            >
              {planet.name.length > 8 ? planet.name.substring(0, 7) + '…' : planet.name}
            </span>
            <div className="budget-bar-container">
              <div
                className="budget-bar-fill planet-fill"
                style={{
                  width: `${relativeImportance}%`,
                  backgroundColor: playerColor
                }}
              />
            </div>
            <span className="budget-percent">{relativeImportance}%</span>
          </div>
        );
      })}

      {planets.length === 0 && (
        <div className="budget-empty">Aucune planète</div>
      )}
    </div>
  );
}

export default BudgetBars;
