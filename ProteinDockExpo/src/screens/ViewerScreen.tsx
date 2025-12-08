import React, { useState, useEffect } from 'react';
import { View, StyleSheet, Alert } from 'react-native';
import { WebView } from 'react-native-webview';
import { ActivityIndicator, Appbar, Text, Card } from 'react-native-paper';

const ViewerScreen = ({ route, navigation }: any) => {
  const { viewerUrl, expiresAt } = route.params;
  const [loading, setLoading] = useState(true);
  const [expired, setExpired] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState<string>('');

  useEffect(() => {
    // Check if already expired
    const expiryTime = new Date(expiresAt);
    if (expiryTime <= new Date()) {
      setExpired(true);
      return;
    }

    // Update countdown every second
    const interval = setInterval(() => {
      const now = new Date();
      const diff = expiryTime.getTime() - now.getTime();
      
      if (diff <= 0) {
        setExpired(true);
        clearInterval(interval);
        Alert.alert(
          'Viewer Expired',
          'This 3D visualization has expired. Please run a new docking job.',
          [{ text: 'OK', onPress: () => navigation.goBack() }]
        );
      } else {
        const minutes = Math.floor(diff / 60000);
        const seconds = Math.floor((diff % 60000) / 1000);
        setTimeRemaining(`${minutes}m ${seconds}s`);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [expiresAt]);

  const handleError = (syntheticEvent: any) => {
    const { nativeEvent } = syntheticEvent;
    console.error('[Viewer] WebView error:', nativeEvent);
    Alert.alert(
      'Loading Error',
      'Failed to load 3D viewer. The visualization may have expired.',
      [{ text: 'OK', onPress: () => navigation.goBack() }]
    );
  };

  const handleHttpError = (syntheticEvent: any) => {
    const { nativeEvent } = syntheticEvent;
    if (nativeEvent.statusCode === 410) {
      setExpired(true);
      Alert.alert(
        'Viewer Expired',
        'This 3D visualization has expired.',
        [{ text: 'OK', onPress: () => navigation.goBack() }]
      );
    }
  };

  return (
    <View style={styles.container}>
      <Appbar.Header>
        <Appbar.BackAction onPress={() => navigation.goBack()} />
        <Appbar.Content title="3D Molecular Viewer" />
        {!expired && timeRemaining && (
          <Text style={styles.timerText}>⏱️ {timeRemaining}</Text>
        )}
      </Appbar.Header>

      {expired ? (
        <Card style={styles.expiredCard}>
          <Card.Content>
            <Text variant="titleLarge" style={styles.expiredTitle}>
              ⏱️ Viewer Expired
            </Text>
            <Text variant="bodyMedium" style={styles.expiredText}>
              This 3D visualization has expired to save storage space.
              Run a new docking job to generate a fresh viewer.
            </Text>
          </Card.Content>
        </Card>
      ) : (
        <>
          {loading && (
            <View style={styles.loadingOverlay}>
              <ActivityIndicator size="large" color="#2196F3" />
              <Text style={styles.loadingText}>Loading 3D viewer...</Text>
            </View>
          )}
          
          <WebView
            source={{ uri: viewerUrl }}
            style={styles.webview}
            onLoadStart={() => setLoading(true)}
            onLoadEnd={() => setLoading(false)}
            onError={handleError}
            onHttpError={handleHttpError}
            javaScriptEnabled={true}
            domStorageEnabled={true}
            startInLoadingState={true}
            scalesPageToFit={true}
            allowsFullscreenVideo={false}
          />
        </>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  webview: {
    flex: 1,
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    zIndex: 10,
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
  },
  timerText: {
    marginRight: 16,
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  expiredCard: {
    margin: 20,
    padding: 20,
  },
  expiredTitle: {
    textAlign: 'center',
    marginBottom: 16,
    color: '#f44336',
  },
  expiredText: {
    textAlign: 'center',
    color: '#666',
  },
});

export default ViewerScreen;
