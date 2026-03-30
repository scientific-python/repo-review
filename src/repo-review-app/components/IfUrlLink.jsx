import React from "react";
import { Typography } from "@mui/material";

export default function IfUrlLink({ name, url, color }) {
  if (url) {
    return (
      <Typography
        sx={{ display: "inline" }}
        variant="body2"
        color={color}
        component="a"
        href={url}
        target="_blank"
        rel="noopener noreferrer"
      >
        {name}
      </Typography>
    );
  }
  return (
    <Typography sx={{ display: "inline" }} component="span" variant="body2" color={color}>
      {name}
    </Typography>
  );
}
