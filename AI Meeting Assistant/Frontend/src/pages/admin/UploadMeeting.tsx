import { useState, useCallback } from 'react';
import { Upload, FileAudio, X, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/hooks/use-toast';

const UploadMeeting = () => {
  const [files, setFiles] = useState<any[]>([]);
  const { toast } = useToast();
  const API_BASE = "http://localhost:8000";
  //const API_BASE = "https://calescent-interveinous-temeka.ngrok-free.dev/";


  const processFile = async (file: File, fileId: string) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      setFiles(prev => prev.map(f => f.id === fileId ? { ...f, status: 'uploading', progress: 30 } : f));

      const response = await fetch(`${API_BASE}/process-meeting/`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error("Processing failed");

      setFiles(prev => prev.map(f => f.id === fileId ? { ...f, status: 'summarizing', progress: 80 } : f));
      
      const data = await response.json();

      setFiles(prev => prev.map(f => f.id === fileId ? { ...f, status: 'completed', progress: 100, result: data } : f));
      toast({ title: "Success", description: "Meeting transcribed and PDF generated." });

    } catch (error) {
      setFiles(prev => prev.map(f => f.id === fileId ? { ...f, status: 'error' } : f));
      toast({ title: "Error", description: "Backend processing failed", variant: "destructive" });
    }
  };

  const handleFiles = useCallback((fileList: FileList) => {
    const newFiles = Array.from(fileList).map(f => {
      const id = Math.random().toString(36).substr(2, 9);
      processFile(f, id);
      return { id, name: f.name, size: f.size, status: 'uploading', progress: 10 };
    });
    setFiles(prev => [...prev, ...newFiles]);
  }, []);

  return (
    <DashboardLayout requireAdmin>
      <div className="max-w-4xl mx-auto space-y-8">
        
        {/* --- HEADER SECTION FROM IMAGE --- */}
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Upload Meeting</h1>
          <p className="text-base text-slate-500 mt-2">
            Upload audio or video files to transcribe and generate AI summaries
          </p>
        </div>

        {/* --- DROPZONE SECTION FROM IMAGE --- */}
        <Card className="border-none shadow-none bg-white">
          <CardContent className="p-0">
            <div className="relative group transition-all duration-300">
              <input 
                type="file" 
                multiple 
                className="absolute inset-0 opacity-0 cursor-pointer z-10" 
                onChange={(e) => e.target.files && handleFiles(e.target.files)} 
              />
              <div className="flex flex-col items-center justify-center p-20 border-2 border-dashed border-slate-200 rounded-[2.5rem] bg-white group-hover:border-[#2DD4BF] group-hover:bg-[#F0FDFA] transition-all duration-300">
                
                {/* Mint Icon Container */}
                <div className="bg-[#E6FFFA] p-5 rounded-2xl mb-8 group-hover:bg-[#CCFBF1] transition-colors">
                  <Upload className="h-10 w-10 text-[#0D9488]" />
                </div>
                
                <h3 className="text-2xl font-bold text-slate-800 mb-2">
                  Drop your meeting recordings here
                </h3>
                <p className="text-slate-500 text-lg">
                  or <span className="text-[#0D9488] font-medium">click to browse</span> · MP3, WAV, MP4, WebM supported
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* --- PROCESSING QUEUE --- */}
        {files.length > 0 && (
          <Card className="rounded-[2rem] border-slate-100 shadow-sm overflow-hidden">
            <CardHeader className="bg-slate-50/50 border-b border-slate-100">
              <CardTitle className="text-xl">Processing Queue</CardTitle>
            </CardHeader>
            <CardContent className="p-6 space-y-4">
              {files.map((file) => (
                <div key={file.id} className="p-5 border border-slate-100 rounded-2xl space-y-4 bg-white hover:shadow-sm transition-shadow">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-slate-100 rounded-lg">
                        <FileAudio className="h-5 w-5 text-slate-600" />
                      </div>
                      <span className="font-semibold text-slate-700">{file.name}</span>
                    </div>
                    {file.status === 'completed' ? (
                      <div className="bg-teal-50 p-1.5 rounded-full">
                        <CheckCircle className="text-[#0D9488] h-5 w-5" />
                      </div>
                    ) : file.status === 'error' ? (
                      <AlertCircle className="text-red-500 h-5 w-5" />
                    ) : (
                      <Loader2 className="animate-spin h-5 w-5 text-[#2DD4BF]" />
                    )}
                  </div>
                  
                  <div className="space-y-2">
                    <Progress value={file.progress} className="h-2 bg-slate-100 shadow-none" />
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-500 capitalize font-medium">{file.status}...</span>
                      <span className="text-slate-400">{file.progress}%</span>
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
};

export default UploadMeeting;