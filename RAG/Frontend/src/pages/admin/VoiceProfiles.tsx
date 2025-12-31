import { useState, useRef, useEffect } from 'react';
import { Mic, Plus, Upload, Trash2, CheckCircle, Loader2, AlertTriangle } from 'lucide-react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
  DialogDescription
} from '@/components/ui/dialog';
import { VoiceProfile } from '@/types/meeting';
import { useToast } from '@/hooks/use-toast';

const VoiceProfiles = () => {
  const [profiles, setProfiles] = useState<VoiceProfile[]>([]);
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [profileToDelete, setProfileToDelete] = useState<{id: string, name: string} | null>(null);
  const [loading, setLoading] = useState(true);
  
  const [newProfile, setNewProfile] = useState({ name: '', department: '' });
  const [uploadingId, setUploadingId] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const API_BASE = "http://localhost:8000";
  //const API_BASE = "https://calescent-interveinous-temeka.ngrok-free.dev/";



  // --- 1. Load existing profiles from Backend (Includes Department from JSON) ---
  useEffect(() => {
    const fetchExistingProfiles = async () => {
      try {
        const response = await fetch(`${API_BASE}/list-speakers`);
        if (response.ok) {
          const data = await response.json();
          setProfiles(data);
        }
      } catch (error) {
        console.error("Failed to sync with backend:", error);
        toast({ title: 'Sync Error', description: 'Could not load profiles', variant: 'destructive' });
      } finally {
        setLoading(false);
      }
    };
    fetchExistingProfiles();
  }, [toast]);

  // --- 2. Add Profile (Local state, preserves department for the upload step) ---
  const handleAddProfile = () => {
    if (!newProfile.name || !newProfile.department) return;
    const profile: VoiceProfile = {
      id: `v${Date.now()}`, 
      name: newProfile.name,
      department: newProfile.department,
      status: 'pending',
    };
    setProfiles(prev => [...prev, profile]);
    setNewProfile({ name: '', department: '' });
    setIsAddDialogOpen(false);
  };

  // --- 3. Upload & Process Audio (Sends Name + Department) ---
  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !uploadingId) return;

    const targetProfile = profiles.find(p => p.id === uploadingId);
    if (!targetProfile) return;

    setProfiles(prev => prev.map(p => p.id === uploadingId ? { ...p, status: 'processing' } : p));

    const formData = new FormData();
    formData.append('file', file);
    formData.append('speaker_name', targetProfile.name);
    // NEW: Pass the department so the backend can save it in the .json file
    formData.append('department', targetProfile.department);

    try {
      const response = await fetch(`${API_BASE}/enroll-speaker/`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Enrollment failed");
      }

      setProfiles(prev => prev.map(p => 
        p.id === uploadingId ? { ...p, status: 'trained' } : p
      ));
      
      toast({ 
        title: 'Profile Trained', 
        description: `Enrolled ${data.speaker} in ${targetProfile.department}` 
      });

    } catch (error: any) {
      console.error("Upload error:", error);
      setProfiles(prev => prev.map(p => p.id === uploadingId ? { ...p, status: 'pending' } : p));
      toast({ title: 'Error', description: error.message, variant: 'destructive' });
    } finally {
      setUploadingId(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  // --- 4. Delete Profile ---
  const confirmDelete = async () => {
    if (!profileToDelete) return;

    try {
      const response = await fetch(`${API_BASE}/delete-speaker/${encodeURIComponent(profileToDelete.name)}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Delete failed");
      }

      setProfiles(prev => prev.filter(p => p.id !== profileToDelete.id));
      toast({ title: 'Profile Removed', description: `Deleted ${profileToDelete.name}` });
    } catch (error: any) {
      toast({ title: 'Delete Failed', description: error.message, variant: 'destructive' });
    } finally {
      setIsDeleteDialogOpen(false);
      setProfileToDelete(null);
    }
  };

  return (
    <DashboardLayout requireAdmin>
      <div className="max-w-4xl mx-auto space-y-8">
        
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 font-tight">Voice Profiles</h1>
            <p className="text-base text-slate-500 mt-1">
              Train the system to recognize team members by their voice
            </p>
          </div>
          
          <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
            <DialogTrigger asChild>
              <Button className="bg-[#2DD4BF] hover:bg-[#26b9a7] text-white px-6 py-5 rounded-2xl text-base font-medium shadow-sm transition-all">
                <Plus className="h-5 w-5 mr-2" /> Add Profile
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create Voice Profile</DialogTitle>
                <DialogDescription>Enter the details of the team member you want to enroll.</DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Full Name</Label>
                  <Input id="name" placeholder="John Doe" value={newProfile.name} onChange={(e) => setNewProfile({...newProfile, name: e.target.value})} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="dept">Department</Label>
                  <Input id="dept" placeholder="Engineering" value={newProfile.department} onChange={(e) => setNewProfile({...newProfile, department: e.target.value})} />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>Cancel</Button>
                <Button className="bg-[#2DD4BF] hover:bg-[#26b9a7]" onClick={handleAddProfile}>Create Profile</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>

        <div className="bg-[#F0FDFA] border border-[#CCFBF1] rounded-[2rem] p-8 flex gap-6 items-center">
          <div className="bg-[#CCFBF1] p-4 rounded-2xl">
            <Mic className="h-8 w-8 text-[#0D9488]" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-slate-800">How Voice Profiles Work</h3>
            <p className="text-slate-500 text-base leading-relaxed mt-1">
              The AI standardizes audio, reduces background noise, and creates a unique voice embedding linked to the member's department.
            </p>
          </div>
        </div>

        <input type="file" ref={fileInputRef} className="hidden" accept="audio/*" onChange={handleFileSelect} />

        <div className="grid gap-4 md:grid-cols-2">
          {loading ? (
            <div className="col-span-full py-12 flex justify-center">
               <Loader2 className="animate-spin h-8 w-8 text-teal-500" />
            </div>
          ) : profiles.length === 0 ? (
            <div className="col-span-full py-12 text-center border-2 border-dashed rounded-3xl text-slate-400">
              No voice profiles created yet.
            </div>
          ) : (
            profiles.map((profile) => (
              <Card key={profile.id} className="rounded-2xl border-slate-100 shadow-sm group transition-all hover:shadow-md">
                <CardContent className="p-6">
                  <div className="flex justify-between items-start">
                    <div className="space-y-1">
                      <h3 className="font-semibold text-lg text-slate-800">{profile.name}</h3>
                      <p className="text-sm text-slate-500">{profile.department}</p>
                      
                      <div className="mt-4 flex gap-2">
                        {profile.status === 'pending' && (
                          <Button 
                            variant="outline" 
                            size="sm" 
                            className="rounded-xl border-slate-200 text-teal-600 hover:bg-teal-50"
                            onClick={() => { setUploadingId(profile.id); fileInputRef.current?.click(); }}
                          >
                            <Upload className="h-4 w-4 mr-2" /> Upload Sample
                          </Button>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      {profile.status === 'processing' ? (
                        <div className="flex items-center gap-2 px-3 py-1 bg-amber-50 rounded-full">
                          <Loader2 className="animate-spin h-4 w-4 text-amber-500" />
                          <span className="text-xs font-medium text-amber-600">Processing...</span>
                        </div>
                      ) : profile.status === 'trained' ? (
                        <div className="flex items-center gap-2 px-3 py-1 bg-teal-50 rounded-full">
                          <CheckCircle className="h-4 w-4 text-teal-600" />
                          <span className="text-xs font-medium text-teal-600">Trained</span>
                        </div>
                      ) : null}

                      <Button
                        variant="ghost"
                        size="icon"
                        className="text-slate-300 hover:text-red-500 hover:bg-red-50 rounded-full"
                        onClick={() => {
                          setProfileToDelete({id: profile.id, name: profile.name});
                          setIsDeleteDialogOpen(true);
                        }}
                      >
                        <Trash2 className="h-5 w-5" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </div>

      <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <div className="mx-auto w-12 h-12 rounded-full bg-red-100 flex items-center justify-center mb-4">
              <AlertTriangle className="h-6 w-6 text-red-600" />
            </div>
            <DialogTitle className="text-center">Delete Voice Profile?</DialogTitle>
            <DialogDescription className="text-center">
              Delete <strong>{profileToDelete?.name}</strong>? This removes their audio and metadata permanently.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="flex flex-row gap-2 sm:justify-center mt-4">
            <Button variant="outline" className="flex-1" onClick={() => setIsDeleteDialogOpen(false)}>Cancel</Button>
            <Button variant="destructive" className="flex-1" onClick={confirmDelete}>Delete</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  );
};

export default VoiceProfiles;