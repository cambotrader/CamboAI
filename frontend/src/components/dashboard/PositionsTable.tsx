import React from 'react';
import { DataGrid, GridColDef, GridCellParams, GridValueFormatterParams } from '@mui/x-data-grid';
import { Paper, Typography } from '@mui/material';

interface Position {
  id: number;
  symbol: string;
  quantity: number;
  entryPrice: number;
  currentPrice: number;
  pnl: number;
}

interface PositionsTableProps {
  positions: Position[];
}

const columns: GridColDef[] = [
  { field: 'symbol', headerName: 'Symbol', flex: 1 },
  { field: 'quantity', headerName: 'Quantity', flex: 1 },
  { 
    field: 'entryPrice', 
    headerName: 'Entry Price', 
    flex: 1,
    valueFormatter: (params: GridValueFormatterParams) => {
      const value = Number(params.value ?? 0);
      return `$${value.toFixed(2)}`;
    }
  },
  { 
    field: 'currentPrice', 
    headerName: 'Current Price', 
    flex: 1,
    valueFormatter: (params: GridValueFormatterParams) => {
      const value = Number(params.value ?? 0);
      return `$${value.toFixed(2)}`;
    }
  },
  { 
    field: 'pnl', 
    headerName: 'P&L', 
    flex: 1,
    valueFormatter: (params: GridValueFormatterParams) => {
      const value = Number(params.value ?? 0);
      return `$${value.toFixed(2)}`;
    },
    cellClassName: (params: GridCellParams) => {
      const value = Number(params.value ?? 0);
      return value >= 0 ? 'positive' : 'negative';
    }
  }
];

const PositionsTable: React.FC<PositionsTableProps> = ({ positions }) => {
  return (
    <Paper elevation={2} sx={{ p: 2, height: '400px' }}>
      <Typography variant="h6" gutterBottom>
        Current Positions
      </Typography>
      <DataGrid
        rows={positions}
        columns={columns}
        initialState={{
          pagination: {
            paginationModel: { page: 0, pageSize: 5 },
          },
        }}
        pageSizeOptions={[5]}
        disableRowSelectionOnClick
        sx={{
          '& .positive': {
            color: 'success.main',
            fontWeight: 'bold'
          },
          '& .negative': {
            color: 'error.main',
            fontWeight: 'bold'
          }
        }}
      />
    </Paper>
  );
};

export default PositionsTable;
