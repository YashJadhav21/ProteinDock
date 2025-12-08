import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { TextInput, Button, Text, Card, Surface, HelperText } from 'react-native-paper';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';
import AsyncStorage from '@react-native-async-storage/async-storage';

const LigandScreen = ({ navigation }: any) => {
  const [mode, setMode] = useState<'smiles' | 'pdb'>('smiles');
  const [name, setName] = useState('');
  const [smiles, setSmiles] = useState('');
  const [pdbContent, setPdbContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [ligand, setLigand] = useState<any>(null);
  const [error, setError] = useState('');
  const { token } = useAuth();

  const createLigand = async () => {
    try {
      setLoading(true);
      setError('');
      
      const payload = mode === 'smiles' 
        ? { name, smiles, formula: '', inputFormat: 'smiles' }
        : { name, pdbFile: pdbContent, formula: '', inputFormat: 'pdb' };
      
      const data = await api.createLigand(payload, token);
      
      if (data.error) {
        setError(data.message || 'Failed to create ligand');
        return;
      }

      // Extract clean data object
      const ligandData = {
        _id: data._id,
        name: data.name,
        smiles: data.smiles,
        formula: data.formula,
        inputFormat: data.inputFormat || 'smiles'
      };

      console.log('Ligand created/found:', ligandData._id, ligandData.name);

      setLigand(ligandData);
      await AsyncStorage.setItem('selectedLigand', JSON.stringify(ligandData));
      setError('');

      if (data.isExisting) {
        Alert.alert('Info', `Using existing ligand: ${data.name}`);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to create ligand');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Surface style={styles.header} elevation={2}>
        <Text variant="headlineSmall">Design Ligand</Text>
      </Surface>

      <ScrollView style={styles.content}>
        <Card style={styles.card}>
          <Card.Content>
            <View style={styles.modeToggle}>
              <Button 
                mode={mode === 'smiles' ? 'contained' : 'outlined'}
                onPress={() => setMode('smiles')}
                style={styles.toggleButton}>
                SMILES
              </Button>
              <Button 
                mode={mode === 'pdb' ? 'contained' : 'outlined'}
                onPress={() => setMode('pdb')}
                style={styles.toggleButton}>
                PDB File
              </Button>
            </View>

            <Text variant="titleMedium" style={styles.cardTitle}>
              {mode === 'smiles' ? 'Enter SMILES' : 'Upload PDB File Content'}
            </Text>
            
            <TextInput
              label="Ligand Name"
              value={name}
              onChangeText={setName}
              mode="outlined"
              style={styles.input}
              placeholder="e.g., Aspirin"
            />

            {mode === 'smiles' ? (
              <TextInput
                label="SMILES String"
                value={smiles}
                onChangeText={setSmiles}
                mode="outlined"
                style={styles.input}
                multiline
                numberOfLines={3}
                placeholder="e.g., CC(=O)Oc1ccccc1C(=O)O"
              />
            ) : (
              <TextInput
                label="Paste PDB File Content"
                value={pdbContent}
                onChangeText={setPdbContent}
                mode="outlined"
                style={styles.input}
                multiline
                numberOfLines={8}
                placeholder="Paste PDB content here (ATOM/HETATM records)"
              />
            )}

            {error ? <Text style={styles.error}>{error}</Text> : null}

            <Button 
              mode="contained" 
              onPress={createLigand}
              loading={loading}
              disabled={loading || !name || (mode === 'smiles' ? !smiles : !pdbContent)}
              style={styles.button}>
              Create Ligand
            </Button>
          </Card.Content>
        </Card>

        {ligand && (
          <Card style={styles.card}>
            <Card.Content>
              <Text variant="titleLarge" style={styles.successTitle}>✓ Ligand Created</Text>
              <Text variant="bodyLarge" style={styles.ligandName}>{ligand.name}</Text>
              <Text variant="bodySmall" style={styles.smilesText}>
                SMILES: {ligand.smiles}
              </Text>
              
              <Button 
                mode="contained" 
                onPress={() => navigation.navigate('Docking')}
                style={styles.nextButton}
                icon="arrow-right">
                Continue to Docking
              </Button>
            </Card.Content>
          </Card>
        )}

        <Card style={styles.infoCard}>
          <Card.Content>
            <Text variant="titleSmall" style={styles.infoTitle}>Example SMILES:</Text>
            <Text variant="bodySmall" style={styles.infoText}>
              • Aspirin: CC(=O)Oc1ccccc1C(=O)O{'\n'}
              • Caffeine: CN1C=NC2=C1C(=O)N(C(=O)N2C)C{'\n'}
              • Ibuprofen: CC(C)Cc1ccc(cc1)C(C)C(=O)O{'\n'}
              • Paracetamol: CC(=O)Nc1ccc(O)cc1{'\n'}
              • Ritonavir (HIV): CC(C)c1nc(cn1C[C@@H](C(=O)NC(Cc2ccccc2)C[C@@H](C(=O)NC(c3ccc(cc3)N4CCCCC4)C(C)(C)C)O)NC(=O)OCc5cncs5)C(C)C
            </Text>
            <HelperText type="info" style={{marginTop: 8}}>
              Tap and hold to copy SMILES strings
            </HelperText>
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
  ligandName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#6200ee',
    marginBottom: 8,
  },
  smilesText: {
    color: '#666',
    fontFamily: 'monospace',
    marginBottom: 8,
  },
  infoCard: {
    backgroundColor: '#fff3e0',
  },
  infoTitle: {
    fontWeight: 'bold',
    marginBottom: 8,
    color: '#f57c00',
  },
  infoText: {
    color: '#555',
    lineHeight: 20,
    fontFamily: 'monospace',
    fontSize: 12,
  },
});

export default LigandScreen;
