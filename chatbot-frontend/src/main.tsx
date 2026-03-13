import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./index.css";

// Force dark mode programmatically so HMR and React fully pick it up
document.documentElement.classList.add("dark");

createRoot(document.getElementById("root")!).render(<App />);
