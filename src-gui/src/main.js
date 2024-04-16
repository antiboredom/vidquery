import "./app.css";
import App from "./App.svelte";

window.addEventListener("pywebviewready", async function() {
  const app = new App({
    target: document.getElementById("app"),
  });
});

// export default app
