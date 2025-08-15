import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  Alert,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tooltip,
  IconButton
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  TrendingDown,
  Warning,
  Info,
  Assessment,
  Security,
  Speed,
  ShowChart,
  Refresh
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar } from 'recharts';
import { apiService } from '../services/api';

interface RiskMetrics {
  value_at_risk_95: number;
  value_at_risk_99: number;
  conditional_var_95: number;
  conditional_var_99: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  information_ratio: number;
  maximum_drawdown: number;
  drawdown_duration: number;
  volatility: number;
  beta: number;
  alpha: number;
}

interface PerformanceMetrics {
  total_return: number;
  annualized_return: number;
  win_rate: number;
  average_win: number;
  average_loss: number;
  profit_factor: number | null;
  best_day: number;
  worst_day: number;
}

interface RiskAlert {
  id: string;
  type: string;
  severity: string;
  title: string;
  message: string;
  value: number;
  threshold: number;
  created_at: string;
  is_active: boolean;
}

interface RiskAnalysis {
  risk_metrics: RiskMetrics;
  performance_metrics: PerformanceMetrics;
  portfolio_stats: any;
  risk_assessment: string;
  recommendations: string[];
}

interface RiskManagementProps {
  portfolioId: string;
}

const RiskManagement: React.FC<RiskManagementProps> = ({ portfolioId }) => {
  const [riskAnalysis, setRiskAnalysis] = useState<RiskAnalysis | null>(null);
  const [alerts, setAlerts] = useState<RiskAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [stressTestOpen, setStressTestOpen] = useState(false);
  const [stressResults, setStressResults] = useState<any>(null);
  const [analysisPeriod, setAnalysisPeriod] = useState(90);

  useEffect(() => {
    loadRiskData();
  }, [portfolioId, analysisPeriod]);

  const loadRiskData = async () => {
    try {
      setLoading(true);
      const [analysisResponse, alertsResponse] = await Promise.all([
        apiService.get(`/api/risk/portfolio/${portfolioId}/analysis?days=${analysisPeriod}`),
        apiService.get(`/api/risk/portfolio/${portfolioId}/alerts`)
      ]);

      setRiskAnalysis(analysisResponse.data.risk_analysis);
      setAlerts(alertsResponse.data.alerts);
    } catch (error) {
      console.error('Error loading risk data:', error);
    } finally {
      setLoading(false);
    }
  };

  const runStressTest = async () => {
    try {
      const response = await apiService.post(`/api/risk/portfolio/${portfolioId}/stress-test`);
      setStressResults(response.data);
      setStressTestOpen(true);
    } catch (error) {
      console.error('Error running stress test:', error);
    }
  };

  const getRiskLevelColor = (assessment: string) => {
    switch (assessment) {
      case 'VERY_LOW': return 'success';
      case 'LOW': return 'info';
      case 'MODERATE': return 'warning';
      case 'HIGH': return 'error';
      case 'VERY_HIGH': return 'error';
      default: return 'default';
    }
  };

  const getAlertSeverityColor = (severity: string) => {
    switch (severity) {
      case 'HIGH': return 'error';
      case 'MEDIUM': return 'warning';
      case 'LOW': return 'info';
      default: return 'default';
    }
  };

  const formatPercentage = (value: number) => `${(value * 100).toFixed(2)}%`;
  const formatRatio = (value: number) => value.toFixed(2);

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
        <Typography sx={{ mt: 2 }}>Loading risk analysis...</Typography>
      </Box>
    );
  }

  if (!riskAnalysis) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="info">No risk data available for this portfolio.</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Risk Management
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<Assessment />}
            onClick={runStressTest}
          >
            Stress Test
          </Button>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={loadRiskData}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {/* Risk Assessment Overview */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Security sx={{ mr: 1 }} />
                <Typography variant="h6">Risk Assessment</Typography>
              </Box>
              <Chip
                label={riskAnalysis.risk_assessment.replace('_', ' ')}
                color={getRiskLevelColor(riskAnalysis.risk_assessment) as any}
                sx={{ mb: 2 }}
              />
              <Typography variant="body2" color="text.secondary">
                Based on Sharpe ratio, drawdown, and volatility analysis
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Warning sx={{ mr: 1 }} />
                <Typography variant="h6">Active Alerts</Typography>
              </Box>
              <Typography variant="h3" color="error">
                {alerts.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Risk alerts requiring attention
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <ShowChart sx={{ mr: 1 }} />
                <Typography variant="h6">Sharpe Ratio</Typography>
              </Box>
              <Typography variant="h3" color={riskAnalysis.risk_metrics.sharpe_ratio >= 1 ? "success.main" : "warning.main"}>
                {formatRatio(riskAnalysis.risk_metrics.sharpe_ratio)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Risk-adjusted returns
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Alerts Section */}
      {alerts.length > 0 && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Risk Alerts
          </Typography>
          {alerts.map((alert, index) => (
            <Alert
              key={alert.id}
              severity={getAlertSeverityColor(alert.severity) as any}
              sx={{ mb: 1 }}
              action={
                <Tooltip title="Alert Details">
                  <IconButton size="small">
                    <Info />
                  </IconButton>
                </Tooltip>
              }
            >
              <Typography variant="subtitle2">{alert.title}</Typography>
              <Typography variant="body2">{alert.message}</Typography>
            </Alert>
          ))}
        </Paper>
      )}

      {/* Risk Metrics */}
      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">Risk Metrics</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Metric</TableCell>
                  <TableCell align="right">Value</TableCell>
                  <TableCell>Description</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                <TableRow>
                  <TableCell>Value at Risk (95%)</TableCell>
                  <TableCell align="right">{formatPercentage(riskAnalysis.risk_metrics.value_at_risk_95)}</TableCell>
                  <TableCell>Maximum expected daily loss (95% confidence)</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Conditional VaR (95%)</TableCell>
                  <TableCell align="right">{formatPercentage(riskAnalysis.risk_metrics.conditional_var_95)}</TableCell>
                  <TableCell>Expected loss when VaR threshold is exceeded</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Maximum Drawdown</TableCell>
                  <TableCell align="right">{formatPercentage(Math.abs(riskAnalysis.risk_metrics.maximum_drawdown))}</TableCell>
                  <TableCell>Largest peak-to-trough decline</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Volatility (Annualized)</TableCell>
                  <TableCell align="right">{formatPercentage(riskAnalysis.risk_metrics.volatility)}</TableCell>
                  <TableCell>Standard deviation of returns</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Beta</TableCell>
                  <TableCell align="right">{formatRatio(riskAnalysis.risk_metrics.beta)}</TableCell>
                  <TableCell>Market sensitivity</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Alpha</TableCell>
                  <TableCell align="right">{formatPercentage(riskAnalysis.risk_metrics.alpha)}</TableCell>
                  <TableCell>Excess return vs. market</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Sortino Ratio</TableCell>
                  <TableCell align="right">{formatRatio(riskAnalysis.risk_metrics.sortino_ratio)}</TableCell>
                  <TableCell>Downside risk-adjusted returns</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        </AccordionDetails>
      </Accordion>

      {/* Performance Metrics */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">Performance Metrics</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>Returns</Typography>
                  <Typography variant="body2">
                    Total Return: {formatPercentage(riskAnalysis.performance_metrics.total_return)}
                  </Typography>
                  <Typography variant="body2">
                    Annualized Return: {formatPercentage(riskAnalysis.performance_metrics.annualized_return)}
                  </Typography>
                  <Typography variant="body2">
                    Best Day: {formatPercentage(riskAnalysis.performance_metrics.best_day)}
                  </Typography>
                  <Typography variant="body2">
                    Worst Day: {formatPercentage(riskAnalysis.performance_metrics.worst_day)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>Trading Statistics</Typography>
                  <Typography variant="body2">
                    Win Rate: {formatPercentage(riskAnalysis.performance_metrics.win_rate)}
                  </Typography>
                  <Typography variant="body2">
                    Average Win: {formatPercentage(riskAnalysis.performance_metrics.average_win)}
                  </Typography>
                  <Typography variant="body2">
                    Average Loss: {formatPercentage(riskAnalysis.performance_metrics.average_loss)}
                  </Typography>
                  <Typography variant="body2">
                    Profit Factor: {riskAnalysis.performance_metrics.profit_factor ? formatRatio(riskAnalysis.performance_metrics.profit_factor) : 'N/A'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </AccordionDetails>
      </Accordion>

      {/* Recommendations */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">Recommendations</Typography>
        </AccordionSummary>
        <AccordionDetails>
          {riskAnalysis.recommendations.map((recommendation, index) => (
            <Alert key={index} severity="info" sx={{ mb: 1 }}>
              {recommendation}
            </Alert>
          ))}
        </AccordionDetails>
      </Accordion>

      {/* Stress Test Dialog */}
      <Dialog
        open={stressTestOpen}
        onClose={() => setStressTestOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Stress Test Results</DialogTitle>
        <DialogContent>
          {stressResults && (
            <Box>
              <Typography variant="body1" sx={{ mb: 2 }}>
                Portfolio Value: ${stressResults.current_portfolio_value?.toFixed(2)}
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Scenario</TableCell>
                      <TableCell align="right">Impact</TableCell>
                      <TableCell align="right">Estimated Loss</TableCell>
                      <TableCell>Severity</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {Object.entries(stressResults.stress_test_results || {}).map(([scenario, results]: [string, any]) => (
                      <TableRow key={scenario}>
                        <TableCell>{scenario.replace('_', ' ').toUpperCase()}</TableCell>
                        <TableCell align="right">{formatPercentage(results.portfolio_impact)}</TableCell>
                        <TableCell align="right">${results.estimated_loss?.toFixed(2)}</TableCell>
                        <TableCell>
                          <Chip
                            label={results.scenario_severity}
                            color={results.scenario_severity === 'HIGH' ? 'error' : results.scenario_severity === 'MEDIUM' ? 'warning' : 'success'}
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setStressTestOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default RiskManagement;
