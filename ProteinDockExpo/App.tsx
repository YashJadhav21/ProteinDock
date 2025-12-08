import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { PaperProvider, configureFonts } from 'react-native-paper';
import { AuthProvider } from './src/contexts/AuthContext';
import { AppNavigator } from './src/navigation/AppNavigator';
import { MaterialCommunityIcons } from '@expo/vector-icons';

// Configure React Native Paper to use Expo vector icons
const theme = {
  fonts: configureFonts(),
};

export default function App() {
  return (
    <PaperProvider 
      theme={theme}
      settings={{
        icon: (props: any) => <MaterialCommunityIcons {...props} />,
      }}
    >
      <AuthProvider>
        <AppNavigator />
        <StatusBar style="auto" />
      </AuthProvider>
    </PaperProvider>
  );
}
