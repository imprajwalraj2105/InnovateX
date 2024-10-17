import React from 'react';
import { StyleSheet } from 'react-native';
import { createStackNavigator } from '@react-navigation/stack';
import { NavigationContainer } from '@react-navigation/native';
import Login from './components/Login';
import Home from './components/Home';
import Signup from './components/Signup';
import BottomTab from './components/BottomTab';

const Stack = createStackNavigator();

const App = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName='Login'>
        <Stack.Screen 
          name="Login" 
          component={Login} 
          options={{ headerShown: false }} 
        />
        <Stack.Screen 
          name='Home' 
          component={Home} 
          options={{ 
            headerShown: true,
            title: 'Welcome Home', // Custom header title
            headerStyle: styles.header,
            headerTintColor: '#fff',
            headerTitleStyle: styles.headerTitle,
          }} 
        />
        <Stack.Screen 
          name='Signup' 
          component={Signup} 
          options={{ headerShown: false }} 
        />
        <Stack.Screen 
          name='Main' 
          component={BottomTab} 
          options={{ headerShown: false }} 
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

const styles = StyleSheet.create({
  header: {
    backgroundColor: '#2196F3', // Custom header background color
    elevation: 0, // Remove shadow on Android
    shadowOpacity: 0, // Remove shadow on iOS
  },
  headerTitle: {
    fontWeight: 'bold',
    fontSize: 18,
  },
});

export default App;
