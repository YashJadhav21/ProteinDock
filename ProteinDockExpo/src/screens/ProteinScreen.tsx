import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { TextInput, Button, Text, Card, Surface, ActivityIndicator } from 'react-native-paper';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';
import AsyncStorage from '@react-native-async-storage/async-storage';

const ProteinScreen = ({ navigation }: any) => {
  const [mode, setMode] = useState<'fetch' | 'upload'>('fetch');
  const [pdbId, setPdbId] = useState('');
  const [pdbName, setPdbName] = useState('');
  const [pdbContent, setPdbContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [protein, setProtein] = useState<any>(null);
  const [error, setError] = useState('');
  const { token } = useAuth();

  const fetchProtein = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await api.fetchProtein(pdbId, token);
      
      if (data.error || data.message?.includes('Failed')) {
        setError(data.message || 'Failed to fetch protein');
        return;
      }

      // Extract clean data object
      const proteinData = {
        _id: data._id,
        pdbId: data.pdbId,
        name: data.name,
        organism: data.organism,
        structure: data.structure
      };

      console.log('Protein fetched:', proteinData._id, proteinData.pdbId);
      
      setProtein(proteinData);
      await AsyncStorage.setItem('selectedProtein', JSON.stringify(proteinData));
      setError('');

      if (data.isExisting) {
        Alert.alert('Info', `Using existing protein: ${data.pdbId}`);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch protein');
    } finally {
      setLoading(false);
    }
  };

  const uploadProtein = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await api.uploadProtein({
        pdbId: pdbName.toUpperCase() || 'CUSTOM',
        name: pdbName || 'Custom Protein',
        structure: pdbContent
      }, token);
      
      if (data.error || data.message?.includes('Failed')) {
        setError(data.message || 'Failed to upload protein');
        return;
      }

      const proteinData = {
        _id: data._id,
        pdbId: data.pdbId,
        name: data.name,
        organism: data.organism,
        structure: data.structure
      };

      console.log('Protein uploaded:', proteinData._id, proteinData.pdbId);
      
      setProtein(proteinData);
      await AsyncStorage.setItem('selectedProtein', JSON.stringify(proteinData));
      setError('');

      if (data.isExisting) {
        Alert.alert('Info', `Using existing protein: ${data.pdbId}`);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to upload protein');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Surface style={styles.header} elevation={2}>
        <Text variant="headlineSmall">Select Protein</Text>
      </Surface>

      <ScrollView style={styles.content}>
        <Card style={styles.card}>
          <Card.Content>
            <View style={styles.modeToggle}>
              <Button 
                mode={mode === 'fetch' ? 'contained' : 'outlined'}
                onPress={() => setMode('fetch')}
                style={styles.toggleButton}>
                Fetch from PDB
              </Button>
              <Button 
                mode={mode === 'upload' ? 'contained' : 'outlined'}
                onPress={() => setMode('upload')}
                style={styles.toggleButton}>
                Upload PDB File
              </Button>
            </View>

            {mode === 'fetch' ? (
              <>
                <Text variant="titleMedium" style={styles.cardTitle}>Fetch from RCSB PDB</Text>
                
                <TextInput
                  label="PDB ID (e.g., 1ABC)"
                  value={pdbId}
                  onChangeText={setPdbId}
                  mode="outlined"
                  autoCapitalize="characters"
                  style={styles.input}
                  maxLength={4}
                />

                {error ? <Text style={styles.error}>{error}</Text> : null}

                <Button 
                  mode="contained" 
                  onPress={fetchProtein}
                  loading={loading}
                  disabled={loading || pdbId.length !== 4}
                  style={styles.button}>
                  Fetch Protein
                </Button>
              </>
            ) : (
              <>
                <Text variant="titleMedium" style={styles.cardTitle}>Upload PDB File Content</Text>
                
                <TextInput
                  label="Protein Name"
                  value={pdbName}
                  onChangeText={setPdbName}
                  mode="outlined"
                  style={styles.input}
                  placeholder="e.g., My Protein"
                />

                <TextInput
                  label="Paste PDB File Content"
                  value={pdbContent}
                  onChangeText={setPdbContent}
                  mode="outlined"
                  multiline
                  numberOfLines={10}
                  style={styles.input}
                  placeholder="Paste PDB content here (starting with HEADER, ATOM, etc.)"
                />

                {error ? <Text style={styles.error}>{error}</Text> : null}

                <Button 
                  mode="contained" 
                  onPress={uploadProtein}
                  loading={loading}
                  disabled={loading || !pdbName || !pdbContent}
                  style={styles.button}>
                  Upload Protein
                </Button>
              </>
            )}
          </Card.Content>
        </Card>

        {protein && (
          <Card style={styles.card}>
            <Card.Content>
              <Text variant="titleLarge" style={styles.successTitle}>✓ Protein Loaded</Text>
              <Text variant="bodyLarge" style={styles.proteinId}>{protein.pdbId}</Text>
              <Text variant="bodyMedium" style={styles.proteinInfo}>
                Name: {protein.name}
              </Text>
              {protein.organism && (
                <Text variant="bodySmall" style={styles.proteinInfo}>
                  Organism: {protein.organism}
                </Text>
              )}
              <Text variant="bodySmall" style={styles.proteinInfo}>
                Structure loaded: {protein.structure?.length || 0} bytes
              </Text>
              
              <Button 
                mode="contained" 
                onPress={() => navigation.navigate('Ligand')}
                style={styles.nextButton}
                icon="arrow-right">
                Continue to Ligand Design
              </Button>
            </Card.Content>
          </Card>
        )}

        <Card style={styles.infoCard}>
          <Card.Content>
            <Text variant="titleSmall" style={styles.infoTitle}>Popular PDB IDs to try:</Text>
            <Text variant="bodySmall" style={styles.infoText}>
              • 1HSG - HIV-1 Protease{'\n'}
              • 3CLN - SARS-CoV Main Protease{'\n'}
              • 1XDN - Insulin{'\n'}
              • 1A28 - Hemoglobin
            </Text>
          </Card.Content>
        </Card>
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
  content: {
    flex: 1,
    padding: 16,
  },
  card: {
    marginBottom: 16,
  },
  cardTitle: {
    marginBottom: 16,
    fontWeight: 'bold',
  },
  input: {
    marginBottom: 16,
  },
  button: {
    marginTop: 8,
  },
  modeToggle: {
    flexDirection: 'row',
    marginBottom: 16,
    gap: 8,
  },
  toggleButton: {
    flex: 1,
  },
  nextButton: {
    marginTop: 16,
  },
  error: {
    color: 'red',
    marginBottom: 8,
  },
  successTitle: {
    color: '#4caf50',
    fontWeight: 'bold',
    marginBottom: 8,
  },
  proteinId: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#6200ee',
    marginBottom: 12,
  },
  proteinInfo: {
    marginBottom: 6,
    color: '#666',
  },
  infoCard: {
    backgroundColor: '#e3f2fd',
  },
  infoTitle: {
    fontWeight: 'bold',
    marginBottom: 8,
    color: '#1976d2',
  },
  infoText: {
    color: '#555',
    lineHeight: 20,
  },
});

export default ProteinScreen;
