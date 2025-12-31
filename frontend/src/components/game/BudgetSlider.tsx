import { useRef, useEffect } from 'react';
import './BudgetSlider.css';

interface BudgetSliderProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
  color?: string;
  disabled?: boolean;
}

// Fonction de rendement logarithmique (rendements décroissants)
// 0% -> 0, 50% -> ~70%, 100% -> 100%
function logarithmicReturn(percentage: number): number {
  if (percentage <= 0) return 0;
  if (percentage >= 100) return 100;
  // Formule log : y = 100 * log(1 + x/100 * (e-1)) / log(e)
  // Simplifiée : plus d'investissement = moins de rendement marginal
  return 100 * Math.log(1 + (percentage / 100) * (Math.E - 1));
}

function BudgetSlider({
  label,
  value,
  onChange,
  color = 'var(--orange-primary)',
  disabled = false,
}: BudgetSliderProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Dessiner la courbe logarithmique
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;
    const padding = 2;

    // Clear
    ctx.clearRect(0, 0, width, height);

    // Background
    ctx.fillStyle = 'var(--bg-darker)';
    ctx.fillRect(0, 0, width, height);

    // Draw linear reference line (gray, dashed)
    ctx.strokeStyle = '#333';
    ctx.setLineDash([2, 2]);
    ctx.beginPath();
    ctx.moveTo(padding, height - padding);
    ctx.lineTo(width - padding, padding);
    ctx.stroke();

    // Draw logarithmic curve
    ctx.strokeStyle = '#555';
    ctx.setLineDash([]);
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let x = 0; x <= 100; x++) {
      const y = logarithmicReturn(x);
      const px = padding + (x / 100) * (width - 2 * padding);
      const py = height - padding - (y / 100) * (height - 2 * padding);
      if (x === 0) {
        ctx.moveTo(px, py);
      } else {
        ctx.lineTo(px, py);
      }
    }
    ctx.stroke();

    // Fill area under curve up to current value
    ctx.fillStyle = color.includes('var(') ? '#ff6600' : color;
    ctx.globalAlpha = 0.3;
    ctx.beginPath();
    ctx.moveTo(padding, height - padding);
    for (let x = 0; x <= value; x++) {
      const y = logarithmicReturn(x);
      const px = padding + (x / 100) * (width - 2 * padding);
      const py = height - padding - (y / 100) * (height - 2 * padding);
      ctx.lineTo(px, py);
    }
    const currentX = padding + (value / 100) * (width - 2 * padding);
    ctx.lineTo(currentX, height - padding);
    ctx.closePath();
    ctx.fill();
    ctx.globalAlpha = 1;

    // Draw current value marker
    const currentY = logarithmicReturn(value);
    const markerX = padding + (value / 100) * (width - 2 * padding);
    const markerY = height - padding - (currentY / 100) * (height - 2 * padding);

    ctx.fillStyle = color.includes('var(') ? '#ff6600' : color;
    ctx.beginPath();
    ctx.arc(markerX, markerY, 3, 0, Math.PI * 2);
    ctx.fill();
  }, [value, color]);

  const effectiveReturn = logarithmicReturn(value);

  return (
    <div className={`budget-slider ${disabled ? 'disabled' : ''}`}>
      <div className="slider-header">
        <span className="slider-label">{label}</span>
        <span className="slider-values">
          <span className="budget-value">{value}%</span>
          <span className="return-value" style={{ color }}>
            {effectiveReturn.toFixed(0)}% eff.
          </span>
        </span>
      </div>

      <div className="slider-container">
        <canvas
          ref={canvasRef}
          width={120}
          height={40}
          className="budget-curve"
        />
        <input
          type="range"
          min={0}
          max={100}
          value={value}
          onChange={(e) => onChange(parseInt(e.target.value))}
          disabled={disabled}
          className="budget-input"
          style={{
            '--slider-color': color,
          } as React.CSSProperties}
        />
      </div>
    </div>
  );
}

export default BudgetSlider;
