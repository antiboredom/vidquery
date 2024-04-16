<script>
  import { onMount } from "svelte";

  const offset = 0.1;

  export let clips = [];
  let video;
  let frame;
  let current = 0;
  let currentClip;
  let started = false;

  onMount(() => {
    if (clips.length > 0) {
      currentClip = clips[current];
      video.src = currentClip.path;
    }

    return () => {
      cancelAnimationFrame(frame);
    };
  });

  async function previewEdl() {
    await pywebview.api.previewMPV(clips);
  }

  function start() {
    if (!started) {
      started = true;
      frame = requestAnimationFrame(step);
    }
  }

  function step() {
    if (!video.src.endsWith(currentClip.path)) {
      video.src = currentClip.path;
      video.play();
    }
    if (video.currentTime < currentClip.start) {
      video.currentTime = currentClip.start;
    } else if (video.currentTime > currentClip.end) {
      current++;
      if (current >= clips.length) {
        current = 0;
      }
      currentClip = clips[current];
    }
    frame = requestAnimationFrame(step);
  }
</script>

<button on:click={previewEdl}>Open in MPV</button>
<video bind:this={video} on:play={start} controls></video>
