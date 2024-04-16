<script>
  import { onMount } from "svelte";
  import Player from "./lib/Player.svelte";

  let videos = [];
  let searchResults = [];
  let route = "home";
  let q = "";
  let hasSearched = false;

  onMount(async () => {
    videos = await pywebview.api.listvideos();
  });

  async function doQuery() {
    console.log(q);
    hasSearched = true;
    searchResults = await pywebview.api.query([], q);
    console.log(searchResults);
  }
</script>

<nav>
  <a href="#search">Search</a>
  <a href="#search">Videos</a>
  <a href="#search">Import</a>
</nav>
<main>
  <form on:submit|preventDefault={doQuery}>
    <input type="text" bind:value={q} />
    <button type="submit">Search</button>
  </form>

  <div>
    {#if searchResults.length > 0}
      <Player clips={searchResults} />
    {/if}
  </div>
</main>

<style>
</style>
