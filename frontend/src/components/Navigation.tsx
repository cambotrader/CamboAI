import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { Link } from 'react-router-dom';

const Navigation = () => {
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component={Link} to="/" sx={{ textDecoration: 'none', color: 'white' }}>
          Cambo AI
        </Typography>
        <Box sx={{ flexGrow: 1, ml: 2 }}>
          <Button color="inherit" component={Link} to="/charts">Charts</Button>
          <Button color="inherit" component={Link} to="/analysis">Analysis</Button>
          <Button color="inherit" component={Link} to="/education">Education</Button>
          <Button color="inherit" component={Link} to="/journal">Journal</Button>
          <Button color="inherit" component={Link} to="/coach">Coach/Therapy</Button>
          <Button color="inherit" component={Link} to="/war-room">War Room</Button>
          <Button color="inherit" component={Link} to="/community">Community</Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navigation;
