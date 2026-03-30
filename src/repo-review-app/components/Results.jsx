import React from "react";
import { List, ListItem, ListItemIcon, ListItemText, ListSubheader, Icon, Typography, Box } from "@mui/material";
import IfUrlLink from "./IfUrlLink";

export default function Results(props) {
  const output = [];
  for (const key in props.results) {
    const inner_results = props.results[key];
    const results_components = inner_results.map((result) => {
      const text_color =
        result.state === false ? "error.main" : result.state === true ? "text.primary" : "info.main";
      const details = result.state === false ? <span dangerouslySetInnerHTML={{ __html: result.err_msg }} /> : null;
      const color = result.state === false ? "error" : result.state === true ? "success" : "info";
      const icon = (
        <Icon color={color}>{result.state === false ? "report" : result.state === true ? "check_box" : "info"}</Icon>
      );

      const skipped = (
        <Typography sx={{ display: "inline" }} component="span" variant="body2" color="text.disabled">
          {` [skipped] ${result.skip_reason}`}
        </Typography>
      );
      const msg = (
        <>
          <IfUrlLink name={result.name} url={result.url} color={text_color} />
          <IfUrlLink name={": "} url={""} color={text_color} />
          <>
            <Typography sx={{ display: "inline" }} component="span" color={text_color}>
              {result.description}
            </Typography>
          </>
          {result.state === undefined && skipped}
        </>
      );
      return (
        <ListItem disablePadding key={result.name}>
          <ListItemIcon>{icon}</ListItemIcon>
          <ListItemText primary={msg} secondary={details} />
        </ListItem>
      );
    });

    output.push(
      <li key={`section-${key}`}>
        <ul>
          <ListSubheader>{props.families[key].name}</ListSubheader>
          {props.families[key].description && (
            <ListItem>
              <span dangerouslySetInnerHTML={{ __html: props.families[key].description }} />
            </ListItem>
          )}
          {results_components}
        </ul>
      </li>
    );
  }

  return (
    <Box sx={{ bgcolor: "background.paper" }}>
      <List subheader={<li />} sx={{ overflow: "auto" }}>
        {output}
      </List>
    </Box>
  );
}
