# AI Shopping Compare Flutter App

This is the mobile/web client for the AI shopping comparison system.

## Local run

```bash
flutter pub get
flutter run
```

Default backend URLs:

- Web / Windows / iOS / macOS: `http://127.0.0.1:8000`
- Android emulator: `http://10.0.2.2:8000`

Override the backend URL:

```bash
flutter run --dart-define=API_BASE_URL=http://127.0.0.1:8000
```

Use mock data after API failure during local development:

```bash
flutter run --dart-define=USE_MOCK_ON_API_FAILURE=true
```
