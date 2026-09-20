# Android app source foundation

This is the Capacitor shell for the same Siddhi Vinayak web experience.

To produce an Android project in a Node/Android build environment:
1. `npm install`
2. `npx cap add android`
3. `npx cap sync android`
4. `npx cap open android`

Set the production HTTPS API base URL in the web frontend before packaging.
This chat environment does not have an Android SDK/signing key or Play Console credentials, so no APK/AAB is falsely claimed here.
