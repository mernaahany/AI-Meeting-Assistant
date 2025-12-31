import { useEffect, useState } from 'react';
import { FileAudio, Users, Clock, Calendar, Loader2, ChevronRight } from 'lucide-react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { format } from 'date-fns';

interface DashboardData {
  totalMeetings: number;
  voiceProfiles: number;
  hoursSaved: number;
  recentMeetings: Array<{
    id: string;
    title: string;
    status: string;
    date: number; // Unix timestamp from Python os.path.getmtime
  }>;
}

const AdminDashboard = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

// 'http://localhost:8000/dashboard-stats'

  // Fetch real stats from the local file-system via FastAPI
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch('http://localhost:8000/dashboard-stats');
        if (!response.ok) throw new Error('Failed to fetch stats');
        const json = await response.json();
        setData(json);
      } catch (error) {
        console.error("Error loading dashboard data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const statsConfig = [
    {
      title: 'Total Meetings',
      value: data?.totalMeetings ?? '0',
      label: 'Files in Test Dir',
      icon: FileAudio,
      color: 'text-primary',
      bgColor: 'bg-accent',
    },
    {
      title: 'Voice Profiles',
      value: data?.voiceProfiles ?? '0',
      label: 'Enrolled Speakers',
      icon: Users,
      color: 'text-success',
      bgColor: 'bg-success/10',
    },
    {
      title: 'Hours Saved',
      value: data?.hoursSaved ?? '0',
      label: 'Manual work avoided',
      icon: Clock,
      color: 'text-primary',
      bgColor: 'bg-primary/10',
    },
  ];

  if (loading) {
    return (
      <DashboardLayout requireAdmin>
        <div className="flex h-[60vh] items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout requireAdmin>
      <div className="space-y-8">
        {/* Header Section */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Admin Dashboard</h1>
            <p className="text-base text-muted-foreground mt-1">
              Live insights from your local processing folders
            </p>
          </div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground bg-white px-4 py-2 rounded-xl shadow-sm border border-slate-100">
            <Calendar className="h-4 w-4 text-primary" />
            <span className="font-medium">{format(new Date(), 'EEEE, MMMM d, yyyy')}</span>
          </div>
        </div>

        {/* Stats Grid - 3 Columns */}
        <div className="grid gap-6 md:grid-cols-3">
          {statsConfig.map((stat) => (
            <Card key={stat.title} className="relative overflow-hidden border-slate-100 shadow-sm transition-hover hover:shadow-md">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">{stat.title}</p>
                    <p className="mt-2 text-3xl font-bold text-foreground">{stat.value}</p>
                    <p className="mt-1 text-xs text-muted-foreground italic font-medium">
                      {stat.label}
                    </p>
                  </div>
                  <div className={`rounded-2xl p-4 ${stat.bgColor}`}>
                    <stat.icon className={`h-6 w-6 ${stat.color}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Recent Meetings List */}
        <div className="grid gap-6 lg:grid-cols-1">
          <Card className="rounded-[2rem] border-slate-100 shadow-sm overflow-hidden">
            <CardHeader className="flex flex-row items-center justify-between bg-slate-50/50 border-b border-slate-100 px-8 py-6">
              <div>
                <CardTitle className="text-lg font-semibold">Processed Files (Latest)</CardTitle>
                <p className="text-sm text-muted-foreground">Recent meeting data from local storage</p>
              </div>
              <span className="bg-white border border-slate-200 text-slate-600 px-3 py-1 rounded-full text-xs font-semibold">
                {data?.recentMeetings?.length || 0} files found
              </span>
            </CardHeader>
            <CardContent className="p-4 space-y-2">
              {data?.recentMeetings && data.recentMeetings.length > 0 ? (
                data.recentMeetings.map((meeting) => (
                  <div
                    key={meeting.id}
                    className="group flex items-center gap-4 rounded-2xl p-4 hover:bg-slate-50 transition-all cursor-default border border-transparent hover:border-slate-100"
                  >
                    <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-teal-50 text-teal-600 group-hover:bg-teal-600 group-hover:text-white transition-colors">
                      <FileAudio className="h-6 w-6" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-slate-800 truncate">{meeting.title}</p>
                      <p className="text-sm text-slate-500">
                        {format(new Date(meeting.date * 1000), 'MMM d, yyyy · h:mm a')}
                      </p>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="inline-flex items-center rounded-full px-3 py-1 text-xs font-bold bg-teal-50 text-teal-700">
                        {meeting.status}
                      </span>
                      <ChevronRight className="h-5 w-5 text-slate-300 group-hover:text-slate-500 transition-colors" />
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-12">
                  <div className="bg-slate-50 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                    <FileAudio className="h-8 w-8 text-slate-300" />
                  </div>
                  <p className="text-slate-500 font-medium">No meetings found in storage</p>
                  <p className="text-xs text-slate-400 mt-1">Files in processed_audio_test will appear here</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default AdminDashboard;