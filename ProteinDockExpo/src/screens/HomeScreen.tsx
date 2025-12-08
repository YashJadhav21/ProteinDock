import React, { useEffect, useState } from 'react';
import { View, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { Text, Card, Button, Surface, IconButton } from 'react-native-paper';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';

const HomeScreen = ({ navigation }: any) => {
  const { user, logout, token } = useAuth();
  const [jobs, setJobs] = useState([]);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadJobs();
  }, []);

  const loadJobs = async () => {
    try {
      const data = await api.getJobs(token);
      setJobs(data);
    } catch (error) {
      console.error('Failed to load jobs:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadJobs();
    setRefreshing(false);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return '#4caf50';
      case 'running': return '#ff9800';
      case 'failed': return '#f44336';
      default: return '#2196f3';
    }
  };

  return (
    <View style={styles.container}>
      <Surface style={styles.header} elevation={2}>
        <View>
          <Text variant="headlineSmall">Welcome, {user?.name}!</Text>
          <Text variant="bodySmall" style={styles.subtitle}>{user?.email}</Text>
        </View>
        <IconButton icon="logout" onPress={logout} />
      </Surface>

      <ScrollView 
        style={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
        
        <Text variant="titleLarge" style={styles.sectionTitle}>Quick Actions</Text>
        
        <View style={styles.actionsGrid}>
          <Card style={styles.actionCard} onPress={() => navigation.navigate('Protein')}>
            <Card.Content style={styles.actionContent}>
              <IconButton icon="molecule" size={40} iconColor="#6200ee" />
              <Text variant="titleSmall">Select Protein</Text>
            </Card.Content>
          </Card>

          <Card style={styles.actionCard} onPress={() => navigation.navigate('Ligand')}>
            <Card.Content style={styles.actionContent}>
              <IconButton icon="flask" size={40} iconColor="#6200ee" />
              <Text variant="titleSmall">Design Ligand</Text>
            </Card.Content>
          </Card>

          <Card style={styles.actionCard} onPress={() => navigation.navigate('Docking')}>
            <Card.Content style={styles.actionContent}>
              <IconButton icon="rocket-launch" size={40} iconColor="#6200ee" />
              <Text variant="titleSmall">Run Docking</Text>
            </Card.Content>
          </Card>
        </View>

        <Text variant="titleLarge" style={styles.sectionTitle}>Recent Jobs</Text>
        
        {jobs.length === 0 ? (
          <Card style={styles.emptyCard}>
            <Card.Content>
              <Text style={styles.emptyText}>No docking jobs yet. Start by selecting a protein!</Text>
            </Card.Content>
          </Card>
        ) : (
          jobs.slice(0, 5).map((job: any) => (
            <Card key={job._id} style={styles.jobCard} onPress={() => navigation.navigate('Results', { jobId: job._id })}>
              <Card.Content>
                <View style={styles.jobHeader}>
                  <Text variant="titleMedium">{job.proteinId?.pdbId || 'Unknown'} × {job.ligandId?.name || 'Ligand'}</Text>
                  <View style={[styles.statusBadge, { backgroundColor: getStatusColor(job.status) }]}>
                    <Text style={styles.statusText}>{job.status}</Text>
                  </View>
                </View>
                {job.status === 'completed' && job.results && (
                  <Text variant="bodyMedium" style={styles.affinity}>
                    Binding Affinity: {job.results.bindingAffinity?.toFixed(2)} kcal/mol
                  </Text>
                )}
                <Text variant="bodySmall" style={styles.date}>
                  {new Date(job.createdAt).toLocaleDateString()}
                </Text>
              </Card.Content>
            </Card>
          ))
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
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#fff',
  },
  subtitle: {
    color: '#666',
    marginTop: 4,
  },
  content: {
    flex: 1,
    padding: 16,
  },
  sectionTitle: {
    marginTop: 16,
    marginBottom: 12,
    fontWeight: 'bold',
  },
  actionsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  actionCard: {
    flex: 1,
    marginHorizontal: 4,
  },
  actionContent: {
    alignItems: 'center',
    paddingVertical: 8,
  },
  jobCard: {
    marginBottom: 12,
  },
  jobHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  affinity: {
    color: '#4caf50',
    fontWeight: 'bold',
    marginBottom: 4,
  },
  date: {
    color: '#666',
  },
  emptyCard: {
    padding: 24,
  },
  emptyText: {
    textAlign: 'center',
    color: '#666',
  },
});

export default HomeScreen;
