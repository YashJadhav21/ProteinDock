import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { 
  Text, 
  Card, 
  ActivityIndicator, 
  Button, 
  Chip,
  ProgressBar,
  DataTable,
  Divider,
  IconButton
} from 'react-native-paper';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';

const ResultsScreen = ({ route, navigation }: any) => {
  const { jobId } = route.params;
  const [job, setJob] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [selectedPose, setSelectedPose] = useState<any>(null);
  const [viewMode, setViewMode] = useState<'all' | 'clusters'>('all');
  const { token } = useAuth();

  useEffect(() => {
    loadJob();
    const interval = setInterval(loadJob, 2000);
    return () => clearInterval(interval);
  }, [jobId]);

  const loadJob = async () => {
    try {
      console.log('[Results] Loading job:', jobId);
      const data = await api.getJob(jobId, token);
      setJob(data);
      
      if (data.status === 'completed' || data.status === 'failed') {
        setLoading(false);
      }
    } catch (error) {
      console.error('[Results] Failed to load job:', error);
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return '#4caf50';
      case 'running': return '#ff9800';
      case 'failed': return '#f44336';
      default: return '#2196f3';
    }
  };

  const getAffinityLevel = (affinity: number) => {
    if (affinity < -9) return '🔥 Excellent';
    if (affinity < -8) return '✨ Very Good';
    if (affinity < -7) return '✓ Good';
    if (affinity < -6) return '~ Moderate';
    return '⚠️ Weak';
  };

  if (loading && !job) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" />
        <Text style={styles.loadingText}>Loading results...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ScrollView style={styles.content}>
        <Card style={styles.card}>
          <Card.Content>
            <View style={styles.statusContainer}>
              <Text variant="titleMedium">Job Status</Text>
              <Chip 
                icon={job?.status === 'completed' ? 'check-circle' : 'clock'}
                style={[styles.statusChip, { backgroundColor: getStatusColor(job?.status) }]}
                textStyle={{ color: 'white' }}
              >
                {job?.status?.toUpperCase()}
              </Chip>
            </View>
            
            {job?.progress !== undefined && job?.status === 'running' && (
              <View style={styles.progressContainer}>
                <Text variant="bodySmall">Progress: {job.progress}%</Text>
                <ProgressBar progress={job.progress / 100} style={styles.progressBar} />
              </View>
            )}
          </Card.Content>
        </Card>

        {(job?.status === 'running' || job?.status === 'pending') && (
          <Card style={styles.card}>
            <Card.Content>
              <ActivityIndicator size="large" style={styles.spinner} />
              <Text variant="bodyLarge" style={styles.processingText}>
                Processing molecular docking...
              </Text>
            </Card.Content>
          </Card>
        )}

        {job?.status === 'completed' && job?.results && (
          <>
            <Card style={styles.card}>
              <Card.Content>
                <Text variant="titleLarge">Best Binding Affinity</Text>
                <Text variant="displayMedium" style={styles.affinityValue}>
                  {job.results.bindingAffinity?.toFixed(2)} kcal/mol
                </Text>
                <Chip icon="trophy" style={styles.levelChip}>
                  {getAffinityLevel(job.results.bindingAffinity)}
                </Chip>
                
                {job.results.viewer && job.results.viewer.urlPath ? (
                  <Button
                    mode="contained"
                    icon="cube-outline"
                    style={styles.viewerButton}
                    onPress={() => {
                      const viewerUrl = `https://proteindock.onrender.com${job.results.viewer.urlPath}`;
                      navigation.navigate('Viewer', {
                        viewerUrl,
                        expiresAt: job.results.viewer.expiresAt
                      });
                    }}
                  >
                    🔬 Open 3D Molecular Viewer
                  </Button>
                ) : (
                  <Text variant="bodySmall" style={styles.viewerNote}>
                    ℹ️ 3D viewer not available for this job. Run a new docking to enable interactive visualization.
                  </Text>
                )}
              </Card.Content>
            </Card>

            {job.results.clusters && job.results.clusters.length > 0 && (
              <Card style={styles.card}>
                <Card.Content>
                  <Text variant="titleMedium">Binding Mode Clusters</Text>
                  <Divider style={styles.divider} />
                  
                  {job.results.clusters.map((cluster: any) => (
                    <View key={cluster.clusterId} style={styles.clusterRow}>
                      <Chip icon="molecule" mode="outlined">
                        Cluster {cluster.clusterId + 1}
                      </Chip>
                      <View style={styles.clusterInfo}>
                        <Text variant="bodySmall">
                          {cluster.memberCount} poses - Best: {cluster.bestScore?.toFixed(2)} kcal/mol
                        </Text>
                      </View>
                    </View>
                  ))}
                </Card.Content>
              </Card>
            )}

            <Card style={styles.card}>
              <Card.Content>
                <Text variant="titleMedium">Binding Poses ({job.results.poses?.length || 0})</Text>
                <DataTable>
                  <DataTable.Header>
                    <DataTable.Title>Pose</DataTable.Title>
                    <DataTable.Title>Cluster</DataTable.Title>
                    <DataTable.Title numeric>Score</DataTable.Title>
                  </DataTable.Header>

                  {job.results.poses?.slice(0, 10).map((pose: any) => (
                    <DataTable.Row
                      key={pose.poseId}
                      onPress={() => setSelectedPose(pose.poseId === selectedPose?.poseId ? null : pose)}
                    >
                      <DataTable.Cell>{pose.poseId}</DataTable.Cell>
                      <DataTable.Cell>{pose.clusterId + 1}</DataTable.Cell>
                      <DataTable.Cell numeric>{pose.score?.toFixed(2)}</DataTable.Cell>
                    </DataTable.Row>
                  ))}
                </DataTable>
              </Card.Content>
            </Card>

            {job.results.interactions && (
              <Card style={styles.card}>
                <Card.Content>
                  <Text variant="titleMedium">Molecular Interactions</Text>
                  <Divider style={styles.divider} />
                  
                  <View style={styles.interactionStats}>
                    <View style={styles.statItem}>
                      <Chip icon="water" mode="outlined" style={styles.statChip}>
                        H-Bonds
                      </Chip>
                      <Text variant="titleMedium" style={styles.statValue}>
                        {Array.isArray(job.results.interactions.hBonds) 
                          ? job.results.interactions.hBonds.length 
                          : (job.results.interactions.hBonds || 0)}
                      </Text>
                    </View>
                    
                    <View style={styles.statItem}>
                      <Chip icon="molecule" mode="outlined" style={styles.statChip}>
                        Hydrophobic
                      </Chip>
                      <Text variant="titleMedium" style={styles.statValue}>
                        {Array.isArray(job.results.interactions.hydrophobic) 
                          ? job.results.interactions.hydrophobic.length 
                          : (job.results.interactions.hydrophobic || 0)}
                      </Text>
                    </View>
                    
                    <View style={styles.statItem}>
                      <Chip icon="hexagon-multiple" mode="outlined" style={styles.statChip}>
                        π-Stacking
                      </Chip>
                      <Text variant="titleMedium" style={styles.statValue}>
                        {Array.isArray(job.results.interactions.piStacking) 
                          ? job.results.interactions.piStacking.length 
                          : (job.results.interactions.piStacking || 0)}
                      </Text>
                    </View>
                    
                    <View style={styles.statItem}>
                      <Chip icon="flash" mode="outlined" style={styles.statChip}>
                        Ionic
                      </Chip>
                      <Text variant="titleMedium" style={styles.statValue}>
                        {Array.isArray(job.results.interactions.ionic) 
                          ? job.results.interactions.ionic.length 
                          : (job.results.interactions.ionic || 0)}
                      </Text>
                    </View>
                  </View>
                  
                  {job.results.interactions.summary && typeof job.results.interactions.summary === 'object' && (
                    <Text variant="bodyMedium" style={styles.interactionSummary}>
                      Total: {job.results.interactions.summary.totalInteractions || 0} interactions across {job.results.interactions.summary.interactingResidues || 0} residues
                    </Text>
                  )}
                  {job.results.interactions.summary && typeof job.results.interactions.summary === 'string' && (
                    <Text variant="bodyMedium" style={styles.interactionSummary}>
                      {job.results.interactions.summary}
                    </Text>
                  )}
                </Card.Content>
              </Card>
            )}
            
            {selectedPose && selectedPose.interactions && (
              <Card style={styles.card}>
                <Card.Content>
                  <Text variant="titleMedium">Pose {selectedPose.poseId} - Interactions</Text>
                  
                  {selectedPose.interactions.hBonds?.length > 0 && (
                    <View style={styles.interactionSection}>
                      <Chip icon="water" mode="outlined">
                        Hydrogen Bonds ({selectedPose.interactions.hBonds.length})
                      </Chip>
                      {selectedPose.interactions.hBonds.map((bond: any, idx: number) => (
                        <Text key={idx} variant="bodySmall" style={styles.interactionText}>
                          • {bond.residue} - {bond.distance.toFixed(2)} Å
                        </Text>
                      ))}
                    </View>
                  )}
                </Card.Content>
              </Card>
            )}
          </>
        )}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  content: { flex: 1, padding: 16 },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  loadingText: { marginTop: 16 },
  card: { marginBottom: 16 },
  statusContainer: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  statusChip: { paddingHorizontal: 8 },
  progressContainer: { marginTop: 16 },
  progressBar: { height: 8, borderRadius: 4, marginTop: 8 },
  spinner: { marginVertical: 16 },
  processingText: { textAlign: 'center' },
  affinityValue: { color: '#2196F3', fontWeight: 'bold', textAlign: 'center', marginVertical: 8 },
  levelChip: { alignSelf: 'center', marginVertical: 8 },
  viewerButton: { marginTop: 16 },
  viewerNote: { marginTop: 16, textAlign: 'center', color: '#666', fontStyle: 'italic' },
  divider: { marginVertical: 12 },
  clusterRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 12 },
  clusterInfo: { marginLeft: 12 },
  interactionStats: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-around', marginTop: 8 },
  statItem: { alignItems: 'center', marginBottom: 12, minWidth: '40%' },
  statChip: { marginBottom: 4 },
  statValue: { fontWeight: 'bold', color: '#2196F3' },
  interactionSummary: { marginTop: 12, fontStyle: 'italic', color: '#666' },
  interactionSection: { marginTop: 12 },
  interactionText: { marginLeft: 12, marginTop: 4 },
});

export default ResultsScreen;
