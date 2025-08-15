import React from 'react';
import { ProcessedFootprintBar } from '../types/footprint';
import styles from './FootprintChart.module.css';

interface FootprintChartProps {
  bars: ProcessedFootprintBar[];
  maxBars?: number;
  cellHeight?: number;
  fontSize?: number;
}

const FootprintChart: React.FC<FootprintChartProps> = ({ bars, maxBars = 30, cellHeight = 16, fontSize = 11 }) => {
  const displayBars = bars.slice(-maxBars);
  const maxVolume = Math.max(...displayBars.flatMap(b => b.levels.map(l => l.ask + l.bid)));

  return (
    <div className={styles.container}>
      {displayBars.map(bar => (
        <div key={bar.time} className={styles.barColumn}>
          {bar.levels.map(level => {
            const vol = level.ask + level.bid;
            const intensity = maxVolume ? (vol / maxVolume) : 0;
            const delta = level.delta || 0;
            let imbalanceClass = '';
            if (level.imbalanceUp) { imbalanceClass = styles.imbalanceUp; }
            if (level.imbalanceDown) { imbalanceClass = styles.imbalanceDown; }
            return (
              <div
                key={level.price}
                className={`${styles.level} ${imbalanceClass}`}
                style={{
                  height: cellHeight,
                  lineHeight: `${cellHeight}px`,
                  fontSize,
                  background: `rgba(64,128,64,${0.15 + 0.55 * intensity})`
                }}
              >
                <span className={styles.price}>{level.price}</span>
                <span className={styles.bid}>{level.bid}</span>
                <span className={styles.ask}>{level.ask}</span>
                <span className={delta >= 0 ? styles.deltaPos : styles.deltaNeg}>{delta}</span>
              </div>
            );
          })}
        </div>
      ))}
    </div>
  );
};

export default FootprintChart;
