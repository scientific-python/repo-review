const FONT_URL =
  "https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap";
const INJECTED_ATTR = "data-repo-review-roboto";

export function injectFonts(): void {
  if (document.querySelector(`link[${INJECTED_ATTR}]`)) return;

  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = FONT_URL;
  link.setAttribute(INJECTED_ATTR, "");
  document.head.appendChild(link);
}
