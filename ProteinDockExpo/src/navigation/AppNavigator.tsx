import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

import { useAuth } from '../contexts/AuthContext';
import LoginScreen from '../screens/LoginScreen';
import RegisterScreen from '../screens/RegisterScreen';
import HomeScreen from '../screens/HomeScreen';
import ProteinScreen from '../screens/ProteinScreen';
import LigandScreen from '../screens/LigandScreen';
import DockingScreen from '../screens/DockingScreen';
import DockingConfigScreen from '../screens/DockingConfigScreen';
import ResultsScreen from '../screens/ResultsScreen';
import ViewerScreen from '../screens/ViewerScreen';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

const MainTabs = () => (
  <Tab.Navigator
    screenOptions={({ route }) => ({
      tabBarIcon: ({ color, size }) => {
        let iconName = 'home';
        if (route.name === 'Home') iconName = 'home';
        else if (route.name === 'Protein') iconName = 'molecule';
        else if (route.name === 'Ligand') iconName = 'flask';
        else if (route.name === 'Docking') iconName = 'rocket-launch';
        
        return <Icon name={iconName} size={size} color={color} />;
      },
      tabBarActiveTintColor: '#6200ee',
      tabBarInactiveTintColor: 'gray',
      headerShown: false,
    })}>
    <Tab.Screen name="Home" component={HomeScreen} />
    <Tab.Screen name="Protein" component={ProteinScreen} />
    <Tab.Screen name="Ligand" component={LigandScreen} />
    <Tab.Screen name="Docking" component={DockingScreen} />
  </Tab.Navigator>
);

export const AppNavigator = () => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return null; // Or a loading screen
  }

  return (
    <NavigationContainer>
      {user ? (
        <Stack.Navigator screenOptions={{ headerShown: false }}>
          <Stack.Screen name="MainTabs" component={MainTabs} />
          <Stack.Screen 
            name="DockingConfig" 
            component={DockingConfigScreen} 
            options={{ 
              headerShown: true, 
              title: 'Docking Configuration',
              headerStyle: { backgroundColor: '#6200ee' },
              headerTintColor: '#fff'
            }} 
          />
          <Stack.Screen 
            name="Results" 
            component={ResultsScreen} 
            options={{ 
              headerShown: true, 
              title: 'Docking Results',
              headerStyle: { backgroundColor: '#6200ee' },
              headerTintColor: '#fff'
            }} 
          />
          <Stack.Screen 
            name="Viewer" 
            component={ViewerScreen} 
            options={{ 
              headerShown: false,
              presentation: 'modal'
            }} 
          />
        </Stack.Navigator>
      ) : (
        <Stack.Navigator screenOptions={{ headerStyle: { backgroundColor: '#6200ee' }, headerTintColor: '#fff' }}>
          <Stack.Screen name="Login" component={LoginScreen} />
          <Stack.Screen name="Register" component={RegisterScreen} />
        </Stack.Navigator>
      )}
    </NavigationContainer>
  );
};
