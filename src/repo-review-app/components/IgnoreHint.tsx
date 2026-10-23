import { Alert, AlertTitle, Box, IconButton } from "@mui/material";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import TipsAndUpdatesOutlinedIcon from "@mui/icons-material/TipsAndUpdatesOutlined";
import type { CheckItem } from "../repo-review-app";
import { ignoreToml } from "../utils/ignore";

interface IgnoreHintProps {
  results: Record<string, CheckItem[]>;
  onCopy: (toml: string) => void;
}

export default function IgnoreHint(props: IgnoreHintProps) {
  const toml = ignoreToml(props.results);
  if (!toml) return null;
  return (
    <Box sx={{ px: 2, py: 3 }}>
      <Alert
        severity="info"
        variant="outlined"
        icon={<TipsAndUpdatesOutlinedIcon />}
        action={
          <IconButton
            onClick={() => props.onCopy(toml)}
            size="small"
            color="inherit"
            aria-label="Copy ignore config"
          >
            <ContentCopyIcon fontSize="small" />
          </IconButton>
        }
        sx={{ "& .MuiAlert-message": { minWidth: 0, flexGrow: 1 } }}
      >
        <AlertTitle>Tip</AlertTitle>
        Not every check fits every project. To ignore the failed checks, add
        this to <code>pyproject.toml</code>:
        <Box
          component="pre"
          sx={{
            mt: 1,
            mb: 0,
            p: 1.5,
            borderRadius: 1,
            bgcolor: "action.hover",
            color: "text.primary",
            whiteSpace: "pre-wrap",
            overflowX: "auto",
          }}
        >
          <code>{toml}</code>
        </Box>
      </Alert>
    </Box>
  );
}
