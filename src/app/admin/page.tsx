'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { getAdminSubmissions, submitLabel, getAdminStats, AdminSubmission, LabelSubmission } from '@/services/api';
import { RoleProtectedRoute } from '@/components/RoleProtectedRoute';
import { 
  UsersIcon, 
  BeakerIcon, 
  ChartBarIcon, 
  ServerIcon,
  PlusIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import * as Dialog from '@radix-ui/react-dialog';
import { Cross2Icon } from '@radix-ui/react-icons';

export default function AdminPage() {
  const { currentUser, loading } = useAuth();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'mlops'>('overview');
  const [users, setUsers] = useState<any[]>([]);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [stats, setStats] = useState<any>(null);
  
  // Professional creation state
  const [profForm, setProfForm] = useState({
    email: '',
    password: '',
    displayName: ''
  });
  const [creatingProf, setCreatingProf] = useState(false);
  const [isCreateProfOpen, setIsCreateProfOpen] = useState(false);

  // Labeling state
  const [submissions, setSubmissions] = useState<AdminSubmission[]>([]);
  const [selectedSubmission, setSelectedSubmission] = useState<AdminSubmission | null>(null);
  const [labelForm, setLabelForm] = useState({
    verifiedSkinType: '',
    verifiedIssues: [] as string[],
    notes: ''
  });
  const [isLoadingSubmissions, setIsLoadingSubmissions] = useState(false);

  const handleCreateProfessional = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreatingProf(true);
    try {
      const { createProfessional } = await import('@/services/api');
      await createProfessional(profForm);
      alert('Professional account created successfully!');
      setProfForm({ email: '', password: '', displayName: '' });
      setIsCreateProfOpen(false);
      loadUsers();
    } catch (error: any) {
      alert('Failed to create professional: ' + (error.response?.data?.error || error.message));
    } finally {
      setCreatingProf(false);
    }
  };

  useEffect(() => {
    if (currentUser) {
      if (activeTab === 'users') {
        loadUsers();
      } else if (activeTab === 'mlops') {
        loadSubmissions();
      } else if (activeTab === 'overview') {
        loadStats();
      }
    }
  }, [currentUser, activeTab]);

  const loadStats = async () => {
    try {
      const data = await getAdminStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats', error);
    }
  };

  const loadUsers = async () => {
    setLoadingUsers(true);
    try {
      const { getAllUsers } = await import('@/services/api');
      const data = await getAllUsers();
      setUsers(data);
    } catch (error) {
      console.error('Failed to load users', error);
    } finally {
      setLoadingUsers(false);
    }
  };

  const handleRoleChange = async (uid: string, newRole: string) => {
      if (!confirm(`Are you sure you want to change this user's role to ${newRole}?`)) return;
      
      try {
          const { updateUserRole } = await import('@/services/api');
          await updateUserRole(uid, newRole);
          loadUsers(); // Refresh list
      } catch (error) {
          alert("Failed to update role");
      }
  };

  const loadSubmissions = async () => {
    setIsLoadingSubmissions(true);
    try {
      const data = await getAdminSubmissions('pending', 50);
      setSubmissions(data);
    } catch (error) {
      console.error('Error loading submissions:', error);
      alert('Failed to load submissions. Make sure you have admin access.');
    } finally {
      setIsLoadingSubmissions(false);
    }
  };

  // ... (keep existing handleSubmitLabel and toggleIssue functions) ...
  const handleSubmitLabel = async () => {
    if (!selectedSubmission) return;

    try {
      const label: LabelSubmission = {
        scanId: selectedSubmission.scanId,
        verifiedSkinType: labelForm.verifiedSkinType,
        verifiedIssues: labelForm.verifiedIssues,
        notes: labelForm.notes
      };

      await submitLabel(label);
      alert('Label submitted successfully!');
      setSelectedSubmission(null);
      setLabelForm({ verifiedSkinType: '', verifiedIssues: [], notes: '' });
      loadSubmissions();
    } catch (error) {
      console.error('Error submitting label:', error);
      alert('Failed to submit label');
    }
  };

  const toggleIssue = (issue: string) => {
    setLabelForm(prev => ({
      ...prev,
      verifiedIssues: prev.verifiedIssues.includes(issue)
        ? prev.verifiedIssues.filter(i => i !== issue)
        : [...prev.verifiedIssues, issue]
    }));
  };

  return (
    <RoleProtectedRoute allowedRoles={['admin']}>
      <div className="flex h-screen bg-slate-50 dark:bg-slate-950">
        {/* Sidebar */}
        <aside className="w-64 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 hidden md:flex flex-col">
          <div className="p-6">
            <h1 className="text-2xl font-bold text-primary">Admin Portal</h1>
            <p className="text-xs text-slate-500 mt-1">System Management</p>
          </div>
          
          <nav className="flex-1 px-4 space-y-2">
            <button
              onClick={() => setActiveTab('overview')}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                activeTab === 'overview' 
                  ? 'bg-primary/10 text-primary font-medium' 
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
              }`}
            >
              <ChartBarIcon className="h-5 w-5" />
              <span>Overview</span>
            </button>
            
            <button
              onClick={() => setActiveTab('users')}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                activeTab === 'users' 
                  ? 'bg-primary/10 text-primary font-medium' 
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
              }`}
            >
              <UsersIcon className="h-5 w-5" />
              <span>User Management</span>
            </button>
            
            <button
              onClick={() => setActiveTab('mlops')}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                activeTab === 'mlops' 
                  ? 'bg-primary/10 text-primary font-medium' 
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
              }`}
            >
              <ServerIcon className="h-5 w-5" />
              <span>ML Ops & Data</span>
            </button>
          </nav>
          
          <div className="p-4 border-t border-slate-200 dark:border-slate-800">
            <div className="flex items-center space-x-3 px-4 py-2">
              <div className="h-2 w-2 rounded-full bg-green-500"></div>
              <span className="text-sm text-slate-600 dark:text-slate-400">System Operational</span>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto p-8">
          {activeTab === 'overview' && (
            <div className="space-y-8">
              <h2 className="text-2xl font-bold">System Overview</h2>
              
              {/* Stats Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="text-sm text-slate-500">Total Users</p>
                      <h3 className="text-3xl font-bold mt-2">{stats?.users?.total || 0}</h3>
                    </div>
                    <div className="p-2 bg-blue-100 text-blue-600 rounded-lg">
                      <UsersIcon className="h-6 w-6" />
                    </div>
                  </div>
                  <p className="text-xs text-slate-500 mt-4">
                    {stats?.users?.professionals || 0} Professionals
                  </p>
                </div>

                <div className="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="text-sm text-slate-500">Total Scans</p>
                      <h3 className="text-3xl font-bold mt-2">{stats?.scans?.total || 0}</h3>
                    </div>
                    <div className="p-2 bg-purple-100 text-purple-600 rounded-lg">
                      <BeakerIcon className="h-6 w-6" />
                    </div>
                  </div>
                  <p className="text-xs text-slate-500 mt-4">
                    {stats?.scans?.labeled || 0} Labeled by Pros
                  </p>
                </div>

                <div className="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="text-sm text-slate-500">Model Version</p>
                      <h3 className="text-xl font-bold mt-2">{stats?.model?.version || 'v1.0.0'}</h3>
                    </div>
                    <div className="p-2 bg-green-100 text-green-600 rounded-lg">
                      <ServerIcon className="h-6 w-6" />
                    </div>
                  </div>
                  <p className="text-xs text-slate-500 mt-4">
                    Accuracy: {(stats?.model?.metrics?.accuracy * 100).toFixed(1)}%
                  </p>
                </div>
                
                <div className="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="text-sm text-slate-500">Data Drift</p>
                      <h3 className="text-xl font-bold mt-2 text-green-600">Stable</h3>
                    </div>
                    <div className="p-2 bg-yellow-100 text-yellow-600 rounded-lg">
                      <ChartBarIcon className="h-6 w-6" />
                    </div>
                  </div>
                  <p className="text-xs text-slate-500 mt-4">
                    Last check: 2 hours ago
                  </p>
                </div>
              </div>

              {/* Model Params */}
              <div className="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 p-6">
                <h3 className="text-lg font-semibold mb-4">Current Model Configuration</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <h4 className="text-sm font-medium text-slate-500 mb-2">Training Params</h4>
                    <ul className="space-y-2 text-sm">
                      <li className="flex justify-between">
                        <span>Epochs:</span>
                        <span className="font-mono">{stats?.model?.params?.epochs || 50}</span>
                      </li>
                      <li className="flex justify-between">
                        <span>Batch Size:</span>
                        <span className="font-mono">{stats?.model?.params?.batch_size || 32}</span>
                      </li>
                      <li className="flex justify-between">
                        <span>Learning Rate:</span>
                        <span className="font-mono">{stats?.model?.params?.learning_rate || 0.001}</span>
                      </li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-slate-500 mb-2">Architecture</h4>
                    <ul className="space-y-2 text-sm">
                      <li className="flex justify-between">
                        <span>Backbone:</span>
                        <span className="font-mono">{stats?.model?.params?.backbone || 'MobileNetV2'}</span>
                      </li>
                      <li className="flex justify-between">
                        <span>Input Size:</span>
                        <span className="font-mono">{stats?.model?.params?.img_size || 224}px</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'users' && (
             <div className="space-y-6">
               <div className="flex justify-between items-center">
                 <h2 className="text-2xl font-bold">User Management</h2>
                 <Dialog.Root open={isCreateProfOpen} onOpenChange={setIsCreateProfOpen}>
                   <Dialog.Trigger asChild>
                     <Button className="flex items-center gap-2">
                       <PlusIcon className="h-4 w-4" />
                       Create Professional
                     </Button>
                   </Dialog.Trigger>
                   <Dialog.Portal>
                     <Dialog.Overlay className="fixed inset-0 bg-black/50 z-50" />
                     <Dialog.Content className="fixed left-[50%] top-[50%] max-h-[85vh] w-[90vw] max-w-[450px] translate-x-[-50%] translate-y-[-50%] rounded-[6px] bg-white dark:bg-slate-900 p-[25px] shadow-[hsl(206_22%_7%_/_35%)_0px_10px_38px_-10px,_hsl(206_22%_7%_/_20%)_0px_10px_20px_-15px] focus:outline-none z-50">
                       <Dialog.Title className="text-lg font-bold mb-4">
                         Create Professional Account
                       </Dialog.Title>
                       <form onSubmit={handleCreateProfessional} className="space-y-4">
                           <div>
                               <label className="block text-sm font-medium mb-1">Display Name</label>
                               <input 
                                   type="text" 
                                   required
                                   className="w-full p-2 border rounded-md dark:bg-slate-800 dark:border-slate-700"
                                   value={profForm.displayName}
                                   onChange={e => setProfForm({...profForm, displayName: e.target.value})}
                               />
                           </div>
                           <div>
                               <label className="block text-sm font-medium mb-1">Email</label>
                               <input 
                                   type="email" 
                                   required
                                   className="w-full p-2 border rounded-md dark:bg-slate-800 dark:border-slate-700"
                                   value={profForm.email}
                                   onChange={e => setProfForm({...profForm, email: e.target.value})}
                               />
                           </div>
                           <div>
                               <label className="block text-sm font-medium mb-1">Password</label>
                               <input 
                                   type="password" 
                                   required
                                   minLength={6}
                                   className="w-full p-2 border rounded-md dark:bg-slate-800 dark:border-slate-700"
                                   value={profForm.password}
                                   onChange={e => setProfForm({...profForm, password: e.target.value})}
                               />
                           </div>
                           <div className="flex justify-end gap-3 mt-6">
                             <Button variant="outline" type="button" onClick={() => setIsCreateProfOpen(false)}>Cancel</Button>
                             <Button type="submit" disabled={creatingProf}>
                                 {creatingProf ? 'Creating...' : 'Create Account'}
                             </Button>
                           </div>
                       </form>
                       <Dialog.Close asChild>
                         <button className="absolute top-[10px] right-[10px] inline-flex h-[25px] w-[25px] appearance-none items-center justify-center rounded-full focus:shadow-[0_0_0_2px] focus:outline-none" aria-label="Close">
                           <Cross2Icon />
                         </button>
                       </Dialog.Close>
                     </Dialog.Content>
                   </Dialog.Portal>
                 </Dialog.Root>
               </div>

               <div className="bg-white dark:bg-slate-900 rounded-xl shadow-md overflow-hidden border border-slate-200 dark:border-slate-800">
                 <div className="overflow-x-auto">
                     <table className="w-full text-left border-collapse">
                         <thead>
                             <tr className="bg-slate-50 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-700">
                                 <th className="p-4 font-semibold text-slate-700 dark:text-slate-300">Email</th>
                                 <th className="p-4 font-semibold text-slate-700 dark:text-slate-300">UID</th>
                                 <th className="p-4 font-semibold text-slate-700 dark:text-slate-300">Role</th>
                                 <th className="p-4 font-semibold text-slate-700 dark:text-slate-300">Joined</th>
                                 <th className="p-4 font-semibold text-slate-700 dark:text-slate-300">Actions</th>
                             </tr>
                         </thead>
                         <tbody>
                             {loadingUsers ? (
                                 <tr><td colSpan={5} className="p-8 text-center text-slate-500">Loading users...</td></tr>
                             ) : users.length === 0 ? (
                                 <tr><td colSpan={5} className="p-8 text-center text-slate-500">No users found</td></tr>
                             ) : (
                                 users.map(user => (
                                     <tr key={user.uid} className="border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50">
                                         <td className="p-4">{user.email}</td>
                                         <td className="p-4 font-mono text-xs text-slate-500">{user.uid.slice(0, 8)}...</td>
                                         <td className="p-4">
                                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                                user.role === 'admin' ? 'bg-purple-100 text-purple-700' :
                                                user.role === 'professional' ? 'bg-blue-100 text-blue-700' :
                                                'bg-slate-100 text-slate-700'
                                            }`}>
                                                {user.role}
                                            </span>
                                         </td>
                                         <td className="p-4 text-sm text-slate-500">
                                             {user.createdAt ? new Date(user.createdAt).toLocaleDateString() : '-'}
                                         </td>
                                         <td className="p-4">
                                             <select 
                                                className="text-sm border rounded px-2 py-1 bg-white dark:bg-slate-800"
                                                value={user.role}
                                                onChange={(e) => handleRoleChange(user.uid, e.target.value)}
                                                disabled={user.email === currentUser?.email} // Prevent changing own role
                                             >
                                                 <option value="user">User</option>
                                                 <option value="professional">Professional</option>
                                                 <option value="admin">Admin</option>
                                             </select>
                                         </td>
                                     </tr>
                                 ))
                             )}
                         </tbody>
                     </table>
                 </div>
             </div>
             </div>
        )}

        {activeTab === 'mlops' && (
            <div className="space-y-8">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold">ML Ops & Data Management</h2>
                <div className="flex gap-2">
                  <Button variant="outline" className="flex items-center gap-2" onClick={() => window.open('http://localhost:5001', '_blank')}>
                    <ChartBarIcon className="h-4 w-4" />
                    Open MLflow
                  </Button>
                  <Button variant="outline" className="flex items-center gap-2">
                    <ArrowPathIcon className="h-4 w-4" />
                    Check Drift
                  </Button>
                  <Button variant="default" className="flex items-center gap-2">
                    <ServerIcon className="h-4 w-4" />
                    Retrain Model
                  </Button>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Submissions List */}
              <div className="bg-white dark:bg-slate-900 rounded-xl shadow-md p-6 border border-slate-200 dark:border-slate-800">
                <h2 className="text-xl font-semibold mb-4">Pending Submissions ({submissions.length})</h2>
                <div className="space-y-3 max-h-[600px] overflow-y-auto">
                  {submissions.map((submission) => (
                    <div
                      key={submission.scanId}
                      onClick={() => setSelectedSubmission(submission)}
                      className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                        selectedSubmission?.scanId === submission.scanId
                          ? 'border-primary bg-primary/10'
                          : 'border-slate-200 dark:border-slate-700 hover:border-primary/50'
                      }`}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <span className="font-medium text-sm">Scan #{submission.scanId.slice(0, 8)}</span>
                        <span className="text-xs text-slate-500">
                          {new Date(submission.timestamp).toLocaleDateString()}
                        </span>
                      </div>
                      <div className="text-sm text-slate-600 dark:text-slate-400">
                        <div>Predicted: {submission.prediction.skinType?.type || 'Unknown'}</div>
                        <div>Issues: {submission.prediction.skinIssues?.length || 0}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Labeling Form */}
              <div className="bg-white dark:bg-slate-900 rounded-xl shadow-md p-6 border border-slate-200 dark:border-slate-800">
                {selectedSubmission ? (
                  <>
                    <h2 className="text-xl font-semibold mb-4">Label Submission</h2>
                    
                    {/* Image Preview */}
                    <div className="mb-6">
                      <div className="w-full aspect-square rounded-lg border-2 border-slate-300 dark:border-slate-700 bg-slate-100 dark:bg-slate-800/50 flex items-center justify-center">
                        <div className="text-center text-slate-400">
                          <p className="text-sm">Image: {selectedSubmission.imagePath}</p>
                          <p className="text-xs mt-2">Image preview not available</p>
                        </div>
                      </div>
                    </div>
                    {/* ... rest of labeling form ... */}
                    {/* AI Prediction */}
                    <div className="mb-6 p-4 bg-slate-100 dark:bg-slate-800/50 rounded-lg">
                      <h3 className="font-medium mb-2">AI Prediction:</h3>
                      <p className="text-sm">
                        <span className="font-medium">Skin Type:</span>{' '}
                        {selectedSubmission.prediction.skinType?.type || 'Unknown'}
                      </p>
                      <p className="text-sm">
                        <span className="font-medium">Issues:</span>{' '}
                        {selectedSubmission.prediction.skinIssues?.map((i: any) => i.name).join(', ') || 'None'}
                      </p>
                    </div>

                    {/* Verified Skin Type */}
                    <div className="mb-4">
                      <label className="block text-sm font-medium mb-2">Verified Skin Type</label>
                      <select
                        value={labelForm.verifiedSkinType}
                        onChange={(e) => setLabelForm({ ...labelForm, verifiedSkinType: e.target.value })}
                        className="w-full p-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800"
                      >
                        <option value="">Select...</option>
                        <option value="Dry">Dry</option>
                        <option value="Oily">Oily</option>
                        <option value="Normal">Normal</option>
                        <option value="Combination">Combination</option>
                      </select>
                    </div>

                    {/* Verified Issues */}
                    <div className="mb-4">
                      <label className="block text-sm font-medium mb-2">Verified Issues</label>
                      <div className="grid grid-cols-2 gap-2">
                        {['Acne', 'Redness', 'Dark Spots', 'Wrinkles', 'Dryness', 'Oiliness'].map((issue) => (
                          <label key={issue} className="flex items-center space-x-2 cursor-pointer">
                            <input
                              type="checkbox"
                              checked={labelForm.verifiedIssues.includes(issue)}
                              onChange={() => toggleIssue(issue)}
                              className="rounded"
                            />
                            <span className="text-sm">{issue}</span>
                          </label>
                        ))}
                      </div>
                    </div>

                    {/* Notes */}
                    <div className="mb-6">
                      <label className="block text-sm font-medium mb-2">Notes</label>
                      <textarea
                        value={labelForm.notes}
                        onChange={(e) => setLabelForm({ ...labelForm, notes: e.target.value })}
                        className="w-full p-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800"
                        rows={3}
                        placeholder="Additional observations..."
                      />
                    </div>

                    <div className="flex space-x-3">
                      <Button onClick={handleSubmitLabel} className="flex-1">
                        Submit Label
                      </Button>
                      <Button
                        onClick={() => {
                          setSelectedSubmission(null);
                          setLabelForm({ verifiedSkinType: '', verifiedIssues: [], notes: '' });
                        }}
                        variant="outline"
                      >
                        Cancel
                      </Button>
                    </div>
                  </>
                ) : (
                  <div className="flex items-center justify-center h-full text-slate-400">
                    <p>Select a submission to label</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
        </main>
      </div>
    </RoleProtectedRoute>
  );
}
