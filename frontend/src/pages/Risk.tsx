import React, { useMemo, useState } from 'react';
import { Typography, Box, Paper, TextField, MenuItem, Divider, Stack } from '@mui/material';

const Risk: React.FC = () => {
  const [account, setAccount] = useState(100000);
  const [riskPct, setRiskPct] = useState(1);
  const [entry, setEntry] = useState(100);
  const [stop, setStop] = useState(95);
  // Options
  const [optType, setOptType] = useState<'long_call' | 'long_put' | 'credit_put_spread' | 'credit_call_spread' | 'debit_call_spread' | 'debit_put_spread'>('long_call');
  const [premium, setPremium] = useState(2.5); // per contract, $
  const [contracts, setContracts] = useState(1);
  const [strike, setStrike] = useState(100);
  const [shortStrike, setShortStrike] = useState(95);
  // Greeks inputs
  const [underlying, setUnderlying] = useState(100); // S
  const [daysToExp, setDaysToExp] = useState(30); // days
  const [ivPct, setIvPct] = useState(25); // %
  const [ratePct, setRatePct] = useState(5); // %

  const { riskAmount, perShareRisk, positionSize, rMultiple1R, rMultiple2R } = useMemo(() => {
    const riskAmount = account * (riskPct / 100);
    const perShareRisk = Math.max(entry - stop, 0);
    const positionSize = perShareRisk > 0 ? Math.floor(riskAmount / perShareRisk) : 0;
    return {
      riskAmount,
      perShareRisk,
      positionSize,
      rMultiple1R: entry + perShareRisk,
      rMultiple2R: entry + perShareRisk * 2,
    };
  }, [account, riskPct, entry, stop]);

  const options = useMemo(() => {
    // All calculations in dollars; 1 contract = 100 shares
    const multiplier = 100;
    let maxLoss = 0;
    let maxGain = undefined as number | undefined;
    let breakeven = undefined as number | undefined;
    const totalPremium = premium * contracts * multiplier;
    switch (optType) {
      case 'long_call':
      case 'long_put':
        maxLoss = totalPremium;
        breakeven = optType === 'long_call' ? strike + premium : strike - premium;
        break;
      case 'credit_put_spread':
      case 'credit_call_spread': {
        const width = Math.abs(shortStrike - strike) * multiplier;
        const credit = totalPremium; // assume entered for net credit equal to premium input
        maxLoss = Math.max(width - credit, 0);
        maxGain = credit;
        break;
      }
      case 'debit_call_spread':
      case 'debit_put_spread': {
        const width = Math.abs(shortStrike - strike) * multiplier;
        const debit = totalPremium;
        maxLoss = debit;
        maxGain = Math.max(width - debit, 0);
        break;
      }
      default:
        maxLoss = totalPremium;
    }
    const allowedRisk = account * (riskPct / 100);
    const suggestedContracts = Math.max(0, Math.floor(allowedRisk / Math.max(maxLoss / Math.max(contracts, 1), 1)));
    return { maxLoss, maxGain, breakeven, allowedRisk, suggestedContracts };
  }, [optType, premium, contracts, strike, shortStrike, account, riskPct]);

  const greeks = useMemo(() => {
    // Only compute for single-leg longs
    if (optType !== 'long_call' && optType !== 'long_put') {
      return null;
    }
    const S = underlying;
    const K = strike;
    const T = Math.max(daysToExp, 0) / 365;
    const sigma = Math.max(ivPct / 100, 1e-6);
    const r = ratePct / 100;
    if (S <= 0 || K <= 0 || T <= 0) {
      return null;
    }
    const ln = Math.log(S / K);
    const d1 = (ln + (r + 0.5 * sigma * sigma) * T) / (sigma * Math.sqrt(T));
    const d2 = d1 - sigma * Math.sqrt(T);
    const Nd = (x: number) => 0.5 * (1 + erf(x / Math.SQRT2));
    const nd = (x: number) => Math.exp(-0.5 * x * x) / Math.sqrt(2 * Math.PI);
    // Approximate error function
    function erf(x: number) {
      // Abramowitz and Stegun approximation
      const sign = Math.sign(x);
      const a1 = 0.254829592, a2 = -0.284496736, a3 = 1.421413741, a4 = -1.453152027, a5 = 1.061405429, p = 0.3275911;
      const t = 1 / (1 + p * Math.abs(x));
      const y = 1 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-x * x);
      return sign * y;
    }
    const call = optType === 'long_call';
    const delta = call ? Nd(d1) : Nd(d1) - 1;
    const gamma = nd(d1) / (S * sigma * Math.sqrt(T));
    // Theta per year; convert to per day and per contract dollars
    const callTheta = -(S * nd(d1) * sigma) / (2 * Math.sqrt(T)) - r * K * Math.exp(-r * T) * Nd(d2);
    const putTheta = -(S * nd(d1) * sigma) / (2 * Math.sqrt(T)) + r * K * Math.exp(-r * T) * Nd(-d2);
    const thetaPerYear = call ? callTheta : putTheta;
    const thetaPerDayPerShare = thetaPerYear / 365;
    const vegaPerVol = S * nd(d1) * Math.sqrt(T); // per 1.0 (100%) vol
    // Normalize outputs per 1 contract (100 shares) and then scale by contracts
    const contractMult = 100;
    return {
      delta: delta * contractMult * contracts,
      gamma: gamma * contractMult * contracts,
      theta: thetaPerDayPerShare * contractMult * contracts, // $/day
      vega: (vegaPerVol / 100) * contractMult * contracts, // $ per 1% IV
    };
  }, [optType, underlying, strike, daysToExp, ivPct, ratePct, contracts]);

  return (
    <Box p={2}>
      <Typography variant="h5" gutterBottom>Risk</Typography>
      <Paper sx={{ p: 2, display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 2, mb: 2 }}>
        <TextField label="Account ($)" type="number" value={account} onChange={(e) => setAccount(Number(e.target.value))} />
        <TextField label="Risk %" type="number" value={riskPct} onChange={(e) => setRiskPct(Number(e.target.value))} />
        <TextField label="Entry" type="number" value={entry} onChange={(e) => setEntry(Number(e.target.value))} />
        <TextField label="Stop" type="number" value={stop} onChange={(e) => setStop(Number(e.target.value))} />
      </Paper>
      <Paper sx={{ p: 2, display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 2 }}>
        <Box>
          <Typography variant="body2" color="text.secondary">Risk Amount</Typography>
          <Typography variant="h6">${riskAmount.toFixed(2)}</Typography>
        </Box>
        <Box>
          <Typography variant="body2" color="text.secondary">Per-Share Risk</Typography>
          <Typography variant="h6">${perShareRisk.toFixed(2)}</Typography>
        </Box>
        <Box>
          <Typography variant="body2" color="text.secondary">Position Size</Typography>
          <Typography variant="h6">{positionSize} shares</Typography>
        </Box>
        <Box>
          <Typography variant="body2" color="text.secondary">1R Target</Typography>
          <Typography variant="h6">${rMultiple1R.toFixed(2)}</Typography>
        </Box>
        <Box>
          <Typography variant="body2" color="text.secondary">2R Target</Typography>
          <Typography variant="h6">${rMultiple2R.toFixed(2)}</Typography>
        </Box>
      </Paper>

      <Divider sx={{ my: 3 }} />
      <Typography variant="h6" gutterBottom>Options Risk</Typography>
      <Paper sx={{ p: 2, display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 2, mb: 2 }}>
        <TextField select label="Strategy" value={optType} onChange={(e) => setOptType(e.target.value as any)}>
          <MenuItem value="long_call">Long Call</MenuItem>
          <MenuItem value="long_put">Long Put</MenuItem>
          <MenuItem value="credit_put_spread">Credit Put Spread</MenuItem>
          <MenuItem value="credit_call_spread">Credit Call Spread</MenuItem>
          <MenuItem value="debit_call_spread">Debit Call Spread</MenuItem>
          <MenuItem value="debit_put_spread">Debit Put Spread</MenuItem>
        </TextField>
        <TextField label="Contracts" type="number" value={contracts} onChange={(e) => setContracts(Math.max(0, Number(e.target.value)))} />
        <TextField label="Premium ($)" type="number" value={premium} onChange={(e) => setPremium(Math.max(0, Number(e.target.value)))} />
        <TextField label="Long Strike" type="number" value={strike} onChange={(e) => setStrike(Number(e.target.value))} />
        <TextField label="Short Strike" type="number" value={shortStrike} onChange={(e) => setShortStrike(Number(e.target.value))} />
        <TextField label="Risk %" type="number" value={riskPct} onChange={(e) => setRiskPct(Number(e.target.value))} />
      </Paper>
      <Paper sx={{ p: 2, display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 2, mb: 2 }}>
        <TextField label="Underlying (S)" type="number" value={underlying} onChange={(e) => setUnderlying(Number(e.target.value))} />
        <TextField label="Days to Exp" type="number" value={daysToExp} onChange={(e) => setDaysToExp(Math.max(0, Number(e.target.value)))} />
        <TextField label="IV %" type="number" value={ivPct} onChange={(e) => setIvPct(Math.max(0, Number(e.target.value)))} />
        <TextField label="Rate %" type="number" value={ratePct} onChange={(e) => setRatePct(Number(e.target.value))} />
      </Paper>
      <Paper sx={{ p: 2, display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 2 }}>
        <Box>
          <Typography variant="body2" color="text.secondary">Max Loss</Typography>
          <Typography variant="h6">${options.maxLoss.toFixed(2)}</Typography>
        </Box>
        <Box>
          <Typography variant="body2" color="text.secondary">Max Gain</Typography>
          <Typography variant="h6">{options.maxGain !== undefined ? `$${options.maxGain.toFixed(2)}` : 'Unlimited/Variable'}</Typography>
        </Box>
        <Box>
          <Typography variant="body2" color="text.secondary">Breakeven</Typography>
          <Typography variant="h6">{options.breakeven !== undefined ? `$${options.breakeven.toFixed(2)}` : '-'}</Typography>
        </Box>
        <Box>
          <Typography variant="body2" color="text.secondary">Allowed Risk</Typography>
          <Typography variant="h6">${options.allowedRisk.toFixed(2)}</Typography>
        </Box>
        <Box>
          <Typography variant="body2" color="text.secondary">Suggested Contracts</Typography>
          <Typography variant="h6">{options.suggestedContracts}</Typography>
        </Box>
      </Paper>
      {greeks && (
        <Paper sx={{ p: 2, mt: 2 }}>
          <Typography variant="subtitle1" gutterBottom>Greeks (approx., per strategy selection)</Typography>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">Delta (per total contracts)</Typography>
              <Typography variant="h6">{greeks.delta.toFixed(2)}</Typography>
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary">Gamma</Typography>
              <Typography variant="h6">{greeks.gamma.toExponential(3)}</Typography>
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary">Theta ($/day)</Typography>
              <Typography variant="h6">{greeks.theta.toFixed(2)}</Typography>
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary">Vega ($ per 1% IV)</Typography>
              <Typography variant="h6">{greeks.vega.toFixed(2)}</Typography>
            </Box>
          </Stack>
        </Paper>
      )}
    </Box>
  );
};

export default Risk;
