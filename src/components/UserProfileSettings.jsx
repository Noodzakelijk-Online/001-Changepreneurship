import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useAssessment } from '../contexts/AssessmentContext';
import { 
  User, 
  Settings, 
  Bell, 
  Shield, 
  Download, 
  Trash2,
  Edit3,
  Save,
  X,
  Link,
  Zap,
  Brain,
  Eye,
  EyeOff,
  CheckCircle,
  AlertCircle,
  Clock,
  RefreshCw
} from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import DataConnectionDashboard from './DataConnectionDashboard';
import './UserProfileSettings.css';

const UserProfileSettings = () => {
  const { user, updateUser } = useAuth();
  const { assessmentData } = useAssessment();
  const [activeTab, setActiveTab] = useState('profile');
  const [isEditing, setIsEditing] = useState(false);
  const [profileData, setProfileData] = useState({
    username: user?.username || '',
    email: user?.email || '',
    firstName: user?.firstName || '',
    lastName: user?.lastName || '',
    bio: user?.bio || '',
    timezone: user?.timezone || 'UTC',
    language: user?.language || 'en'
  });
  const [notifications, setNotifications] = useState({
    emailUpdates: true,
    assessmentReminders: true,
    weeklyInsights: true,
    marketingEmails: false
  });
  const [privacy, setPrivacy] = useState({
    profileVisibility: 'private',
    dataSharing: false,
    analyticsTracking: true
  });
  const [connectedAccounts, setConnectedAccounts] = useState({});
  const [integrationInsights, setIntegrationInsights] = useState([]);

  useEffect(() => {
    // Load user settings from API
    loadUserSettings();
    loadConnectedAccounts();
  }, []);

  const loadUserSettings = async () => {
    try {
      // API call to load user settings
      // const settings = await api.getUserSettings();
      // setNotifications(settings.notifications);
      // setPrivacy(settings.privacy);
    } catch (error) {
      console.error('Failed to load user settings:', error);
    }
  };

  const loadConnectedAccounts = async () => {
    try {
      // API call to load connected accounts
      // const accounts = await api.getConnectedAccounts();
      // setConnectedAccounts(accounts);
      
      // Mock data for demo
      setConnectedAccounts({
        gmail: { status: 'connected', lastSync: new Date(), insights: 15 },
        instagram: { status: 'connected', lastSync: new Date(), insights: 8 },
        youtube: { status: 'pending', lastSync: null, insights: 0 }
      });
      
      setIntegrationInsights([
        {
          id: 1,
          type: 'communication_style',
          title: 'Communication Style',
          description: 'Analysis shows you have a direct and analytical communication approach',
          confidence: 92,
          source: 'Gmail',
          appliedToAssessment: true
        },
        {
          id: 2,
          type: 'social_engagement',
          title: 'Social Engagement',
          description: 'Your Instagram activity indicates high visual creativity and social influence',
          confidence: 87,
          source: 'Instagram',
          appliedToAssessment: false
        }
      ]);
    } catch (error) {
      console.error('Failed to load connected accounts:', error);
    }
  };

  const handleProfileSave = async () => {
    try {
      await updateUser(profileData);
      setIsEditing(false);
      // Show success message
    } catch (error) {
      console.error('Failed to update profile:', error);
      // Show error message
    }
  };

  const handleNotificationChange = (key, value) => {
    setNotifications(prev => ({
      ...prev,
      [key]: value
    }));
    // Auto-save notifications
    saveNotificationSettings({ ...notifications, [key]: value });
  };

  const handlePrivacyChange = (key, value) => {
    setPrivacy(prev => ({
      ...prev,
      [key]: value
    }));
    // Auto-save privacy settings
    savePrivacySettings({ ...privacy, [key]: value });
  };

  const saveNotificationSettings = async (settings) => {
    try {
      // API call to save notification settings
      // await api.updateNotificationSettings(settings);
    } catch (error) {
      console.error('Failed to save notification settings:', error);
    }
  };

  const savePrivacySettings = async (settings) => {
    try {
      // API call to save privacy settings
      // await api.updatePrivacySettings(settings);
    } catch (error) {
      console.error('Failed to save privacy settings:', error);
    }
  };

  const exportUserData = async () => {
    try {
      // API call to export user data
      // const data = await api.exportUserData();
      // Download the data as JSON
      const dataStr = JSON.stringify({ user, assessmentData, connectedAccounts }, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `changepreneurship-data-${new Date().toISOString().split('T')[0]}.json`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to export user data:', error);
    }
  };

  const deleteAccount = async () => {
    if (window.confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      try {
        // API call to delete account
        // await api.deleteAccount();
        // Redirect to home page
      } catch (error) {
        console.error('Failed to delete account:', error);
      }
    }
  };

  const getAccountStatusIcon = (status) => {
    switch (status) {
      case 'connected':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'pending':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return null;
    }
  };

  const formatLastSync = (date) => {
    if (!date) return 'Never';
    const now = new Date();
    const diff = now - new Date(date);
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
  };

  return (
    <div className="user-profile-settings">
      <div className="settings-header">
        <div className="header-content">
          <div className="user-avatar">
            <div className="avatar-circle">
              {user?.username?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div className="user-info">
              <h1>{user?.username || 'User'}</h1>
              <p>{user?.email || 'user@example.com'}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="settings-content">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="settings-tabs">
          <TabsList className="tabs-list">
            <TabsTrigger value="profile" className="tab-trigger">
              <User className="w-4 h-4" />
              Profile
            </TabsTrigger>
            <TabsTrigger value="integrations" className="tab-trigger">
              <Link className="w-4 h-4" />
              Integrations
            </TabsTrigger>
            <TabsTrigger value="notifications" className="tab-trigger">
              <Bell className="w-4 h-4" />
              Notifications
            </TabsTrigger>
            <TabsTrigger value="privacy" className="tab-trigger">
              <Shield className="w-4 h-4" />
              Privacy
            </TabsTrigger>
            <TabsTrigger value="data" className="tab-trigger">
              <Download className="w-4 h-4" />
              Data
            </TabsTrigger>
          </TabsList>

          <TabsContent value="profile" className="tab-content">
            <Card>
              <CardHeader>
                <div className="card-header-with-action">
                  <div>
                    <CardTitle>Profile Information</CardTitle>
                    <CardDescription>
                      Update your personal information and preferences
                    </CardDescription>
                  </div>
                  <Button
                    variant={isEditing ? "outline" : "default"}
                    onClick={() => isEditing ? setIsEditing(false) : setIsEditing(true)}
                  >
                    {isEditing ? <X className="w-4 h-4" /> : <Edit3 className="w-4 h-4" />}
                    {isEditing ? 'Cancel' : 'Edit'}
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="profile-form">
                  <div className="form-row">
                    <div className="form-field">
                      <label>Username</label>
                      <input
                        type="text"
                        value={profileData.username}
                        onChange={(e) => setProfileData(prev => ({ ...prev, username: e.target.value }))}
                        disabled={!isEditing}
                        className="form-input"
                      />
                    </div>
                    <div className="form-field">
                      <label>Email</label>
                      <input
                        type="email"
                        value={profileData.email}
                        onChange={(e) => setProfileData(prev => ({ ...prev, email: e.target.value }))}
                        disabled={!isEditing}
                        className="form-input"
                      />
                    </div>
                  </div>

                  <div className="form-row">
                    <div className="form-field">
                      <label>First Name</label>
                      <input
                        type="text"
                        value={profileData.firstName}
                        onChange={(e) => setProfileData(prev => ({ ...prev, firstName: e.target.value }))}
                        disabled={!isEditing}
                        className="form-input"
                      />
                    </div>
                    <div className="form-field">
                      <label>Last Name</label>
                      <input
                        type="text"
                        value={profileData.lastName}
                        onChange={(e) => setProfileData(prev => ({ ...prev, lastName: e.target.value }))}
                        disabled={!isEditing}
                        className="form-input"
                      />
                    </div>
                  </div>

                  <div className="form-field">
                    <label>Bio</label>
                    <textarea
                      value={profileData.bio}
                      onChange={(e) => setProfileData(prev => ({ ...prev, bio: e.target.value }))}
                      disabled={!isEditing}
                      className="form-textarea"
                      rows={3}
                      placeholder="Tell us about yourself..."
                    />
                  </div>

                  <div className="form-row">
                    <div className="form-field">
                      <label>Timezone</label>
                      <select
                        value={profileData.timezone}
                        onChange={(e) => setProfileData(prev => ({ ...prev, timezone: e.target.value }))}
                        disabled={!isEditing}
                        className="form-select"
                      >
                        <option value="UTC">UTC</option>
                        <option value="America/New_York">Eastern Time</option>
                        <option value="America/Chicago">Central Time</option>
                        <option value="America/Denver">Mountain Time</option>
                        <option value="America/Los_Angeles">Pacific Time</option>
                        <option value="Europe/London">London</option>
                        <option value="Europe/Paris">Paris</option>
                        <option value="Asia/Tokyo">Tokyo</option>
                      </select>
                    </div>
                    <div className="form-field">
                      <label>Language</label>
                      <select
                        value={profileData.language}
                        onChange={(e) => setProfileData(prev => ({ ...prev, language: e.target.value }))}
                        disabled={!isEditing}
                        className="form-select"
                      >
                        <option value="en">English</option>
                        <option value="es">Spanish</option>
                        <option value="fr">French</option>
                        <option value="de">German</option>
                        <option value="it">Italian</option>
                        <option value="pt">Portuguese</option>
                      </select>
                    </div>
                  </div>

                  {isEditing && (
                    <div className="form-actions">
                      <Button onClick={handleProfileSave} className="save-button">
                        <Save className="w-4 h-4" />
                        Save Changes
                      </Button>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="integrations" className="tab-content">
            <div className="integrations-content">
              <Card className="integrations-overview">
                <CardHeader>
                  <CardTitle>🔗 Account Integrations</CardTitle>
                  <CardDescription>
                    Connect your digital accounts for hyper-personalized entrepreneurial insights
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="integration-stats">
                    <div className="stat-card">
                      <div className="stat-number">{Object.keys(connectedAccounts).length}</div>
                      <div className="stat-label">Connected Accounts</div>
                    </div>
                    <div className="stat-card">
                      <div className="stat-number">{integrationInsights.length}</div>
                      <div className="stat-label">AI Insights Generated</div>
                    </div>
                    <div className="stat-card">
                      <div className="stat-number">
                        {integrationInsights.filter(i => i.appliedToAssessment).length}
                      </div>
                      <div className="stat-label">Applied to Assessment</div>
                    </div>
                  </div>

                  {Object.keys(connectedAccounts).length > 0 && (
                    <div className="connected-accounts-summary">
                      <h4>Connected Accounts</h4>
                      <div className="accounts-list">
                        {Object.entries(connectedAccounts).map(([platform, data]) => (
                          <div key={platform} className="account-summary">
                            <div className="account-info">
                              <div className="account-name">
                                {getAccountStatusIcon(data.status)}
                                <span>{platform.charAt(0).toUpperCase() + platform.slice(1)}</span>
                              </div>
                              <div className="account-details">
                                <span>Last sync: {formatLastSync(data.lastSync)}</span>
                                <span>{data.insights} insights generated</span>
                              </div>
                            </div>
                            <Button variant="outline" size="sm">
                              <Settings className="w-4 h-4" />
                            </Button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {integrationInsights.length > 0 && (
                    <div className="recent-insights">
                      <h4>Recent AI Insights</h4>
                      <div className="insights-list">
                        {integrationInsights.slice(0, 3).map(insight => (
                          <div key={insight.id} className="insight-summary">
                            <div className="insight-content">
                              <div className="insight-header">
                                <span className="insight-title">{insight.title}</span>
                                <span className="insight-confidence">{insight.confidence}% confident</span>
                              </div>
                              <p className="insight-description">{insight.description}</p>
                              <div className="insight-meta">
                                <span className="insight-source">From {insight.source}</span>
                                {insight.appliedToAssessment && (
                                  <span className="applied-badge">Applied to Assessment</span>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Full Data Connection Dashboard */}
              <DataConnectionDashboard />
            </div>
          </TabsContent>

          <TabsContent value="notifications" className="tab-content">
            <Card>
              <CardHeader>
                <CardTitle>Notification Preferences</CardTitle>
                <CardDescription>
                  Choose how you want to be notified about your progress and updates
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="notification-settings">
                  <div className="setting-item">
                    <div className="setting-info">
                      <h4>Email Updates</h4>
                      <p>Receive important updates about your assessment progress</p>
                    </div>
                    <label className="toggle-switch">
                      <input
                        type="checkbox"
                        checked={notifications.emailUpdates}
                        onChange={(e) => handleNotificationChange('emailUpdates', e.target.checked)}
                      />
                      <span className="toggle-slider"></span>
                    </label>
                  </div>

                  <div className="setting-item">
                    <div className="setting-info">
                      <h4>Assessment Reminders</h4>
                      <p>Get reminded to continue your entrepreneurial assessment</p>
                    </div>
                    <label className="toggle-switch">
                      <input
                        type="checkbox"
                        checked={notifications.assessmentReminders}
                        onChange={(e) => handleNotificationChange('assessmentReminders', e.target.checked)}
                      />
                      <span className="toggle-slider"></span>
                    </label>
                  </div>

                  <div className="setting-item">
                    <div className="setting-info">
                      <h4>Weekly Insights</h4>
                      <p>Receive weekly personalized insights and recommendations</p>
                    </div>
                    <label className="toggle-switch">
                      <input
                        type="checkbox"
                        checked={notifications.weeklyInsights}
                        onChange={(e) => handleNotificationChange('weeklyInsights', e.target.checked)}
                      />
                      <span className="toggle-slider"></span>
                    </label>
                  </div>

                  <div className="setting-item">
                    <div className="setting-info">
                      <h4>Marketing Emails</h4>
                      <p>Receive updates about new features and entrepreneurship tips</p>
                    </div>
                    <label className="toggle-switch">
                      <input
                        type="checkbox"
                        checked={notifications.marketingEmails}
                        onChange={(e) => handleNotificationChange('marketingEmails', e.target.checked)}
                      />
                      <span className="toggle-slider"></span>
                    </label>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="privacy" className="tab-content">
            <Card>
              <CardHeader>
                <CardTitle>Privacy & Security</CardTitle>
                <CardDescription>
                  Control your privacy settings and data sharing preferences
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="privacy-settings">
                  <div className="setting-item">
                    <div className="setting-info">
                      <h4>Profile Visibility</h4>
                      <p>Control who can see your profile information</p>
                    </div>
                    <select
                      value={privacy.profileVisibility}
                      onChange={(e) => handlePrivacyChange('profileVisibility', e.target.value)}
                      className="form-select"
                    >
                      <option value="private">Private</option>
                      <option value="public">Public</option>
                      <option value="friends">Friends Only</option>
                    </select>
                  </div>

                  <div className="setting-item">
                    <div className="setting-info">
                      <h4>Anonymous Data Sharing</h4>
                      <p>Help improve our platform by sharing anonymous usage data</p>
                    </div>
                    <label className="toggle-switch">
                      <input
                        type="checkbox"
                        checked={privacy.dataSharing}
                        onChange={(e) => handlePrivacyChange('dataSharing', e.target.checked)}
                      />
                      <span className="toggle-slider"></span>
                    </label>
                  </div>

                  <div className="setting-item">
                    <div className="setting-info">
                      <h4>Analytics Tracking</h4>
                      <p>Allow us to track your usage to provide better recommendations</p>
                    </div>
                    <label className="toggle-switch">
                      <input
                        type="checkbox"
                        checked={privacy.analyticsTracking}
                        onChange={(e) => handlePrivacyChange('analyticsTracking', e.target.checked)}
                      />
                      <span className="toggle-slider"></span>
                    </label>
                  </div>
                </div>

                <div className="privacy-info">
                  <h4>🛡️ Your Privacy Rights</h4>
                  <ul>
                    <li>✅ Your data is encrypted and secure</li>
                    <li>✅ We never sell your personal information</li>
                    <li>✅ You can export or delete your data anytime</li>
                    <li>✅ We comply with GDPR and CCPA regulations</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="data" className="tab-content">
            <Card>
              <CardHeader>
                <CardTitle>Data Management</CardTitle>
                <CardDescription>
                  Export your data or delete your account
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="data-actions">
                  <div className="action-item">
                    <div className="action-info">
                      <h4>Export Your Data</h4>
                      <p>Download all your assessment data, responses, and insights in JSON format</p>
                    </div>
                    <Button onClick={exportUserData} variant="outline">
                      <Download className="w-4 h-4" />
                      Export Data
                    </Button>
                  </div>

                  <div className="action-item danger">
                    <div className="action-info">
                      <h4>Delete Account</h4>
                      <p>Permanently delete your account and all associated data. This action cannot be undone.</p>
                    </div>
                    <Button onClick={deleteAccount} variant="destructive">
                      <Trash2 className="w-4 h-4" />
                      Delete Account
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default UserProfileSettings;

