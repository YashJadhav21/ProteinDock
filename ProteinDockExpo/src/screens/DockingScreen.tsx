import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { Button, Text, Card, Surface, ActivityIndicator, IconButton } from 'react-native-paper';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useFocusEffect } from '@react-navigation/native';

const DockingScreen = ({ navigation, route }: any) => {
  const [protein, setProtein] = useState<any>(null);
  const [ligand, setLigand] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const { token } = useAuth();

  // Get config from route params if navigating from DockingConfigScreen
  const config = route?.params?.config;

  useFocusEffect(
    React.useCallback(() => {
      loadSelectedData();
    }, [])
  );

  // Handle config submission from DockingConfigScreen
  useEffect(() => {
    if (config) {
      submitDockingWithConfig(config);
    }
  }, [config]);

  const loadSelectedData = async () => {
    try {
      setLoading(true);
      const proteinData = await AsyncStorage.getItem('selectedProtein');
      const ligandData = await AsyncStorage.getItem('selectedLigand');
      
      console.log('Loading docking data...');
      
      if (proteinData) {
        const protein = JSON.parse(proteinData);
        console.log('Loaded protein:', protein._id, protein.pdbId);
        setProtein(protein);
      } else {
        console.log('No protein data in storage');
        setProtein(null);
      }
      
      if (ligandData) {
        const ligand = JSON.parse(ligandData);
        console.log('Loaded ligand:', ligand._id, ligand.name);
        setLigand(ligand);
      } else {
        console.log('No ligand data in storage');
        setLigand(null);
      }
    } catch (error) {
      console.error('Failed to load data:', error);
      Alert.alert('Error', 'Failed to load protein/ligand data. Please select them again.');
    } finally {
      setLoading(false);
    }
  };

  const configureAndSubmit = () => {
    if (!protein || !ligand) {
      Alert.alert('Error', 'Please select both protein and ligand first');
      return;
    }

    if (!protein._id || !ligand._id) {
      Alert.alert(
        'Error', 
        'Protein or ligand is missing database ID. Please re-select them from the Protein/Ligand screens.',
        [
          { text: 'Select Protein', onPress: () => navigation.navigate('Protein') },
          { text: 'Select Ligand', onPress: () => navigation.navigate('Ligand') },
          { text: 'Cancel', style: 'cancel' }
        ]
      );
      return;
    }

    console.log('[Docking] Navigating to config screen with IDs:', {
      proteinId: protein._id,
      ligandId: ligand._id
    });
    navigation.navigate('DockingConfig', {
      proteinId: protein._id,
      ligandId: ligand._id,
      proteinName: `${protein.pdbId} - ${protein.name}`,
      ligandName: ligand.name,
    });
  };

  const submitDockingWithConfig = async (dockingConfig: any) => {
    try {
      console.log('[Docking] Submitting docking job with config:', dockingConfig);
      setSubmitting(true);
      const job = await api.submitDocking(dockingConfig, token);

      console.log('[Docking] Job submitted successfully:', job._id);
      Alert.alert(
        'Success',
        'Docking job submitted! Results will be ready shortly.',
        [
          {
            text: 'View Results',
            onPress: () => navigation.navigate('Results', { jobId: job._id })
          },
          {
            text: 'OK',
            style: 'cancel'
          }
        ]
      );
    } catch (error: any) {
      console.error('[Docking] Submission error:', error);
      Alert.alert('Error', error.message || 'Failed to submit docking job');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Surface style={styles.header} elevation={2}>
        <View style={styles.headerContent}>
          <Text variant="headlineSmall">Run Docking</Text>
          <IconButton
            icon="refresh"
            size={24}
            onPress={loadSelectedData}
            disabled={loading}
          />
        </View>
      </Surface>

      <ScrollView style={styles.content}>
        {!protein || !ligand ? (
          <Card style={styles.warningCard}>
            <Card.Content>
              <Text variant="titleMedium" style={styles.warningTitle}>⚠️ Missing Data</Text>
              <Text variant="bodyMedium" style={styles.warningText}>
                You need to select both a protein and a ligand before running docking.
              </Text>
              {!protein && (
                <Button 
                  mode="outlined" 
                  onPress={() => navigation.navigate('Protein')}
                  style={styles.warningButton}>
                  Select Protein
                </Button>
              )}
              {!ligand && (
                <Button 
                  mode="outlined" 
                  onPress={() => navigation.navigate('Ligand')}
                  style={styles.warningButton}>
                  Design Ligand
                </Button>
              )}
            </Card.Content>
          </Card>
        ) : (
          <>
            <Card style={styles.card}>
              <Card.Content>
                <View style={styles.cardHeader}>
                  <Text variant="titleMedium" style={styles.cardTitle}>Selected Protein</Text>
                  <Button 
                    mode="text" 
                    compact
                    onPress={() => navigation.navigate('Protein')}
                    icon="pencil">
                    Change
                  </Button>
                </View>
                <Text variant="bodyLarge" style={styles.dataText}>{protein.pdbId}</Text>
                <Text variant="bodyMedium" style={styles.dataSubtext}>{protein.name}</Text>
                {protein._id && (
                  <Text variant="bodySmall" style={styles.idText}>ID: {protein._id}</Text>
                )}
              </Card.Content>
            </Card>

            <Card style={styles.card}>
              <Card.Content>
                <View style={styles.cardHeader}>
                  <Text variant="titleMedium" style={styles.cardTitle}>Selected Ligand</Text>
                  <Button 
                    mode="text" 
                    compact
                    onPress={() => navigation.navigate('Ligand')}
                    icon="pencil">
                    Change
                  </Button>
                </View>
                <Text variant="bodyLarge" style={styles.dataText}>{ligand.name}</Text>
                <Text variant="bodySmall" style={styles.dataSubtext}>{ligand.smiles?.substring(0, 50)}...</Text>
                {ligand._id && (
                  <Text variant="bodySmall" style={styles.idText}>ID: {ligand._id}</Text>
                )}
              </Card.Content>
            </Card>

            <Card style={styles.infoCard}>
              <Card.Content>
                <Text variant="titleSmall" style={styles.infoTitle}>SwissDock-Inspired Features</Text>
                <Text variant="bodySmall" style={styles.infoText}>
                  ✓ Configurable search space (grid box){'\n'}
                  ✓ Adjustable exhaustivity (1-64){'\n'}
                  ✓ Multiple binding poses generation{'\n'}
                  ✓ Clustering & interaction analysis
                </Text>
              </Card.Content>
            </Card>

            <Button 
              mode="contained" 
              onPress={configureAndSubmit}
              loading={submitting}
              disabled={submitting}
              style={styles.submitButton}
              icon="cog"
              contentStyle={styles.submitButtonContent}>
              Configure & Run Docking
            </Button>
          </>
        )}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 16,
    backgroundColor: '#fff',
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  card: {
    marginBottom: 16,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  cardTitle: {
    fontWeight: 'bold',
    color: '#666',
  },
  dataText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#6200ee',
    marginBottom: 4,
  },
  dataSubtext: {
    color: '#666',
    marginBottom: 4,
  },
  idText: {
    color: '#999',
    fontSize: 10,
    fontFamily: 'monospace',
  },
  warningCard: {
    backgroundColor: '#fff3cd',
    marginBottom: 16,
  },
  warningTitle: {
    color: '#856404',
    fontWeight: 'bold',
    marginBottom: 8,
  },
  warningText: {
    color: '#856404',
    marginBottom: 12,
  },
  warningButton: {
    marginTop: 8,
  },
  infoCard: {
    backgroundColor: '#e8f5e9',
    marginBottom: 24,
  },
  infoTitle: {
    fontWeight: 'bold',
    marginBottom: 8,
    color: '#2e7d32',
  },
  infoText: {
    color: '#555',
    lineHeight: 20,
  },
  submitButton: {
    paddingVertical: 8,
  },
  submitButtonContent: {
    paddingVertical: 8,
  },
});

export default DockingScreen;
