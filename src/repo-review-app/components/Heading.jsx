import React from "react";
import { Box, AppBar, Toolbar, Typography, Button } from "@mui/material";

export default function Heading(props) {
  return (
    <Box sx={{ flexGrow: 1, mb: 2 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Repo-Review
          </Typography>
          <Button href="https://github.com/scientific-python/repo-review" color="inherit">
            Source
          </Button>
        </Toolbar>
      </AppBar>
    </Box>
  );
}
