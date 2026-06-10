import React from "react";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import useMediaQuery from "@mui/material/useMediaQuery";

// Tailwind stone palette used by mystmd for dark mode backgrounds.
// Applied when the host page explicitly controls dark mode via a CSS class.
const STONE_900 = "#1c1917";
const STONE_800 = "#292524";

interface PageTheme {
  darkMode: boolean;
  hostControlled: boolean;
}

function usePageTheme(): PageTheme {
  const getPageClass = (): boolean | null => {
    if (typeof document === "undefined") return null;
    const { classList } = document.documentElement;
    if (classList.contains("dark")) return true;
    if (classList.contains("light")) return false;
    return null;
  };

  const [pageClass, setPageClass] = React.useState<boolean | null>(
    getPageClass,
  );

  React.useEffect(() => {
    if (
      typeof document === "undefined" ||
      typeof MutationObserver === "undefined"
    )
      return;
    const observer = new MutationObserver(() => setPageClass(getPageClass()));
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["class"],
    });
    return () => observer.disconnect();
  }, []);

  return { darkMode: pageClass ?? false, hostControlled: pageClass !== null };
}

export default function MyThemeProvider(props: { children: React.ReactNode }) {
  const { darkMode: pageDark, hostControlled } = usePageTheme();
  const prefersDarkMode = useMediaQuery("(prefers-color-scheme: dark)");

  // Host page class (e.g. mystmd/Tailwind) takes priority over OS preference.
  const isDarkMode = hostControlled ? pageDark : prefersDarkMode;

  const theme = React.useMemo(
    () =>
      createTheme({
        palette: {
          mode: isDarkMode ? "dark" : "light",
          // When the host page controls the theme, match its stone palette to
          // avoid a jarring color contrast between the widget and the page.
          ...(isDarkMode &&
            hostControlled && {
              background: {
                default: STONE_900,
                paper: STONE_800,
              },
            }),
        },
      }),
    [isDarkMode, hostControlled],
  );

  return <ThemeProvider theme={theme}>{props.children}</ThemeProvider>;
}
