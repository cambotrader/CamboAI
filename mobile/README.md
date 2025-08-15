# CamboStation Vision Mobile App

## 🚀 Free Mobile App Development Setup

This is a React Native Expo app that provides mobile access to your CamboStation Vision trading platform.

### 📱 Features
- Real-time market data and charts
- Trading interface
- Portfolio management
- AI-powered analytics
- Cross-platform (iOS & Android)

## 🆓 Free Development & Distribution

### Prerequisites (All Free)
1. **Node.js** (Free) - Download from nodejs.org
2. **Expo CLI** (Free) - `npm install -g @expo/cli`
3. **EAS CLI** (Free) - `npm install -g eas-cli`
4. **Expo Account** (Free) - Sign up at expo.dev

### Setup Instructions

1. **Install Dependencies**
```bash
cd mobile
npm install
```

2. **Start Development Server**
```bash
npm start
```

3. **Test on Device (Free)**
   - Install "Expo Go" app on your phone (iOS/Android)
   - Scan QR code from terminal
   - App runs instantly on your device!

### 🔨 Building APK & iOS Apps (100% Free)

#### Android APK (Free)
```bash
# Login to Expo (free account)
eas login

# Build APK (free with limitations)
eas build --platform android --profile preview

# Download APK when build completes
# Install directly on Android devices
```

#### iOS App (Free with Apple Developer Account)
```bash
# Build iOS app (requires Apple Developer account - $99/year)
eas build --platform ios --profile production

# Or build for iOS Simulator (completely free)
eas build --platform ios --profile development
```

### 🌐 Alternative Free Options

#### 1. PWA (Progressive Web App) - 100% Free
Convert to PWA for app-like experience:
```bash
# Add to existing web build
npm run build:web
# Users can "Add to Home Screen" on mobile browsers
```

#### 2. Capacitor (Free)
```bash
# Install Capacitor
npm install @capacitor/core @capacitor/cli
npm install @capacitor/android @capacitor/ios

# Build for mobile
npx cap add android
npx cap add ios
npx cap run android
```

### 📦 Free Distribution Options

#### Android
1. **Direct APK Distribution** (Free)
   - Share APK file directly
   - Users enable "Unknown Sources"
   - Install manually

2. **Google Play Store** ($25 one-time fee)
   - Professional distribution
   - Automatic updates

#### iOS
1. **TestFlight** (Free with Apple Developer)
   - Beta testing platform
   - Up to 10,000 testers

2. **App Store** (Free with Apple Developer)
   - Professional distribution

### 🔧 Configuration

#### Backend Connection
Update API endpoints in screens to match your backend:
```typescript
// Replace localhost with your backend URL
const API_BASE = 'https://your-backend-url.com/api';
```

#### Customization
- Update `app.json` with your app details
- Replace icons in `assets/` folder
- Modify colors and branding in components

### 🚀 Deployment Options (Free)

#### 1. Expo Updates (Free)
```bash
# Push updates instantly to users
eas update --branch production
```

#### 2. GitHub Actions (Free)
```yaml
# .github/workflows/mobile-build.yml
name: Build Mobile App
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: npm install
      - run: eas build --platform all --non-interactive
```

### 💡 Pro Tips for Free Development

1. **Use Expo Go** for instant testing
2. **Leverage EAS Build** free tier (limited builds/month)
3. **Use GitHub Actions** for CI/CD
4. **Consider PWA** for web-based mobile experience
5. **Use TestFlight** for iOS beta testing

### 🔗 Useful Links
- [Expo Documentation](https://docs.expo.dev/)
- [EAS Build](https://docs.expo.dev/build/introduction/)
- [React Native](https://reactnative.dev/)
- [Expo Go App](https://expo.dev/client)

### 📞 Support
For issues or questions, check:
- Expo Discord Community (Free)
- Stack Overflow
- GitHub Issues