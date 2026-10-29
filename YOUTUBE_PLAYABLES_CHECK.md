# YouTube Playables - Merge Battle (youtube build only)

| Playables item | Status | How |
|---|---|---|
| SDK from youtube.com/game_api/v1 only, no other network requests | Done | Font is embedded in the page, nothing else is fetched. |
| `firstFrameReady()` and `gameReady()` | Done | Called on the first drawn frame once saved data is loaded. |
| Save data with `saveData` / `loadData` | Done | One tiny JSON string (no localStorage). |
| `onPause` / `onResume` | Done | Game and audio pause and resume. |
| `isAudioEnabled` / `onAudioEnabledChange` | Done | Follows YouTube's audio state. |
| `engagement.sendScore` | Done | Sends the level reached when a level is cleared. |
| `ads.requestInterstitialAd()` | Done | Between levels only; game and audio paused while it shows. |
| Rewarded ads | Not available | The portal has none, so no "watch ad" button is shown. |
| `health.logError()` | Done | Called on window errors. |
| Only what YouTube needs | Done | No mute button, skip button or keyboard shortcuts in this build. |
| Also works outside YouTube | Done | If the page is opened directly (own site, Vercel), the YouTube SDK is ignored: sound stays on and progress is saved in the browser. |
