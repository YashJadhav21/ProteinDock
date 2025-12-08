import React, { useState, useEffect } from 'react';
import { View, ScrollView, StyleSheet, Alert } from 'react-native';
import {
  Text,
  Card,
  Button,
  TextInput,
  SegmentedButtons,
  Switch,
  Divider,
  HelperText,
  ActivityIndicator,
  IconButton,
} from 'react-native-paper';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { api } from '../services/api';

interface DockingConfigScreenProps {
  navigation: any;
  route: any;
}

export default function DockingConfigScreen({ navigation, route }: DockingConfigScreenProps) {
  const { proteinId, ligandId, proteinName, ligandName } = route.params;

  // SwissDock-inspired: Search space (grid box) parameters
  const [gridCenter, setGridCenter] = useState({ x: '0', y: '0', z: '0' });
  const [gridSize, setGridSize] = useState({ x: '20', y: '20', z: '20' });
  const [gridMethod, setGridMethod] = useState<string>('loading...');
  const [loadingGrid, setLoadingGrid] = useState(false);

  // Docking method
  const [method, setMethod] = useState('vina');

  // Parameters
  const [exhaustivity, setExhaustivity] = useState('16');
  const [numPoses, setNumPoses] = useState('9');

  // Advanced options
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Auto-detect grid on mount
  useEffect(() => {
    detectGrid();
  }, []);

  const detectGrid = async () => {
    try {
      setLoadingGrid(true);
      const token = await AsyncStorage.getItem('token');
      const result = await api.getGridSuggestion(proteinId, token);
      
      if (result.gridCenter && result.gridSize) {
        setGridCenter({
          x: result.gridCenter.x.toString(),
          y: result.gridCenter.y.toString(),
          z: result.gridCenter.z.toString(),
        });
        setGridSize({
          x: result.gridSize.x.toString(),
          y: result.gridSize.y.toString(),
          z: result.gridSize.z.toString(),
        });
        setGridMethod(result.message || result.method);
        console.log('[Grid Auto-Detect]', result);
      }
    } catch (error: any) {
      console.error('[Grid Auto-Detect] Error:', error);
      setGridMethod('Using default grid (auto-detect failed)');
    } finally {
      setLoadingGrid(false);
    }
  };

  const handleStartDocking = async () => {
    try {
      const config = {
        proteinId,
        ligandId,
        parameters: {
          gridCenter: {
            x: parseFloat(gridCenter.x) || 0,
            y: parseFloat(gridCenter.y) || 0,
            z: parseFloat(gridCenter.z) || 0,
          },
          gridSize: {
            x: parseFloat(gridSize.x) || 20,
            y: parseFloat(gridSize.y) || 20,
            z: parseFloat(gridSize.z) || 20,
          },
          method,
          exhaustivity: parseInt(exhaustivity) || 8,
          numPoses: parseInt(numPoses) || 9,
        },
      };

      console.log('[DockingConfig] Starting docking with config:', config);

      // Submit docking job using API service
      const token = await AsyncStorage.getItem('token');
      const job = await api.submitDocking(config, token);

      if (job.error || !job._id) {
        throw new Error(job.message || 'Failed to submit docking job');
      }

      console.log('[DockingConfig] Job submitted:', job._id);

      // Navigate to Results screen
      navigation.navigate('Results', { jobId: job._id });
    } catch (error: any) {
      console.error('[DockingConfig] Error:', error);
      Alert.alert('Error', error.message || 'Failed to submit docking job');
    }
  };

  const estimateTime = () => {
    const exh = parseInt(exhaustivity) || 8;
    const poses = parseInt(numPoses) || 9;
    // Simple estimation: ~30 seconds per exhaustivity level
    const minutes = Math.ceil((exh * poses * 30) / 60);
    return minutes;
  };

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <Card style={styles.card}>
        <Card.Content>
          <Text variant="titleLarge">Docking Configuration</Text>
          <Text variant="bodyMedium" style={styles.subtitle}>
            Configure parameters for molecular docking
          </Text>
          <Divider style={styles.divider} />
          <Text variant="bodySmall">
            Protein: {proteinName}
          </Text>
          <Text variant="bodySmall">
            Ligand: {ligandName}
          </Text>
        </Card.Content>
      </Card>

      {/* Docking Method Selection */}
      <Card style={styles.card}>
        <Card.Content>
          <Text variant="titleMedium">1. Select Docking Method</Text>
          <HelperText type="info">
            Choose the algorithm for molecular docking
          </HelperText>
          <SegmentedButtons
            value={method}
            onValueChange={setMethod}
            buttons={[
              { value: 'vina', label: 'AutoDock Vina' },
              { value: 'attracting-cavities', label: 'Attracting Cavities', disabled: true },
            ]}
            style={styles.segment}
          />
        </Card.Content>
      </Card>

      {/* Search Space (Grid Box) */}
      <Card style={styles.card}>
        <Card.Content>
          <View style={styles.sectionHeader}>
            <Text variant="titleMedium">2. Define Search Space</Text>
            <IconButton
              icon="refresh"
              size={20}
              onPress={detectGrid}
              disabled={loadingGrid}
            />
          </View>
          <HelperText type="info">
            {loadingGrid ? 'Detecting optimal grid box...' : gridMethod}
          </HelperText>

          {loadingGrid && (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="small" />
              <Text style={styles.loadingText}>Auto-detecting binding site...</Text>
            </View>
          )}

          <Text variant="labelLarge" style={styles.sectionLabel}>
            Grid Center (Å)
          </Text>
          <View style={styles.row}>
            <TextInput
              label="X"
              value={gridCenter.x}
              onChangeText={(text) => setGridCenter({ ...gridCenter, x: text })}
              keyboardType="numeric"
              mode="outlined"
              dense
              style={styles.input}
            />
            <TextInput
              label="Y"
              value={gridCenter.y}
              onChangeText={(text) => setGridCenter({ ...gridCenter, y: text })}
              keyboardType="numeric"
              mode="outlined"
              dense
              style={styles.input}
            />
            <TextInput
              label="Z"
              value={gridCenter.z}
              onChangeText={(text) => setGridCenter({ ...gridCenter, z: text })}
              keyboardType="numeric"
              mode="outlined"
              dense
              style={styles.input}
            />
          </View>

          <Text variant="labelLarge" style={styles.sectionLabel}>
            Grid Size (Å)
          </Text>
          <View style={styles.row}>
            <TextInput
              label="X"
              value={gridSize.x}
              onChangeText={(text) => setGridSize({ ...gridSize, x: text })}
              keyboardType="numeric"
              mode="outlined"
              dense
              style={styles.input}
            />
            <TextInput
              label="Y"
              value={gridSize.y}
              onChangeText={(text) => setGridSize({ ...gridSize, y: text })}
              keyboardType="numeric"
              mode="outlined"
              dense
              style={styles.input}
            />
            <TextInput
              label="Z"
              value={gridSize.z}
              onChangeText={(text) => setGridSize({ ...gridSize, z: text })}
              keyboardType="numeric"
              mode="outlined"
              dense
              style={styles.input}
            />
          </View>
        </Card.Content>
      </Card>

      {/* Docking Parameters */}
      <Card style={styles.card}>
        <Card.Content>
          <Text variant="titleMedium">3. Set Docking Parameters</Text>
          <HelperText type="info">
            Configure exhaustivity and number of poses
          </HelperText>

          <TextInput
            label="Exhaustivity (1-64)"
            value={exhaustivity}
            onChangeText={setExhaustivity}
            keyboardType="numeric"
            mode="outlined"
            style={styles.fullInput}
          />
          <HelperText type="info">
            Higher values = more thorough search (default: 8)
          </HelperText>

          <TextInput
            label="Number of Poses"
            value={numPoses}
            onChangeText={setNumPoses}
            keyboardType="numeric"
            mode="outlined"
            style={styles.fullInput}
          />
          <HelperText type="info">
            Number of binding modes to generate (default: 9)
          </HelperText>

          {/* Advanced Options Toggle */}
          <View style={styles.switchRow}>
            <Text variant="bodyMedium">Show Advanced Options</Text>
            <Switch value={showAdvanced} onValueChange={setShowAdvanced} />
          </View>

          {showAdvanced && (
            <View style={styles.advanced}>
              <Text variant="bodySmall" style={{ color: '#666' }}>
                Advanced features coming soon:
              </Text>
              <Text variant="bodySmall" style={{ color: '#666' }}>
                • Cavity prioritization
              </Text>
              <Text variant="bodySmall" style={{ color: '#666' }}>
                • Flexible residues selection
              </Text>
              <Text variant="bodySmall" style={{ color: '#666' }}>
                • Energy cutoff settings
              </Text>
            </View>
          )}
        </Card.Content>
      </Card>

      {/* Estimation */}
      <Card style={styles.card}>
        <Card.Content>
          <Text variant="titleMedium">Estimated Calculation Time</Text>
          <Text variant="headlineMedium" style={styles.estimate}>
            ~{estimateTime()} minutes
          </Text>
          <HelperText type="info">
            Actual time may vary based on system complexity
          </HelperText>
        </Card.Content>
      </Card>

      {/* Start Button */}
      <Button
        mode="contained"
        onPress={handleStartDocking}
        style={styles.button}
        icon="rocket-launch"
      >
        Start Docking Job
      </Button>

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  card: {
    margin: 16,
    marginBottom: 8,
  },
  subtitle: {
    marginTop: 8,
    color: '#666',
  },
  divider: {
    marginVertical: 12,
  },
  segment: {
    marginTop: 8,
  },
  sectionLabel: {
    marginTop: 16,
    marginBottom: 8,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#e3f2fd',
    borderRadius: 8,
    marginVertical: 8,
  },
  loadingText: {
    marginLeft: 12,
    color: '#1976d2',
  },
  row: {
    flexDirection: 'row',
    gap: 8,
  },
  input: {
    flex: 1,
  },
  fullInput: {
    marginTop: 8,
  },
  switchRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 16,
  },
  advanced: {
    marginTop: 12,
    padding: 12,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
  },
  estimate: {
    marginTop: 8,
    color: '#2196F3',
    fontWeight: 'bold',
  },
  button: {
    margin: 16,
    marginTop: 8,
  },
});
