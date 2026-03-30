import React from "react";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import useMediaQuery from "@mui/material/useMediaQuery";

export default function MyThemeProvider(props: any) {
  const prefersDarkMode = useMediaQuery("(prefers-color-scheme: dark)");

  const theme = React.useMemo(
    () =>
      createTheme({ palette: { mode: prefersDarkMode ? "dark" : "light" } }),
    [prefersDarkMode],
  );

  return <ThemeProvider theme={theme}>{props.children}</ThemeProvider>;
}
